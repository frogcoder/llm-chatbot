let accessToken = null;

// Toggle the visibility of the chat popup
function toggleChat() {
  const chatPopup = document.getElementById('chat-popup');
  chatPopup.classList.toggle('hidden');
  
  // If we're opening the chat and not logged in, show login modal
  if (!chatPopup.classList.contains('hidden') && !accessToken) {
    document.getElementById('login-modal').classList.remove('hidden');
  }
}

// Append a message to the chat box
function appendMessage(sender, message) {
  const chatBox = document.getElementById('chat-box');
  const msgElem = document.createElement('div');
  
  if (sender === 'You') {
    msgElem.classList.add('message', 'user-message');
    msgElem.innerHTML = `${message}`;
  } else if (sender === 'Bot') {
    msgElem.classList.add('message', 'bot-message');
    msgElem.innerHTML = `${message}`;
  } else {
    msgElem.classList.add('message', 'system-message');
    msgElem.innerHTML = `${message}`;
  }
  
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

// Show typing indicator
function showTypingIndicator() {
  const chatBox = document.getElementById('chat-box');
  const indicator = document.createElement('div');
  indicator.classList.add('typing-indicator');
  indicator.id = 'typing-indicator';
  indicator.innerHTML = '<span></span><span></span><span></span>';
  chatBox.appendChild(indicator);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) {
    indicator.remove();
  }
}

// Send a chat message to the backend
async function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  appendMessage('You', message);

  // We should already be logged in at this point
  if (!accessToken) {
    appendMessage('System', '🔒 Session expired. Please login again.');
    document.getElementById('login-modal').classList.remove('hidden');
    return;
  }

  try {
    // Show typing indicator
    showTypingIndicator();
    
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ message })
    });
    
    // Remove typing indicator
    removeTypingIndicator();
    
    const data = await res.json();
    appendMessage('Bot', data.reply);
  } catch (err) {
    // Remove typing indicator
    removeTypingIndicator();
    
    console.error('Chat error:', err);
    appendMessage('System', '⚠️ Could not send message.');
  }
}

// Hook up event listeners once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('login-button').addEventListener('click', submitLogin);
  document.getElementById('send-button').addEventListener('click', sendMessage);
  document.getElementById('chat-toggle').addEventListener('click', toggleChat);
  
  // Add event listener for Enter key in the message input
  document.getElementById('message').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });
  
  // Add event listeners for Enter key in login inputs
  document.getElementById('username').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      document.getElementById('password').focus();
    }
  });
  
  document.getElementById('password').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      submitLogin();
    }
  });
});
