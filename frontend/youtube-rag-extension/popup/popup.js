// ----------------- START: PASTE THIS INTO POPUP.JS -----------------

const API_BASE_URL = 'http://localhost:8000';

let currentVideoId = '';
let isProcessed = false;
let isProcessing = false;

// DOM elements
const messagesContainer = document.getElementById('messages' );
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusBar = document.getElementById('statusBar');
const loading = document.getElementById('loading');

// Initialize popup when the HTML is fully loaded
document.addEventListener('DOMContentLoaded', async () => {
  await initializeExtension();
  setupEventListeners();
});

// Main function to start the extension
async function initializeExtension() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab && tab.url && tab.url.includes('youtube.com/watch')) {
      const url = new URL(tab.url);
      const videoId = url.searchParams.get('v');
      
      if (videoId) {
        currentVideoId = videoId;
        updateStatus(`Detected video: ${videoId}`, 'info');
        await checkVideoStatus(videoId);
        await loadStoredMessages(videoId);
      } else {
        updateStatus('No video ID found in URL.', 'error');
      }
    } else {
      updateStatus('Please navigate to a YouTube video page.', 'info');
    }
  } catch (error) {
    console.error('Error initializing extension:', error);
    updateStatus('Error initializing. Is the backend running?', 'error');
  }
}

// Checks if the video is already processed or needs processing
async function checkVideoStatus(videoId) {
  try {
    const response = await fetch(`${API_BASE_URL}/videos`);
    if (!response.ok) {
      // This happens if the backend is down
      throw new Error('Backend server is not responding.');
    }
    
    const data = await response.json();
    const isAlreadyProcessed = data.processed_videos.some(v => v.video_id === videoId);
    
    if (isAlreadyProcessed) {
      console.log("Video already processed.");
      isProcessed = true;
      updateStatus('Video ready. Ask me anything!', 'processing');
      enableChat();
    } else {
      console.log("Video not processed yet. Starting processing...");
      // If not processed, start the processing automatically
      await processCurrentVideo();
    }
  } catch (error) {
    console.error('Error checking video status:', error);
    updateStatus(error.message, 'error');
    disableChat();
  }
}

// Sends the request to the backend to process the video transcript
async function processCurrentVideo() {
  if (!currentVideoId || isProcessing) return;
  
  isProcessing = true;
  updateStatus('Processing video...', 'processing');
  disableChat();
  
  try {
    const response = await fetch(`${API_BASE_URL}/process_video`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: currentVideoId }),
    });
    
    if (response.ok) {
      const data = await response.json();
      isProcessed = true;
    //   addMessage('system', data.message);
      updateStatus('Processing complete. Ready to chat!', 'processing');
      enableChat();
      await chrome.storage.local.set({ [`processed_${currentVideoId}`]: true });
    } else {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to process video');
    }
  } catch (error) {
    console.error('Error processing video:', error);
    addMessage('error', `Error: ${error.message}`);
    updateStatus('Processing failed. Please check backend.', 'error');
  } finally {
    isProcessing = false;
  }
}

// Sends a user's chat message to the backend
async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message || !isProcessed || !currentVideoId) return;
  
  addMessage('user', message);
  messageInput.value = '';
  showLoading(true);
  disableChat();
  
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: currentVideoId, query: message }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const formatted_data = marked.parse(data.response);
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
    enableChat();
    await storeCurrentMessages(currentVideoId);
  }
}

// --- Helper Functions ---

function setupEventListeners() {
  sendButton.addEventListener('click', sendMessage);
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 80)}px`;
  });
}

function addMessage(type, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.innerHTML = content;
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  return messageDiv; 
}

async function loadStoredMessages(videoId) {
  try {
    const key = `messages_${videoId}`;
    const result = await chrome.storage.local.get([key]);
    const messages = result[key] || [];
    
    const welcomeMessage = messagesContainer.querySelector('.message.welcome');
    messagesContainer.innerHTML = '';
    if (welcomeMessage) {
      messagesContainer.appendChild(welcomeMessage);
    }
    
    messages.forEach(msg => {
      if (msg.type && msg.content) {
        addMessage(msg.type, msg.content);
      }
    });
  } catch (error) {
    console.error('Error loading stored messages:', error);
  }
}

async function storeCurrentMessages(videoId) {
  const messages = [];
  messagesContainer.querySelectorAll('.message:not(.welcome)').forEach(el => {
    messages.push({
      type: el.className.replace('message ', ''),
      content: el.innerHTML // Use innerHTML to save formatting
    });
  });
  const key = `messages_${videoId}`;
  await chrome.storage.local.set({ [key]: messages });
}

function updateStatus(message, type = 'info') {
  statusBar.textContent = message;
  statusBar.className = `status-bar ${type}`;
}

function enableChat() {
  if (isProcessed) {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = 'Ask about the video...';
  }
}

function disableChat() {
  messageInput.disabled = true;
  sendButton.disabled = true;
}

function showLoading(show) {
  loading.style.display = show ? 'flex' : 'none';
}

// ----------------- END: PASTE THIS INTO POPUP.JS -----------------
