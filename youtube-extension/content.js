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
  setupEventListeners();
}

// Set up all event listeners
function setupEventListeners() {
  const input = document.getElementById('yt-ai-input');
  const sendBtn = document.getElementById('yt-ai-send');
  const toggle = document.getElementById('yt-ai-toggle');
  const suggestions = document.querySelectorAll('.yt-ai-suggestion');

  toggle.addEventListener('click', () => {
    const content = document.getElementById('yt-ai-content');
    const isHidden = content.style.display === 'none';
    content.style.display = isHidden ? 'block' : 'none';
    toggle.textContent = isHidden ? '▼' : '▲';
  });

  sendBtn.addEventListener('click', () => {
    const command = input.value.trim();
    if (command) {
      handleCommand(command);
      input.value = '';
    }
  });

  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const command = input.value.trim();
      if (command) {
        handleCommand(command);
        input.value = '';
      }
    }
  });

  suggestions.forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.textContent;
      handleCommand(btn.textContent);
      input.value = '';
    });
  });

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
    const response = await chrome.runtime.sendMessage({
      type: 'PROCESS_COMMAND',
      command: command
    });

    if (response.success) {
      updateStatus(response.message, 'success');
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
  if (!status) return;
  status.textContent = message;
  status.className = 'yt-ai-status ' + type;

  if (type === 'success' || type === 'error') {
    setTimeout(() => {
      if (status) {
        status.textContent = 'Ready - Type a command!';
        status.className = 'yt-ai-status';
      }
    }, 5000);
  }
}

// Navigate to YouTube search and store auto-play intent for the new page
function searchAndPlayYouTube(query) {
  chrome.storage.local.set({ autoPlay: true, autoPlayQuery: query });
  window.location.href = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
}

// Poll for the first search result and click it (runs on the search results page)
function waitForFirstVideoAndPlay() {
  let attempts = 0;
  const interval = setInterval(() => {
    const firstVideo = document.querySelector('ytd-video-renderer a#video-title');
    if (firstVideo) {
      clearInterval(interval);
      updateStatus('Playing: ' + firstVideo.textContent.trim(), 'success');
      firstVideo.click();
    } else if (++attempts >= 20) {
      clearInterval(interval);
      updateStatus('Could not auto-play. Click a video to start.', 'error');
    }
  }, 500);
}

// Initialize when YouTube is ready
waitForYouTube().then(async () => {
  console.log('✅ YouTube loaded, creating command box...');
  createCommandBox();

  // Check for pending auto-play stored by the previous page before it navigated
  const { autoPlay } = await chrome.storage.local.get(['autoPlay']);
  if (autoPlay) {
    await chrome.storage.local.remove(['autoPlay', 'autoPlayQuery']);
    waitForFirstVideoAndPlay();
  } else {
    setTimeout(() => {
      updateStatus('AI Agent ready! Press ` (backtick) to open.', 'success');
    }, 1000);
  }
});

// Keyboard shortcut: backtick (`) to focus command box — avoids YouTube's k/j/l conflicts
document.addEventListener('keydown', (e) => {
  if (e.key === '`' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
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
