
# 💬 Grp7 Digital Banking Bot

A web-based chatbot assistant that supports FAQ handling, intent detection, and secure banking actions (like deposit/withdraw) after authentication.

---

## 🧩 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **LLM Integration**: Gemini API (planned)
- **Authentication**: Username/Password (dummy login)
- **Intent Detection**: Currently keyword-based, to be replaced with LLM or classifier

---

## 📁 Project Structure

```
chatbot_project/
│
├── app.py                      # Flask backend server
├── /templates
│   └── chat.html               # Chat UI with floating button and login modal
│
├── /static
│   ├── style.css               # Styling for chatbot and landing page
│   └── script.js               # JS for chat interaction and login popup
│
└── README.md                   # Project info and team guidance
```

---

## ✅ Features

- Chatbot UI accessible via floating 🤖 button
- Chat popup with message history and smart scroll
- Login modal triggered **only when required** (e.g., for banking actions)
- Dummy authentication: `username=admin`, `password=123`
- Intent-aware chatbot backend (to be powered by Gemini)

---

## 🧠 API Endpoints Used by Frontend

| Endpoint   | Method | Description                          |
|------------|--------|--------------------------------------|
| `/chat`    | POST   | Handles user input, returns bot reply and intent |
| `/auth`    | POST   | Authenticates user (dummy logic for now) |

### Chat Request Format:
```json
{ "message": "I want to deposit money" }
```

### Chat Response Expected:
```json
{
  "reply": "Please login to continue.",
  "intent": "deposit"
}
```

### Auth Request Format:
```json
{ "username": "admin", "password": "123" }
```

---

## 👨‍💻 Backend Team – Integration Guide

### 🔹 Replace Dummy Intent Detection

In `app.py`:

```python
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    # 🔽 Replace this with Gemini intent classifier
    if "deposit" in user_input:
        return jsonify({"reply": "Please login to continue.", "intent": "deposit"})
```

> 🔁 Return both `reply` and `intent`

### 🔹 Plug in Gemini API

Use the Gemini API to:
- Detect user intent
- Generate a context-aware reply

Then return both values to the frontend.

---

## 🧪 Running the App Locally

### 1. Install Flask (once)
```bash
pip install flask
```

### 2. Start the server
```bash
python app.py
```

### 3. Visit the app
Open  browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🙋 Front-End Contact: Bikash  
Handles HTML, CSS, JS, and integration layout.  
