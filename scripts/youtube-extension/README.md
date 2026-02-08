# 🎵 YouTube AI Music Agent - Browser Extension

Control YouTube with natural language commands using AI!

## ✨ Features

- **Natural Language Control** - Type "play lofi hip hop" and it automatically searches and plays
- **Beautiful UI** - Sleek command box that floats on YouTube pages
- **AI-Powered** - Uses Claude AI to understand your commands
- **Keyboard Shortcuts** - Press `K` to quickly focus the command box
- **Quick Suggestions** - Click pre-made command suggestions

## 🚀 Installation

### 1. Get Your Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Create a new API key
3. Copy it (starts with `sk-ant-api03-...`)

### 2. Add Extension Icons (Required)

The extension needs icons to work. Create or download icons and place them in the `icons/` folder:

- `icons/icon16.png` (16x16 pixels)
- `icons/icon48.png` (48x48 pixels)
- `icons/icon128.png` (128x128 pixels)

**Quick way to create icons:**
You can use any 🎵 emoji or music note image and resize it to the required sizes.

### 3. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `youtube-extension` folder
5. The extension icon should appear in your toolbar!

### 4. Configure API Key

1. Click the extension icon in your toolbar
2. Paste your Anthropic API key
3. Click **Save Settings**

## 🎯 How to Use

### On YouTube:

1. Go to any YouTube page (youtube.com)
2. You'll see a purple command box in the bottom-right corner
3. Type your command (or press `K` to focus)
4. Press Enter or click Send

### Example Commands:

```
play lofi hip hop
play something energetic
I want to hear jazz
play Taylor Swift
find sad music
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `K` | Focus command box |
| `Enter` | Send command |
| `Esc` | Close command box |

## 🛠️ Files

```
youtube-extension/
├── manifest.json       # Extension configuration
├── content.js         # Injects UI into YouTube
├── background.js      # Handles AI API calls
├── styles.css         # Command box styling
├── popup.html         # Settings page
├── popup.js           # Settings logic
├── icons/            # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

## 🔧 Troubleshooting

**Extension won't load:**
- Make sure you have icon files in the `icons/` folder
- Check that all files are in the same directory
- Try reloading the extension in `chrome://extensions/`

**Commands not working:**
- Click the extension icon and verify API key is saved
- Check browser console for errors (F12 → Console tab)
- Make sure you're on youtube.com

**API errors:**
- Verify your API key is correct
- Check you have credits in your Anthropic account
- Make sure API key starts with `sk-ant-api03-`

## 💡 Tips

- Use natural language - the AI understands context!
- Click the suggestion buttons for quick commands
- The command box is draggable (future feature)
- Works on all YouTube pages (search, watch, home)

## 🎵 How It Works

1. You type a command in the floating box
2. Content script sends it to background script
3. Background script calls Claude AI API
4. AI extracts the search query from your natural language
5. Extension searches YouTube and plays first result

## 📝 License

MIT - Built as part of the AMP (AI Music Player) project

---

Made with 🎵 by the AMP Team
