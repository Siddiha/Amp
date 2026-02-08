# 🎵 AMP - AI Music Player

Your intelligent Spotify assistant. Just type what you want and AMP does it automatically!

![AMP Demo](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square) ![Spotify](https://img.shields.io/badge/Spotify-API-1DB954?style=flat-square) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat-square)

## ✨ Features

- **Natural Language Control** - Just type "play some chill music" or "skip this"
- **Smart Recommendations** - AI-powered music suggestions based on mood
- **Playlist Creation** - "Create a workout playlist" and it's done
- **Real-time Now Playing** - See what's playing with progress bar
- **Conversation Memory** - "Play more like this" remembers context

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/amp.git
cd amp
pip install -r requirements.txt
```

### 2. Get API Keys

**Spotify:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Add `http://localhost:8888/callback` to Redirect URIs
4. Copy Client ID and Client Secret

**OpenAI:**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new key

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
|---------|--------------|
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
AMP: ▶️ Playing - Take Five by Dave Brubeck

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

- **Python 3.11+** - Core language
- **Spotipy** - Spotify API wrapper
- **OpenAI GPT-4** - Natural language understanding
- **Rich** - Beautiful terminal UI
- **Click** - CLI framework

## 📁 Project Structure

```
amp/
├── amp.py           # Main application (single file!)
├── requirements.txt # Dependencies
├── .env.example     # Environment template
├── .env             # Your API keys (not tracked)
└── .spotify_cache   # Spotify auth cache (not tracked)
```

## 🔧 Troubleshooting

**"No active device"**
- Open Spotify app on your computer/phone first
- Make sure you're logged in

**"Missing API keys"**
- Copy `.env.example` to `.env`
- Add your Spotify and OpenAI keys

**Auth not working**
- Delete `.spotify_cache` and try again
- Make sure redirect URI matches in Spotify Dashboard

## 📝 License

MIT - Do whatever you want with it!

---

Made with 🎵 by [Your Name]
