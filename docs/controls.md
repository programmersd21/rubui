# Controls Reference

## Face Moves

| Key | Move | Description |
|-----|------|-------------|
| `R` | R | Right face clockwise |
| `L` | L | Left face clockwise |
| `U` | U | Upper face clockwise |
| `D` | D | Down face clockwise |
| `F` | F | Front face clockwise |
| `B` | B | Back face clockwise |

## Wide Moves (Lowercase)

| Key | Move | Description |
|-----|------|-------------|
| `r` | Rw | Right two layers clockwise |
| `l` | Lw | Left two layers clockwise |
| `u` | Uw | Upper two layers clockwise |
| `d` | Dw | Down two layers clockwise |
| `f` | Fw | Front two layers clockwise |
| `b` | Bw | Back two layers clockwise |

## Prime / Double Modifiers

- Press `'` (or `` ` `` / `;`) then a move to make it prime: `R'`, `U'`, etc.
- Press `2` then a move for a double turn, or press `2` within 350ms after a move to convert it to `X2`.

## Middle Layers

| Key | Move | Description |
|-----|------|-------------|
| `m` | M | Middle slice clockwise |
| `e` | E | Equatorial slice clockwise |
| `S` (command prompt) | S | Standing slice clockwise |

## Cube Rotations

| Key | Rotation | Meaning |
|-----|----------|---------|
| `x` | x | Rotate the whole cube like an R turn |
| `y` | y | Rotate the whole cube like a U turn |
| `z` | z | Rotate the whole cube like an F turn |

## Camera (View)

| Key | Action |
|-----|--------|
| Arrow keys | Rotate cube view |

## Actions

| Key | Action |
|-----|--------|
| `s` | Scramble the cube |
| `v` | Solve the cube (kociemba) |
| `Ctrl+Z` | Undo last move |
| `Ctrl+Y` | Redo last undone move |
| `m` | Switch between manual/auto mode |
| `:` or `/` | Open command prompt |
| `?` | Show help overlay |
| `q` | Quit |

## Command Prompt

Press `:` or `/` to open the command prompt at the bottom of the screen.

Type standard cube notation (space-separated):

```
R U R' U'
F2 D L' U2
x y R U R'
```

- **Enter** — Execute the sequence
- **Escape** — Cancel and close prompt
- **Backspace** — Delete last character
