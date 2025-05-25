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
      
      const chatBox = document.getElementById('chat-box');
      const msgElem = document.createElement('div');
      msgElem.classList.add('message', 'success-message');
      msgElem.innerHTML = '✅ Login successful! You can now proceed.';
      chatBox.appendChild(msgElem);
      chatBox.scrollTop = chatBox.scrollHeight;
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

// Make the chat popup draggable
function makeDraggable(element, handle) {
  let initialX, initialY, initialLeft, initialTop;
  
  handle.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    
    // Get initial positions
    initialX = e.clientX;
    initialY = e.clientY;
    
    // If not already absolute, convert to absolute positioning
    if (element.style.position !== 'absolute') {
      const rect = element.getBoundingClientRect();
      element.style.top = rect.top + 'px';
      element.style.left = rect.left + 'px';
      element.style.bottom = 'auto';
      element.style.right = 'auto';
      element.style.position = 'absolute';
    }
    
    initialLeft = parseInt(element.style.left) || 0;
    initialTop = parseInt(element.style.top) || 0;
    
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    
    // Calculate the new position directly
    const dx = e.clientX - initialX;
    const dy = e.clientY - initialY;
    
    element.style.left = (initialLeft + dx) + "px";
    element.style.top = (initialTop + dy) + "px";
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

// Make the chat popup resizable
function makeResizable(element) {
  const resizers = element.querySelectorAll('.resizer');
  const minimum_size = 300;
  let original_width = 0;
  let original_height = 0;
  let original_x = 0;
  let original_y = 0;
  let original_mouse_x = 0;
  let original_mouse_y = 0;

  for (let i = 0; i < resizers.length; i++) {
    const currentResizer = resizers[i];
    currentResizer.addEventListener('mousedown', function(e) {
      e.preventDefault();
      
      // If not already absolute, convert to absolute positioning
      if (element.style.position !== 'absolute') {
        const rect = element.getBoundingClientRect();
        element.style.top = rect.top + 'px';
        element.style.left = rect.left + 'px';
        element.style.bottom = 'auto';
        element.style.right = 'auto';
        element.style.position = 'absolute';
      }
      
      original_width = parseFloat(getComputedStyle(element).getPropertyValue('width').replace('px', ''));
      original_height = parseFloat(getComputedStyle(element).getPropertyValue('height').replace('px', ''));
      original_x = element.getBoundingClientRect().left;
      original_y = element.getBoundingClientRect().top;
      original_mouse_x = e.pageX;
      original_mouse_y = e.pageY;
      
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResize);
    });
    
    function resize(e) {
      if (currentResizer.classList.contains('resizer-right') || 
          currentResizer.classList.contains('resizer-both')) {
        const width = original_width + (e.pageX - original_mouse_x);
        if (width > minimum_size) {
          element.style.width = width + 'px';
        }
      }
      
      if (currentResizer.classList.contains('resizer-bottom') || 
          currentResizer.classList.contains('resizer-both')) {
        const height = original_height + (e.pageY - original_mouse_y);
        if (height > minimum_size) {
          element.style.height = height + 'px';
        }
      }
      
      if (currentResizer.classList.contains('resizer-left')) {
        const width = original_width - (e.pageX - original_mouse_x);
        if (width > minimum_size) {
          element.style.width = width + 'px';
          element.style.left = original_x + (e.pageX - original_mouse_x) + 'px';
        }
      }
      
      if (currentResizer.classList.contains('resizer-top')) {
        const height = original_height - (e.pageY - original_mouse_y);
        if (height > minimum_size) {
          element.style.height = height + 'px';
          element.style.top = original_y + (e.pageY - original_mouse_y) + 'px';
        }
      }
    }
    
    function stopResize() {
      window.removeEventListener('mousemove', resize);
    }
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
  
  // Make the chat popup draggable by its header
  const chatPopup = document.getElementById('chat-popup');
  const chatHeader = document.querySelector('.chat-header');
  makeDraggable(chatPopup, chatHeader);
  
  // Make the chat popup resizable
  makeResizable(chatPopup);
});
