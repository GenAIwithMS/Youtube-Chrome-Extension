const API_BASE_URL = 'http://localhost:8000';

let currentVideoId = '';
let isProcessed = false;
let isProcessing = false;

// DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusBar = document.getElementById('statusBar');
const loading = document.getElementById('loading');

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await initializeExtension();
  setupEventListeners();
});

async function initializeExtension() {
  try {
    // Get current tab URL to extract video ID
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab.url && tab.url.includes('youtube.com/watch')) {
      const url = new URL(tab.url);
      const videoId = url.searchParams.get('v');
      
      if (videoId) {
        currentVideoId = videoId;
        updateStatus(`Detected video: ${videoId}`, 'info');
        
        // Check if video is already processed
        await checkVideoStatus(videoId);
        
        // Load stored messages for this video
        await loadStoredMessages(videoId);
      } else {
        updateStatus('No video ID found in URL', 'error');
      }
    } else {
      updateStatus('Please navigate to a YouTube video', 'info');
    }
  } catch (error) {
    console.error('Error initializing extension:', error);
    updateStatus('Error initializing extension', 'error');
  }
}

async function checkVideoStatus(videoId) {
  try {
    // Check if video was already processed by calling the backend
    const response = await fetch(`${API_BASE_URL}/videos`);
    if (response.ok) {
      const data = await response.json();
      const processedVideo = data.processed_videos.find(v => v.video_id === videoId);
      
      if (processedVideo) {
        isProcessed = true;
        updateStatus('Video processed - Ready to chat!', 'processing');
        enableChat();
      } else {
        // Auto-process the video
        await processCurrentVideo();
      }
    } else {
      // If backend is not available, try to process
      await processCurrentVideo();
    }
  } catch (error) {
    console.error('Error checking video status:', error);
    updateStatus('Backend not available. Please start the server.', 'error');
  }
}

async function processCurrentVideo() {
  if (!currentVideoId || isProcessing) return;
  
  isProcessing = true;
  updateStatus('Processing video...', 'processing');
  
  try {
    const response = await fetch(`${API_BASE_URL}/process_video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_id: currentVideoId }),
    });
    
    if (response.ok) {
      const data = await response.json();
      isProcessed = true;
      
      // Add system message
      addMessage('system', data.message);
      
      updateStatus('Video processed - Ready to chat!', 'processing');
      enableChat();
      
      // Store processing status
      await chrome.storage.local.set({ 
        [`processed_${currentVideoId}`]: true,
        [`messages_${currentVideoId}`]: await getStoredMessages(currentVideoId)
      });
      
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to process video');
    }
  } catch (error) {
    console.error('Error processing video:', error);
    addMessage('error', `Error: ${error.message}`);
    updateStatus('Processing failed. Check if backend is running.', 'error');
  } finally {
    isProcessing = false;
  }
}

async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message || !isProcessed || !currentVideoId) return;
  
  // Add user message
  addMessage('user', message);
  messageInput.value = '';
  
  // Show loading
  showLoading(true);
  disableInput();
  
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: currentVideoId,
        query: message
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const formatted_data = marked.parse(data.response)
      addMessage('assistant', formatted_data);
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get response');
    }
  } catch (error) {
    console.error('Error sending message:', error);
    addMessage('error', `Error: ${error.message}`);
  } finally {
    showLoading(false);
    enableInput();
    
    // Store updated messages
    if (currentVideoId) {
      await chrome.storage.local.set({
        [`messages_${currentVideoId}`]: await getStoredMessages(currentVideoId)
      });
    }
  }
}

function addMessage(type, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.innerHTML = content;
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function loadStoredMessages(videoId) {
  try {
    const stored = await chrome.storage.local.get([`messages_${videoId}`]);
    const messages = stored[`messages_${videoId}`] || [];
    
    // Clear existing messages except welcome
    const welcomeMessage = messagesContainer.querySelector('.message.welcome');
    messagesContainer.innerHTML = '';
    if (welcomeMessage) {
      messagesContainer.appendChild(welcomeMessage);
    }
    
    // Add stored messages
    messages.forEach(msg => {
      if (msg.type && msg.content) {
        addMessage(msg.type, msg.content);
      }
    });
  } catch (error) {
    console.error('Error loading stored messages:', error);
  }
}

async function getStoredMessages(videoId) {
  const messages = [];
  const messageElements = messagesContainer.querySelectorAll('.message:not(.welcome)');
  
  messageElements.forEach(element => {
    const type = element.className.replace('message ', '');
    const content = element.textContent;
    messages.push({ type, content });
  });
  
  return messages;
}

function setupEventListeners() {
  // Send button click
  sendButton.addEventListener('click', sendMessage);
  
  // Enter key to send message
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  
  // Auto-resize textarea
  messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 80) + 'px';
  });
}

function updateStatus(message, type = 'info') {
  statusBar.textContent = message;
  statusBar.className = `status-bar ${type}`;
}

function enableChat() {
  messageInput.disabled = false;
  sendButton.disabled = false;
  messageInput.placeholder = 'Ask about the video...';
}

function disableInput() {
  messageInput.disabled = true;
  sendButton.disabled = true;
}

function enableInput() {
  if (isProcessed) {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
  }
}

function showLoading(show) {
  if (show) {
    loading.classList.add('show');
  } else {
    loading.classList.remove('show');
  }
}

