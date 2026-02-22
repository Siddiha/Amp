// YouTube AI Music Agent - Popup Script
// Handles extension settings — Claude & Gemini provider support

const PROVIDER_INFO = {
  gemini: {
    placeholder: 'AIzaSy...',
    badge: 'FREE',
    info: 'Get a free Gemini key at <a href="https://aistudio.google.com/apikey" target="_blank">aistudio.google.com</a>',
    validate: (key) => key.startsWith('AIza') && key.length > 20,
    error: 'Gemini keys start with "AIza..."'
  },
  claude: {
    placeholder: 'sk-ant-api03-xxxxx...',
    badge: 'PAID',
    info: 'Get your API key from <a href="https://console.anthropic.com/settings/keys" target="_blank">Anthropic Console</a>',
    validate: (key) => key.startsWith('sk-ant-'),
    error: 'Claude keys start with "sk-ant-..."'
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  const apiKeyInput = document.getElementById('api-key');
  const providerSelect = document.getElementById('provider');
  const saveBtn = document.getElementById('save-btn');
  const statusEl = document.getElementById('status');
  const keyBadge = document.getElementById('key-badge');
  const keyInfo = document.getElementById('key-info');

  // Load saved settings
  const { apiKey, provider } = await chrome.storage.sync.get(['apiKey', 'provider']);
  const savedProvider = provider || 'gemini';

  providerSelect.value = savedProvider;
  if (apiKey) {
    apiKeyInput.value = apiKey;
  }
  updateProviderUI(savedProvider);

  // Update UI when provider changes
  providerSelect.addEventListener('change', () => {
    const info = PROVIDER_INFO[providerSelect.value];
    apiKeyInput.value = '';
    apiKeyInput.placeholder = info.placeholder;
    updateProviderUI(providerSelect.value);
  });

  // Save settings on button click
  saveBtn.addEventListener('click', async () => {
    const key = apiKeyInput.value.trim();
    const selectedProvider = providerSelect.value;
    const info = PROVIDER_INFO[selectedProvider];

    if (!key) {
      showStatus('Please enter an API key', 'error');
      return;
    }

    if (!info.validate(key)) {
      showStatus(info.error, 'error');
      return;
    }

    try {
      await chrome.storage.sync.set({ apiKey: key, provider: selectedProvider });
      showStatus('✅ Settings saved!', 'success');
      setTimeout(() => {
        apiKeyInput.value = '••••••••••••••••';
      }, 1000);
    } catch (error) {
      showStatus('❌ Error saving settings', 'error');
    }
  });

  // Enter key to save
  apiKeyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') saveBtn.click();
  });

  function updateProviderUI(provider) {
    const info = PROVIDER_INFO[provider];
    keyBadge.textContent = info.badge;
    keyBadge.style.background = provider === 'gemini'
      ? 'rgba(76, 175, 80, 0.4)'
      : 'rgba(255, 152, 0, 0.4)';
    keyInfo.innerHTML = info.info;
    apiKeyInput.placeholder = info.placeholder;
  }

  function showStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = 'status ' + type;
    if (type === 'success') {
      setTimeout(() => { statusEl.className = 'status'; }, 3000);
    }
  }
});
