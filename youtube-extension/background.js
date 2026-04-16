// YouTube AI Music Agent - Background Script
// Handles AI API calls — supports Claude (Anthropic) and Gemini (Google, FREE)

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

// Process user command with AI
async function processCommand(command) {
  try {
    console.log('🤖 Processing command:', command);

    // Get settings from storage
    const { apiKey, provider } = await chrome.storage.sync.get(['apiKey', 'provider']);
    const selectedProvider = provider || 'gemini'; // default to Gemini (free)

    if (!apiKey) {
      return {
        success: false,
        error: 'API key not set. Click the extension icon to configure.'
      };
    }

    const searchQuery = await extractSearchQuery(command, apiKey, selectedProvider);

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

// Extract a YouTube search query from the user's natural-language command
async function extractSearchQuery(command, apiKey, provider) {
  const prompt = `You are a YouTube music assistant. The user said: "${command}"

Extract the music search query from this command. Respond with ONLY the search query text, nothing else.

Examples:
User: "play lofi hip hop" → "lofi hip hop"
User: "play something energetic" → "energetic music"
User: "I want to hear jazz" → "jazz music"
User: "play Taylor Swift" → "Taylor Swift"

Now extract the search query:`;

  if (provider === 'gemini') {
    return await callGemini(prompt, apiKey);
  } else {
    return await callClaude(prompt, apiKey);
  }
}

// --- Gemini (Google, FREE tier) ---
async function callGemini(prompt, apiKey) {
  const model = 'gemini-2.0-flash';
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { maxOutputTokens: 60, temperature: 0.3 }
    })
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error?.message || 'Gemini API request failed');
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || 'music';
}

// --- Claude (Anthropic) ---
async function callClaude(prompt, apiKey) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-haiku-20240307',
      max_tokens: 60,
      messages: [{ role: 'user', content: prompt }]
    })
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error?.message || 'Claude API request failed');
  }

  const data = await response.json();
  return data.content[0].text.trim();
}

// Handle extension installation
chrome.runtime.onInstalled.addListener(async () => {
  console.log('🎵 YouTube AI Music Agent installed!');

  // Set Gemini as the default provider if nothing is configured
  const { provider } = await chrome.storage.sync.get(['provider']);
  if (!provider) {
    await chrome.storage.sync.set({ provider: 'gemini' });
  }

  // Open popup if no API key yet
  const { apiKey } = await chrome.storage.sync.get(['apiKey']);
  if (!apiKey) {
    chrome.action.openPopup().catch(() => {
      // openPopup() only works when Chrome is focused; silently ignore if it fails
    });
  }
});
