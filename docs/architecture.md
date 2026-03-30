# Architecture

## Module Dependency Graph

```
main.py (CLI entry point)
  ├── config.py (configuration loading)
  ├── manual_mode.py
  │     ├── cube_engine.py (cube state)
  │     ├── moves.py (move execution)
  │     ├── parser.py (notation parsing)
  │     ├── renderer.py (3D rendering)
  │     ├── input_handler.py (keyboard input)
  │     ├── solver.py (kociemba integration)
  │     └── utils.py (terminal utilities)
  └── auto_mode.py
        ├── cube_engine.py
        ├── moves.py
        ├── renderer.py
        └── utils.py
```

## Module Descriptions

### `cube_engine.py`
Core cube state: dictionary mapping face names to 9-element sticker arrays.
Provides solved-state factory, `is_solved()`, state copy/load, move history
tracking (undo/redo stacks), and scramble generation.

### `moves.py`
All 18 face moves (R/L/U/D/F/B × CW/CCW/double) and 6 cube rotations
(x/y/z × both directions). Each move mutates sticker arrays in-place via
direct index permutations. Includes dispatch table, inverse lookup, and
`undo()`/`redo()` functions.

### `parser.py`
Parses space-separated cube notation strings into validated token lists.
Handles Unicode prime characters and provides clear error messages.

### `renderer.py`
Two rendering modes:
- **3D Isometric**: Shows top, front, and right faces with brightness-based
  depth shading using ANSI truecolour backgrounds.

Also renders: animated pyfiglet banner, live status bar, full frame composer.

### `config.py`
TOML configuration with layered priority (CLI > local file > global file >
defaults). Uses `tomllib` (3.11+) with `tomli` fallback. Provides the
`rubui init` config file generator.

### `input_handler.py`
Cross-platform raw keyboard input (msvcrt on Windows, termios on Unix).
Key-to-move mapping, 350ms double-turn detection, integrated command
prompt mode, and special key handling.

### `manual_mode.py`
Main interactive game loop: render → read input → animate move → repeat.
Includes animated startup banner, live status bar, help overlay, command
prompt, and clean terminal lifecycle management.

### `solver.py`
Converts the current cube state into Kociemba facelet order (URFDLB) and
invokes the `kociemba` package to return a move sequence that solves the cube.

### `auto_mode.py`
Screensaver mode: picks random moves at configurable speed, renders
continuously, responds to quit/mode-switch.

### `utils.py`
Terminal primitives: ANSI support detection (with Windows VT processing
enablement), cursor/screen control, RGB colour helpers, theme definitions
(dark/light/monochrome), frame timer, and time formatting.
