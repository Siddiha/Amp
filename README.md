#  AMP 

Your intelligent music assistant. Just type what you want — AMP understands and acts!

##  Features

- **Natural Language Control** — say "play something chill" or "skip this, too slow"
- **Multiple Music Sources** — Spotify (full control) or YouTube Music (browser-based)
- **Multiple AI Providers** — Google Gemini (free), Groq/Llama-3 (free & fast), or Anthropic Claude
- **Smart Recommendations** — mood-based music suggestions (happy, sad, chill, workout…)
- **AI Playlist Creation** — "create a focus playlist" and it's done
- **Real-time Now Playing** — progress bar in the terminal
- **Conversation Memory** — "play more like this" keeps context
- **Shell Commands** — run `!git status` or `!ls` from inside AMP
- **Chrome Extension** — AI command box injected into YouTube pages

---

##  Quick Start

### 1. Install

```bash
git clone https://github.com/yourusername/amp.git
cd amp
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your keys (see below)
```

### 3. Run

```bash
# Interactive mode
python amp.py

# One-shot command
python amp.py "play lofi beats"
```

---

## 🔑 API Keys

### Music Provider

Choose one via `MUSIC_PROVIDER` in `.env`:

| Provider | Env var(s) | Notes |
|----------|-----------|-------|
| **YouTube Music** (default) | _(none required)_ | Opens browser tab |
| **Spotify** | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` | Full native control |

Spotify keys: [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) → create app → add `http://localhost:8888/callback` as redirect URI.

### AI Provider

Choose one via `AMP_LLM_PROVIDER` in `.env`:

| Provider | Env var | Cost | Notes |
|----------|---------|------|-------|
| **Gemini** (default) | `GOOGLE_API_KEY` | Free | [aistudio.google.com](https://aistudio.google.com/apikey) |
| **Groq** | `GROQ_API_KEY` | Free | [console.groq.com](https://console.groq.com/keys) |
| **Claude** | `ANTHROPIC_API_KEY` | Paid | [console.anthropic.com](https://console.anthropic.com/settings/keys) |

---

## 💬 Commands

| Command | What it does |
|---------|-------------|
| `play <song>` | Search and play a song |
| `pause` | Pause playback |
| `skip` / `next` | Skip to next track |
| `back` / `prev` | Previous track |
| `volume 50` | Set volume (0–100) |
| `search <query>` | Search without playing |
| `queue <song>` | Add song to queue |
| `recommend` | Get AI recommendations |
| `like` / `save` | Save current song |
| `playlist <name>` | Create AI playlist |
| `shuffle on/off` | Toggle shuffle |
| `now` / `np` | What's playing? |
| `!<shell cmd>` | Run shell command |
| `cd <path>` | Change directory |
| `help` | Show all commands |
| `quit` / `exit` | Exit AMP |

**Or just type naturally!** AMP understands:
- "play something energetic"
- "I'm feeling sad, play something to match"
- "create a workout playlist with 15 songs"
- "turn it up a bit"

---

## 🎯 Example Session

```
AMP - AI Music Player

✓ Connected to YouTube Music

Now Playing
No music playing
Type 'play <song>' to start!

You: play some jazz

AMP: 🎷 Opening "Take Five - Dave Brubeck" in YouTube Music!

You: skip, I want something more upbeat

AMP: ⏭️ Skipped! Opening "Sing Sing Sing - Benny Goodman" now.

You: create a focus playlist

AMP: ✅ Created 'Focus' with 20 tracks!

You: what's playing?

AMP: 🎵 Playing: Sing Sing Sing by Benny Goodman
```

---

## 🌐 Chrome Extension

AMP includes a **YouTube AI Music Agent** Chrome extension that injects an AI command box directly into YouTube pages.

### Install

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `youtube-extension/` folder
5. Click the extension icon → paste your AI API key → Save

### Use

- Press **K** anywhere on YouTube to open the command box
- Type any music command and press **Enter**
- The extension searches YouTube and plays the first result

---

## 📁 Project Structure

```
Amp/
├── amp.py                  # Entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── .env                    # Your secrets (not tracked)
│
├── amp/                    # Main package
│   ├── agent/              # AI agent (processes commands)
│   ├── cli/                # Terminal UI (Rich)
│   ├── config/             # Configuration management
│   ├── llm/                # LLM providers (Gemini, Groq, Claude)
│   ├── models/             # Data models (Track, Playlist, User…)
│   ├── spotify/            # Music players (Spotify + YouTube)
│   └── utils/              # Logging, caching, retry, audio utils
│
├── youtube-extension/      # Chrome extension
│   ├── manifest.json
│   ├── background.js       # AI API calls (Claude / Gemini)
│   ├── content.js          # Injected command box
│   ├── popup.html/js       # Extension settings
│   └── icons/              # Extension icons
│
└── config/                 # Optional TOML config overrides
    └── amp-common.toml
```

---

## 🔧 Troubleshooting

**"No active device"** (Spotify)
- Open the Spotify app first, start playing anything, then retry

**"Missing API keys"**
- Copy `.env.example` → `.env` and fill in your keys

**Spotify auth loop**
- Delete `.spotify_cache` and re-run; follow the browser auth URL

**YouTube Music not finding songs**
- `ytmusicapi` uses public search — no auth needed; just ensure you're online

---

## 📝 License

MIT — do whatever you want with it!

---

Made with 🎵 by AMP Team
