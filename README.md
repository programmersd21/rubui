# 🧊 rubui

> A colorful 3D Rubik's Cube terminal UI with manual and auto modes.

```
██████╗ ██╗   ██╗██████╗ ██╗   ██╗██╗
██╔══██╗██║   ██║██╔══██╗██║   ██║██║
██████╔╝██║   ██║██████╔╝██║   ██║██║
██╔══██╗██║   ██║██╔══██╗██║   ██║██║
██║  ██║╚██████╔╝██████╔╝╚██████╔╝██║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝
```

> *The demo gif might take some time to load... (it will appear below 👇)*

![Demo](demo/demo.gif)

🤩 **Rubui** is a high-performance, fully 3D interactive Rubik's Cube simulator that runs **entirely in your terminal**. No GUI, no browser—just pure terminal wizardry.

💡 **The Spark**

Amid my desk clutter—PCs, USB drives, random stuff—one thing caught my eye: a Rubik’s Cube. I thought, *“Why not bring this puzzle to my terminal?”* That tiny idea grew into **Rubui**, born from curiosity, fun, and love for coding.

🚀 **Why Rubui?**
Because your terminal deserves more than logs and scripts—it deserves **playable 3D magic**.

---

## ✨ Features

- 🎮 **Manual Mode** — Solve the cube with keyboard controls
- 🌀 **Auto Mode** — Watch the cube scramble like a colorful screensaver
- 🧊 **3D Isometric Rendering** — Three visible faces with depth and shading
- 🎨 **Rich ANSI Colors** — Vibrant face colours with theme support
- ⌨️ **Real Cube Notation** — R, U, F, L, D, B + primes + doubles
- 🔄 **Undo / Redo** — Full move history
- 🤖 **Auto Solve** — Kociemba two‑phase solver integration
- ⚡ **Smooth Animation** — Frame-based move transitions
- 📝 **Command Prompt** — Type move sequences in-app
- ⚙️ **Config System** — TOML config with CLI overrides
- 🎭 **Themes** — Dark, light, and monochrome
- 📊 **Live Status Bar** — Mode, moves, timer, FPS, theme

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/programmersd21/rubui.git
cd rubui

# Install in development mode
pip install -e .

# Run it!
rubui
```

### Requirements

- Python 3.10+
- A terminal with ANSI color support (Windows Terminal, iTerm2, any modern Linux terminal)

---

## 🎮 Usage

```bash
# Start in manual mode (default)
rubui

# Start in auto/screensaver mode
rubui -m auto

# Start scrambled
rubui --scramble

# Auto-solve the current cube (uses kociemba)
rubui --solve

# Deterministic scramble for testing
rubui --scramble --seed 42

# Control auto mode speed
rubui -m auto --speed 0.1

# Use a different theme
rubui --theme light

# Disable colours
rubui --no-color

# Generate default config
rubui init
```

---

## ⌨️ Controls (Manual Mode)

| Key | Action |
|-----|--------|
| `R L U D F B` | Face turns (clockwise) |
| `r l u d f b` | Wide turns (Rw/Lw/Uw/Dw/Fw/Bw) |
| `'` then move | Prime turn (X') |
| `2` then move | Double turn (X2) |
| `x y z` | Whole cube rotations |
| Arrow keys | Rotate cube view |
| `s` | Scramble |
| `v` | Solve (kociemba) |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `m` | Switch manual/auto mode |
| `:` or `/` | Open command prompt |
| `?` | Show help |
| `q` | Quit |

### Command Prompt

Press `:` or `/` to enter the command prompt. Type standard cube notation:

```
R U R' U'
F2 D L' U2
```

Press **Enter** to execute, **Escape** to cancel.

---

## ⚙️ Configuration

rubui supports TOML configuration files with the following priority:

1. **CLI arguments** (highest)
2. **Local `rubui.toml`** (current directory)
3. **Global `~/.config/rubui/rubui.toml`**
4. **Built-in defaults** (lowest)

Generate a default config:

```bash
rubui init
```

Example `rubui.toml`:

```toml
[app]
mode = "manual"
theme = "dark"
scramble_on_start = false
solve_on_start = false
color = true

[auto]
fps = 60
speed = 0.05

[scramble]
length = 25
seed = 0
```

---

## 🏗️ Architecture

```
rubui/
├── main.py           # CLI entry point (Typer)
├── cube_engine.py    # Core 3×3 cube state
├── moves.py          # Move execution + undo/redo
├── parser.py         # Notation parser
├── renderer.py       # 3D isometric renderer
├── config.py         # TOML config system
├── input_handler.py  # Keyboard input
├── manual_mode.py    # Interactive manual mode
├── auto_mode.py      # Screensaver auto mode
├── solver.py         # Kociemba solver integration
└── utils.py          # Terminal utilities + themes
```

See [docs/architecture.md](docs/architecture.md) for detailed module documentation.

---

## 🧪 Testing

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

---

<p align="center">
  Made with ❤️ for cube enthusiasts who live in the terminal.
</p>
