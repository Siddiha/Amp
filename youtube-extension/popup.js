// YouTube AI Music Agent - Popup Script
// Handles extension settings

document.addEventListener('DOMContentLoaded', async () => {
  const apiKeyInput = document.getElementById('api-key');
  const saveBtn = document.getElementById('save-btn');
  const status = document.getElementById('status');

  // Load saved API key
  const { apiKey } = await chrome.storage.sync.get(['apiKey']);
  if (apiKey) {
    apiKeyInput.value = apiKey;
  }

  // Save API key
  saveBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
      showStatus('Please enter an API key', 'error');
      return;
    }

    if (!apiKey.startsWith('sk-ant-')) {
      showStatus('Invalid API key format', 'error');
      return;
    }

    try {
      await chrome.storage.sync.set({ apiKey });
      showStatus('✅ Settings saved successfully!', 'success');

      // Clear input (for security)
      setTimeout(() => {
        apiKeyInput.value = '••••••••••••••••';
      }, 1000);
    } catch (error) {
      showStatus('❌ Error saving settings', 'error');
    }
  });

  // Show status message
  function showStatus(message, type) {
    status.textContent = message;
    status.className = 'status ' + type;

    if (type === 'success') {
      setTimeout(() => {
        status.className = 'status';
      }, 3000);
    }
  }

  // Enter key to save
  apiKeyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      saveBtn.click();
    }
  });
});
