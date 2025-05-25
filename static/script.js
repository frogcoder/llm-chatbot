let accessToken = null;

// Toggle the visibility of the chat popup
function toggleChat() {
  const chatPopup = document.getElementById('chat-popup');
  chatPopup.classList.toggle('hidden');
}

// Append a message to the chat box
function appendMessage(sender, message) {
  const chatBox = document.getElementById('chat-box');
  const msgElem = document.createElement('div');
  msgElem.classList.add('message');
  msgElem.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(msgElem);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Handle user login submission
async function submitLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (res.ok && data.status === 'success') {
      accessToken = data.access_token;
      document.getElementById('login-modal').classList.add('hidden');
      appendMessage('System', '✅ Login successful! You can now proceed.');
    } else {
      appendMessage('System', '❌ Login failed. Try again.');
    }
  } catch (err) {
    console.error('Login error:', err);
    appendMessage('System', '⚠️ An error occurred. Please try again.');
  }
}

// Send a chat message to the backend
async function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  appendMessage('You', message);

  if (!accessToken) {
    appendMessage('System', '🔒 Please login to continue.');
    document.getElementById('login-modal').classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    appendMessage('Bot', data.reply);
  } catch (err) {
    console.error('Chat error:', err);
    appendMessage('System', '⚠️ Could not send message.');
  }
}

// Hook up event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('login-button').addEventListener('click', submitLogin);
  document.getElementById('send-button').addEventListener('click', sendMessage);
  document.getElementById('chat-toggle').addEventListener('click', toggleChat);
});
