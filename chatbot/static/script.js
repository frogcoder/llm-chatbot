let accessToken = null;

async function submitLogin() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok && data.status === "success") {
    accessToken = data.access_token;
    document.getElementById("login-modal").style.display = "none";
    appendMessage("System", "✅ Login successful! You can now proceed.");
  } else {
    appendMessage("System", "❌ Login failed. Try again.");
  }
}

async function sendMessage() {
  const input = document.getElementById("message");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  appendMessage("You", message);

  if (!accessToken) {
    appendMessage("System", "🔒 Please login to continue.");
    document.getElementById("login-modal").style.display = "flex";
    return;
  }

  const res = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${accessToken}`
    },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  appendMessage("Bot", data.reply);
}