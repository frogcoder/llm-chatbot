import os, threading, asyncio, json
from flask import Flask, render_template, request, jsonify, abort
import jwt
from datetime import datetime, timedelta
from chatbot.database import auth_user, init_db
from chatbot.mcp.client_sse import InteractiveBankingAssistant

# Initialize Flask app pointing to local templates/ and static/
app = Flask(__name__, template_folder="templates", static_folder="static")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Instantiate & initialize the agent at startup
assistant = InteractiveBankingAssistant()

# Spin up a dedicated loop in a background thread
background_loop = asyncio.new_event_loop()
def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(assistant.initialize_session())
    loop.run_forever()

t = threading.Thread(target=_start_background_loop, args=(background_loop,), daemon=True)
t.start()

# Helpers for JWT
def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if not user:
            abort(401, "Invalid token payload")
        return user
    except jwt.ExpiredSignatureError:
        abort(401, "Token has expired")
    except jwt.InvalidTokenError:
        abort(401, "Invalid token")

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("chat.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, 'Missing "username" or "password"')

    # Validate against real database
    if not auth_user(username, password):
        return jsonify({"status": "fail"}), 401

    token = create_access_token(username)
    return jsonify({"status": "success", "access_token": token, "token_type": "bearer"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    # 3) auth as before…
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"reply": "🔒 Please login to continue."}), 401
    token = auth_header.split(" ", 1)[1]
    user = verify_access_token(token)

    # 4) Grab the incoming message
    msg = request.json.get("message", "").strip()
    if not msg:
        return jsonify({"reply": "💡 I didn’t get any text."}), 400

    # 5) Schedule your send_message onto the background loop
    future = asyncio.run_coroutine_threadsafe(
        assistant.send_message(msg),
        background_loop
    )
    try:
        result = future.result(timeout=30)   # wait up to 30s
    except Exception as e:
        return jsonify({"reply": f"❌ Internal error: {e}"}), 500

    # 6) Handle the two possible return types
    #    - A string → that’s your model’s reply
    #    - A dict/list → that’s raw tool output, so jsonify it or summarize
    if isinstance(result, str):
        return jsonify({"reply": result})

    # If it’s a dict with an "error" key, bubble that up:
    if isinstance(result, dict) and "error" in result:
        return jsonify({"reply": result["error"]})

    # Otherwise, just stringify the payload
    return jsonify({"reply": json.dumps(result, indent=2)})

if __name__ == "__main__":
    init_db()
    # Turn off the reloader
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
