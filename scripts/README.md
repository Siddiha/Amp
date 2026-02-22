# 🎵 AMP — AI Music Player

Your intelligent music assistant. Just type what you want and AMP does it automatically!

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![Spotify](https://img.shields.io/badge/Spotify-API-1DB954?style=flat-square)
![YouTube Music](https://img.shields.io/badge/YouTube-Music-FF0000?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-Free-4285F4?style=flat-square)

## ✨ Features

- **Natural Language Control** — "play some chill music" or "skip this"
- **Multiple Music Sources** — Spotify (full control) or YouTube Music (browser)
- **Multiple AI Providers** — Gemini (free), Groq (free), or Claude
- **Smart Recommendations** — AI-powered suggestions based on mood
- **Playlist Creation** — "Create a workout playlist" and it's done
- **Real-time Now Playing** — progress bar in the terminal
- **Conversation Memory** — "Play more like this" remembers context

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/amp.git
cd amp
pip install -r requirements.txt
```

### 2. Get API Keys

**Music Provider** (choose one):

- **YouTube Music** — no keys needed (default)
- **Spotify** — Create an app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard), add `http://localhost:8888/callback` as redirect URI

**AI Provider** (choose one):

- **Google Gemini** — Free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **Groq** — Free at [console.groq.com/keys](https://console.groq.com/keys)
- **Anthropic Claude** — Paid at [console.anthropic.com](https://console.anthropic.com/settings/keys)

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your keys
```

### 4. Run

```bash
# Interactive mode
python amp.py

# Quick command
python amp.py "play lofi beats"
```

## 💬 Commands

| Command | What it does |
|---------|-------------|
| `play <song>` | Search and play a song |
| `pause` | Pause playback |
| `skip` / `next` | Skip to next track |
| `back` / `prev` | Previous track |
| `volume 50` | Set volume (0-100) |
| `search <query>` | Search without playing |
| `queue <song>` | Add song to queue |
| `recommend` | Get AI recommendations |
| `like` / `save` | Save current song |
| `playlist <name>` | Create AI playlist |
| `shuffle on/off` | Toggle shuffle |
| `now` / `playing` | What's playing? |

**Or just type naturally!** AMP understands things like:
- "play something energetic"
- "I'm feeling sad, play something to match"
- "skip this, too slow"
- "create a playlist called Morning Coffee with chill vibes"

## 🎯 Examples

```
You: play some jazz
AMP: 🎷 Playing Take Five by Dave Brubeck

You: skip, I want something more upbeat
AMP: ⏭️ Skipped! Now playing "Sing Sing Sing" by Benny Goodman

You: add fly me to the moon to queue
AMP: ➕ Added to queue: Fly Me to the Moon - Frank Sinatra

You: create a focus playlist
AMP: ✅ Created 'Focus' with 20 tracks!

You: like this song
AMP: 💚 Saved 'Sing Sing Sing' to library!
```

## 🛠️ Tech Stack

- **Python 3.11+** — Core language
- **Spotipy** — Spotify API wrapper
- **ytmusicapi** — YouTube Music search
- **Google Gemini / Groq / Claude** — Natural language understanding
- **Rich** — Beautiful terminal UI
- **Click** — CLI framework

## 📁 Project Structure

```
Amp/
├── amp.py                  # Entry point
├── requirements.txt
├── .env.example
│
├── amp/
│   ├── agent/              # AI agent (processes commands)
│   ├── cli/                # Terminal interface
│   ├── config/             # Configuration
│   ├── llm/                # Gemini / Groq / Claude providers
│   ├── models/             # Data models
│   ├── spotify/            # Spotify + YouTube Music players
│   └── utils/              # Logging, caching, audio utils
│
└── youtube-extension/      # Chrome extension
```

## 🔧 Troubleshooting

**"No active device"** (Spotify)
- Open Spotify app on your computer first, start playing, then retry

**"Missing API keys"**
- Copy `.env.example` to `.env` and add your keys

**Spotify auth not working**
- Delete `.spotify_cache` and try again
- Make sure redirect URI matches in Spotify Dashboard

## 📝 License

MIT — Do whatever you want with it!

---

Made with 🎵 by AMP Team
