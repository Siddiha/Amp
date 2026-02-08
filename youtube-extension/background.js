// YouTube AI Music Agent - Background Script
// Handles AI API calls to Claude

console.log('🎵 YouTube AI Agent Background Service loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'PROCESS_COMMAND') {
    processCommand(request.command)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({
        success: false,
        error: error.message
      }));
    return true; // Keep channel open for async response
  }
});

// Process user command with Claude AI
async function processCommand(command) {
  try {
    console.log('🤖 Processing command:', command);

    // Get API key from storage
    const { apiKey } = await chrome.storage.sync.get(['apiKey']);

    if (!apiKey) {
      return {
        success: false,
        error: 'API key not set. Click the extension icon to configure.'
      };
    }

    // Call Claude API
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 200,
        messages: [{
          role: 'user',
          content: `You are a YouTube music assistant. The user said: "${command}"

Extract the music search query from this command. Respond with ONLY the search query text, nothing else.

Examples:
User: "play lofi hip hop" → "lofi hip hop"
User: "play something energetic" → "energetic music"
User: "I want to hear jazz" → "jazz music"
User: "play Taylor Swift" → "Taylor Swift"

Now extract the search query:`
        }]
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'API request failed');
    }

    const data = await response.json();
    const searchQuery = data.content[0].text.trim();

    console.log('✅ AI extracted search query:', searchQuery);

    return {
      success: true,
      message: `🎵 Searching for: ${searchQuery}`,
      searchQuery: searchQuery
    };

  } catch (error) {
    console.error('❌ Error processing command:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Handle extension installation
chrome.runtime.onInstalled.addListener(async () => {
  console.log('🎵 YouTube AI Music Agent installed!');

  // Check if API key is set
  const { apiKey } = await chrome.storage.sync.get(['apiKey']);

  if (!apiKey) {
    // Open options page to set API key
    chrome.runtime.openOptionsPage();
  }
});
