import os
from flask import Flask, render_template, request, jsonify, abort
import jwt
from datetime import datetime, timedelta
from chatbot.database import auth_user, init_db

# Initialize Flask app pointing to local templates/ and static/
app = Flask(__name__, template_folder="templates", static_folder="static")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


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
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"reply": "🔒 Please login to continue."}), 401
    token = auth_header.split(" ", 1)[1]
    user = verify_access_token(token)

    msg = request.json.get("message", "")
    if "transfer" in msg.lower():
        return jsonify({"reply": f"🔄 Transfer flow would run here for {user}."})
    if "faq" in msg.lower():
        return jsonify({"reply": "Here’s an FAQ answer stub."})
    return jsonify({"reply": "You are being transferred to a human agent."})

if __name__ == "__main__":
    init_db()  # Ensure database is initialized
    app.run(host="0.0.0.0", port=5000, debug=True)