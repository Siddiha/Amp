"""AMP CLI interface — beautiful terminal UI."""

import os
import sys
import time
import subprocess
import platform
import shutil

# Fix Windows console encoding for Unicode characters (Rich UI)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box

from amp.config import init_config
from amp.spotify.player import SpotifyPlayer
from amp.spotify.youtube_player import YouTubePlayer
from amp.agent.amp_agent import AMPAgent
from amp.utils.logger import setup_logging, get_logger

logger = get_logger("cli")
console = Console(force_terminal=True)


def ensure_spotify_running() -> bool:
    """Check if Spotify is running, launch it if not. Returns True if ready."""
    system = platform.system()

    # Check if Spotify is already running
    try:
        if system == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
                capture_output=True, text=True, timeout=5
            )
            if "Spotify.exe" in result.stdout:
                return True
        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ["pgrep", "-x", "Spotify"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return True
        elif system == "Linux":
            result = subprocess.run(
                ["pgrep", "-x", "spotify"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return True
    except Exception:
        pass

    # Spotify not running — try to launch it
    console.print("[yellow]  Spotify not running. Launching...[/yellow]")
    try:
        if system == "Windows":
            # Try Microsoft Store version first, then desktop
            spotify_path = shutil.which("spotify")
            if spotify_path:
                subprocess.Popen([spotify_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(
                    ["cmd", "/c", "start", "spotify:"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", "Spotify"])
        elif system == "Linux":
            subprocess.Popen(["spotify"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for Spotify to start up
        console.print("[dim]  Waiting for Spotify to start...[/dim]")
        for _ in range(10):
            time.sleep(1.5)
            try:
                if system == "Windows":
                    result = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
                        capture_output=True, text=True, timeout=5
                    )
                    if "Spotify.exe" in result.stdout:
                        time.sleep(2)  # Extra time for Spotify to fully initialize
                        console.print("[green]  Spotify launched![/green]")
                        return True
                elif system == "Darwin":
                    result = subprocess.run(["pgrep", "-x", "Spotify"], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        time.sleep(2)
                        console.print("[green]  Spotify launched![/green]")
                        return True
                elif system == "Linux":
                    result = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        time.sleep(2)
                        console.print("[green]  Spotify launched![/green]")
                        return True
            except Exception:
                pass

        console.print("[red]  Could not launch Spotify. Please open it manually.[/red]")
        return False

    except Exception as e:
        console.print(f"[red]  Could not launch Spotify: {e}[/red]")
        console.print("[dim]  Please open Spotify manually and try again.[/dim]")
        return False


def create_header() -> Panel:
    """Create the AMP header."""
    title = Text()
    title.append("  AMP", style="bold magenta")
    title.append(" - AI Music Player", style="dim")
    return Panel(title, box=box.ROUNDED, border_style="magenta")


def create_now_playing(spotify: SpotifyPlayer) -> Panel:
    """Create now playing display."""
    track = spotify.get_current_track()
    if track:
        status = "Now Playing" if track["is_playing"] else "Paused"
        progress = track["progress_ms"] / track["duration_ms"] if track["duration_ms"] else 0
        bar_width = 30
        filled = int(progress * bar_width)
        filled = max(0, min(bar_width - 1, filled))
        bar = "━" * filled + "○" + "─" * (bar_width - filled - 1)

        content = Text()
        content.append(f"{status}\n", style="bold green" if track["is_playing"] else "bold yellow")
        content.append(f"{track['name']}\n", style="bold white")
        content.append(f"{track['artists']}\n", style="dim")
        content.append(f"[{bar}]", style="magenta")

        return Panel(content, title="Now Playing", box=box.ROUNDED, border_style="green")
    else:
        return Panel(
            "No music playing\nType 'play <song>' to start!",
            title="Now Playing",
            box=box.ROUNDED,
            border_style="dim",
        )


def execute_shell_command(command: str) -> None:
    """Execute a shell command and display output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )

        if result.stdout:
            console.print(result.stdout, style="dim")
        if result.stderr:
            console.print(result.stderr, style="red dim")

        if result.returncode != 0:
            console.print(f"[red]Command exited with code {result.returncode}[/red]")
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out (30s limit)[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def show_help():
    """Show help message."""
    help_text = """
[bold magenta]AMP Commands:[/bold magenta]

[cyan]Playback:[/cyan]
  play <song>     Play a song or artist
  pause           Pause playback
  skip / next     Skip to next track
  back / prev     Previous track
  volume <0-100>  Set volume

[cyan]Discovery:[/cyan]
  search <query>  Search for songs
  recommend       Get recommendations
  queue <song>    Add to queue

[cyan]Library:[/cyan]
  like / save     Save current song
  playlist <name> Create AI playlist

[cyan]Info:[/cyan]
  now / playing   What's playing?
  help            Show this help
  quit / exit     Exit AMP

[cyan]Shell:[/cyan]
  !<command>      Run shell command (e.g., !ls, !git status)
  cd <path>       Change directory
  pwd             Show current directory

[dim]Or just type naturally - AMP understands![/dim]
"""
    console.print(Panel(Markdown(help_text), title="Help", border_style="cyan"))


@click.command()
@click.argument("command", nargs=-1, required=False)
@click.option("--config", "config_path", default=None, help="Path to config TOML file")
def main(command, config_path):
    """AMP - Your AI Music Assistant

    Start interactive mode: python amp.py
    Quick command: python amp.py "play chill music"
    """
    # Initialize config
    config = init_config(config_path=config_path)

    # Setup logging
    setup_logging(level=config.log_level, log_file=config.log_file, debug=config.debug)

    # Validate config
    errors = config.validate()
    if errors:
        for err in errors:
            console.print(f"[red]  {err}[/red]")
        console.print("\n[dim]Copy .env.example to .env and add your keys.[/dim]")
        return

    console.print(create_header())

    # Initialize music player based on config
    music_provider = config.music_provider.lower()

    if music_provider == "youtube":
        try:
            player = YouTubePlayer()
            agent = AMPAgent(player)
            console.print("[green]✓ Connected to YouTube Music[/green]")
        except Exception as e:
            console.print(f"[red]Failed to connect to YouTube Music: {e}[/red]")
            return
    else:
        # Ensure Spotify is running (auto-launch if needed)
        ensure_spotify_running()

        try:
            player = SpotifyPlayer()
            agent = AMPAgent(player)
            console.print("[green]✓ Connected to Spotify[/green]")
        except Exception as e:
            console.print(f"[red]Failed to connect to Spotify: {e}[/red]")
            return

    # Quick command mode
    if command:
        user_input = " ".join(command)
        with console.status("[magenta]Thinking...[/magenta]"):
            response = agent.process(user_input)
        console.print(f"\n[bold cyan]AMP:[/bold cyan] {response}\n")
        return

    # Interactive mode
    console.print("[dim]Type your command or 'help' for options. 'quit' to exit.[/dim]\n")
    console.print(create_now_playing(player))
    console.print()

    while True:
        try:
            user_input = Prompt.ask("[bold magenta]You[/bold magenta]")

            if not user_input.strip():
                continue

            lower = user_input.lower().strip()

            # Built-in commands
            if lower in ["quit", "exit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break
            elif lower in ["help", "?"]:
                show_help()
                continue
            elif lower in ["now", "playing", "np"]:
                console.print(create_now_playing(player))
                continue
            elif lower == "clear":
                console.clear()
                console.print(create_header())
                continue
            elif lower == "pwd":
                console.print(f"[cyan]{os.getcwd()}[/cyan]")
                continue

            # Shell commands (prefixed with !)
            if user_input.startswith("!"):
                execute_shell_command(user_input[1:].strip())
                continue

            # Change directory command
            if lower.startswith("cd "):
                path = user_input[3:].strip()
                try:
                    os.chdir(path)
                    console.print(f"[green]Changed to: {os.getcwd()}[/green]")
                except FileNotFoundError:
                    console.print(f"[red]Directory not found: {path}[/red]")
                except PermissionError:
                    console.print(f"[red]Permission denied: {path}[/red]")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                continue

            # Process with AI
            with console.status("[magenta]Thinking...[/magenta]"):
                response = agent.process(user_input)

            console.print(f"\n[bold cyan]AMP:[/bold cyan] {response}\n")

            # Show now playing after play commands
            if any(word in lower for word in ["play", "skip", "next", "back", "prev"]):
                time.sleep(0.5)
                console.print(create_now_playing(player))
                console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
