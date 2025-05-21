let isAuthenticated = false;

function toggleChat() {
  const chatPopup = document.getElementById("chat-popup");
  chatPopup.style.display = (chatPopup.style.display === "flex") ? "none" : "flex";
}

function appendMessage(sender, msg) {
  const chatBox = document.getElementById("chat-box");
  const message = document.createElement("p");
  message.innerHTML = `<strong>${sender}:</strong> ${msg}`;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("message");
  const message = input.value;
  if (!message.trim()) return;
  input.value = "";

  appendMessage("You", message);

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  });

  const data = await res.json();
  appendMessage("Bot", data.reply);

  if (data.reply.toLowerCase().includes("please login")) {
    document.getElementById("login-modal").style.display = "flex";
  }
}

async function submitLogin() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (data.status === "success") {
    isAuthenticated = true;
    document.getElementById("login-modal").style.display = "none";
    appendMessage("System", "✅ Login successful! You can now proceed.");
  } else {
    appendMessage("System", "❌ Login failed. Try again.");
  }
}
