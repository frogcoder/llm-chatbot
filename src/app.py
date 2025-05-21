from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    # Dummy logic for demo
    if "deposit" in user_input or "withdraw" in user_input:
        return jsonify({"reply": "Please login to continue."})
    return jsonify({"reply": f"You said: {user_input}"})

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    if data["username"] == "admin" and data["password"] == "123":
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"})

if __name__ == "__main__":
    app.run(debug=True)
