// YouTube AI Music Agent - Content Script
// Injects command interface into YouTube pages

console.log('🎵 YouTube AI Music Agent loaded!');

// Wait for YouTube to fully load
function waitForYouTube() {
  return new Promise((resolve) => {
    const checkYouTube = setInterval(() => {
      if (document.querySelector('ytd-app')) {
        clearInterval(checkYouTube);
        resolve();
      }
    }, 500);
  });
}

// Create the command interface
function createCommandBox() {
  // Check if already exists
  if (document.getElementById('yt-ai-agent')) {
    return;
  }

  const container = document.createElement('div');
  container.id = 'yt-ai-agent';
  container.innerHTML = `
    <div class="yt-ai-header">
      <span class="yt-ai-title">🎵 AI Music Agent</span>
      <button class="yt-ai-toggle" id="yt-ai-toggle">▼</button>
    </div>
    <div class="yt-ai-content" id="yt-ai-content">
      <div class="yt-ai-status" id="yt-ai-status">Ready - Type a command!</div>
      <div class="yt-ai-input-container">
        <input
          type="text"
          id="yt-ai-input"
          class="yt-ai-input"
          placeholder="Type your command (e.g., 'play lofi hip hop')..."
        />
        <button class="yt-ai-send" id="yt-ai-send">Send</button>
      </div>
      <div class="yt-ai-suggestions">
        <button class="yt-ai-suggestion">play lofi hip hop</button>
        <button class="yt-ai-suggestion">play energetic music</button>
        <button class="yt-ai-suggestion">play jazz</button>
      </div>
    </div>
  `;

  document.body.appendChild(container);

  // Set up event listeners
  setupEventListeners();
}

// Set up all event listeners
function setupEventListeners() {
  const input = document.getElementById('yt-ai-input');
  const sendBtn = document.getElementById('yt-ai-send');
  const toggle = document.getElementById('yt-ai-toggle');
  const suggestions = document.querySelectorAll('.yt-ai-suggestion');

  // Toggle expand/collapse
  toggle.addEventListener('click', () => {
    const content = document.getElementById('yt-ai-content');
    const isHidden = content.style.display === 'none';
    content.style.display = isHidden ? 'block' : 'none';
    toggle.textContent = isHidden ? '▼' : '▲';
  });

  // Send command on button click
  sendBtn.addEventListener('click', () => {
    const command = input.value.trim();
    if (command) {
      handleCommand(command);
      input.value = '';
    }
  });

  // Send command on Enter key
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const command = input.value.trim();
      if (command) {
        handleCommand(command);
        input.value = '';
      }
    }
  });

  // Handle suggestion clicks
  suggestions.forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.textContent;
      handleCommand(btn.textContent);
      input.value = '';
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const content = document.getElementById('yt-ai-content');
      content.style.display = 'none';
      toggle.textContent = '▲';
    }
  });
}

// Handle user commands
async function handleCommand(command) {
  console.log('🎵 Command received:', command);
  updateStatus('Processing...', 'loading');

  try {
    // Send command to background script for AI processing
    const response = await chrome.runtime.sendMessage({
      type: 'PROCESS_COMMAND',
      command: command
    });

    if (response.success) {
      updateStatus(response.message, 'success');

      // Execute the search on YouTube
      if (response.searchQuery) {
        searchAndPlayYouTube(response.searchQuery);
      }
    } else {
      updateStatus('Error: ' + response.error, 'error');
    }
  } catch (error) {
    console.error('Error processing command:', error);
    updateStatus('Error: ' + error.message, 'error');
  }
}

// Update status message
function updateStatus(message, type = 'info') {
  const status = document.getElementById('yt-ai-status');
  status.textContent = message;
  status.className = 'yt-ai-status ' + type;

  // Clear status after 5 seconds for success/error
  if (type === 'success' || type === 'error') {
    setTimeout(() => {
      status.textContent = 'Ready - Type a command!';
      status.className = 'yt-ai-status';
    }, 5000);
  }
}

// Search and play on YouTube
function searchAndPlayYouTube(query) {
  console.log('🔍 Searching YouTube for:', query);

  // Navigate to YouTube search
  const searchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;

  if (window.location.href.includes('/watch')) {
    // If on a video page, open in same tab
    window.location.href = searchUrl;
  } else {
    // Navigate to search results
    window.location.href = searchUrl;
  }

  // Wait for search results and play first video
  setTimeout(() => {
    const firstVideo = document.querySelector('ytd-video-renderer a#video-title');
    if (firstVideo) {
      updateStatus('Playing: ' + firstVideo.textContent, 'success');
      firstVideo.click();
    }
  }, 1500);
}

// Initialize when YouTube is ready
waitForYouTube().then(() => {
  console.log('✅ YouTube loaded, creating command box...');
  createCommandBox();

  // Show welcome message
  setTimeout(() => {
    updateStatus('AI Agent ready! Press K to focus command box.', 'success');
  }, 1000);
});

// Keyboard shortcut: K to focus command box
document.addEventListener('keydown', (e) => {
  // Only if not typing in another input
  if (e.key === 'k' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
    e.preventDefault();
    const input = document.getElementById('yt-ai-input');
    const content = document.getElementById('yt-ai-content');
    if (input) {
      content.style.display = 'block';
      document.getElementById('yt-ai-toggle').textContent = '▼';
      input.focus();
    }
  }
});
