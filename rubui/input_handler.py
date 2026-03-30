"""
rubui.input_handler
~~~~~~~~~~~~~~~~~~~
Cross-platform raw keyboard input for the TUI.
Supports full move set, modifiers, and arrow-key camera rotation.
"""

from __future__ import annotations

import sys
import time

# ── cross-platform getch ──────────────────────────────────────────────────

if sys.platform == "win32":
    import msvcrt

    def _getch_raw() -> str | None:
        if msvcrt.kbhit():
            return msvcrt.getwch()
        return None

    def _getch_blocking() -> str:
        return msvcrt.getwch()

    def kbhit() -> bool:
        return msvcrt.kbhit()

else:
    import select
    import termios
    import tty

    _old_settings = None

    def _init_raw() -> None:
        global _old_settings
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    def _restore() -> None:
        global _old_settings
        if _old_settings is not None:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, _old_settings)

    def _getch_raw() -> str | None:
        fd = sys.stdin.fileno()
        rlist, _, _ = select.select([fd], [], [], 0)
        if rlist:
            return sys.stdin.read(1)
        return None

    def _getch_blocking() -> str:
        return sys.stdin.read(1)

    def kbhit() -> bool:
        fd = sys.stdin.fileno()
        rlist, _, _ = select.select([fd], [], [], 0)
        return bool(rlist)


# ── key-to-move mapping ───────────────────────────────────────────────────

# Direct single-key moves (clockwise). Lowercase = wide moves.
KEY_MOVE_MAP: dict[str, str] = {
    "R": "R",
    "L": "L",
    "U": "U",
    "D": "D",
    "F": "F",
    "B": "B",
    "r": "Rw",
    "l": "Lw",
    "u": "Uw",
    "d": "Dw",
    "f": "Fw",
    "b": "Bw",
    "m": "M",
    "e": "E",
    "s": "S",
    "x": "x",
    "y": "y",
    "z": "z",
}

DOUBLE_TURN: dict[str, str] = {
    "R": "R2",
    "R'": "R2",
    "R2": "R2",
    "L": "L2",
    "L'": "L2",
    "L2": "L2",
    "U": "U2",
    "U'": "U2",
    "U2": "U2",
    "D": "D2",
    "D'": "D2",
    "D2": "D2",
    "F": "F2",
    "F'": "F2",
    "F2": "F2",
    "B": "B2",
    "B'": "B2",
    "B2": "B2",
    "Rw": "Rw2",
    "Rw'": "Rw2",
    "Lw": "Lw2",
    "Lw'": "Lw2",
    "Uw": "Uw2",
    "Uw'": "Uw2",
    "Dw": "Dw2",
    "Dw'": "Dw2",
    "Fw": "Fw2",
    "Fw'": "Fw2",
    "Bw": "Bw2",
    "Bw'": "Bw2",
    "M": "M2",
    "M'": "M2",
    "E": "E2",
    "E'": "E2",
    "S": "S2",
    "S'": "S2",
    "x": "x2",
    "x'": "x2",
    "y": "y2",
    "y'": "y2",
    "z": "z2",
    "z'": "z2",
}


class InputHandler:
    """Handles keyboard input with modifiers and command prompt."""

    DOUBLE_TURN_WINDOW = 0.35

    def __init__(self) -> None:
        self._last_move: str = ""
        self._last_move_time: float = 0.0
        self._command_mode: bool = False
        self._command_buffer: str = ""
        self._prime_next: bool = False
        self._double_next: bool = False

    @property
    def in_command_mode(self) -> bool:
        return self._command_mode

    @property
    def command_buffer(self) -> str:
        return self._command_buffer

    def enter_command_mode(self) -> None:
        self._command_mode = True
        self._command_buffer = ""

    def exit_command_mode(self) -> tuple[str, bool]:
        buf = self._command_buffer
        self._command_mode = False
        self._command_buffer = ""
        return buf, True

    def cancel_command_mode(self) -> None:
        self._command_mode = False
        self._command_buffer = ""

    def process_key(self, key: str) -> dict:
        result: dict = {"action": "none", "move": "", "command": ""}
        now = time.perf_counter()

        # ── Command mode ──
        if self._command_mode:
            if key == "\r" or key == "\n":
                buf, _ = self.exit_command_mode()
                result["action"] = "command_submit"
                result["command"] = buf
            elif key == "\x1b":
                self.cancel_command_mode()
                result["action"] = "command_update"
            elif key in ("\x7f", "\b", "\x08"):
                self._command_buffer = self._command_buffer[:-1]
                result["action"] = "command_update"
            else:
                if len(key) == 1 and key.isprintable():
                    self._command_buffer += key
                    result["action"] = "command_update"
            return result

        # ── Special keys ──
        if key in ("q", "Q"):
            result["action"] = "quit"
            return result
        if key in ("s", "S"):
            result["action"] = "scramble"
            return result
        if key == "\x1a":  # Ctrl+Z
            result["action"] = "undo"
            return result
        if key == "\x19":  # Ctrl+Y
            result["action"] = "redo"
            return result
        if key == "?":
            result["action"] = "help"
            return result
        if key in (":", "/"):
            self.enter_command_mode()
            result["action"] = "command_update"
            return result
        if key in ("m", "M"):
            result["action"] = "mode_switch"
            return result
        if key in ("v", "V"):
            result["action"] = "solve"
            return result

        # ── Modifiers ──
        if key in ("'", "`", ";"):
            self._prime_next = True
            return result
        if key == "2":
            if (
                self._last_move
                and self._last_move in DOUBLE_TURN
                and (now - self._last_move_time) < self.DOUBLE_TURN_WINDOW
            ):
                result["action"] = "move"
                result["move"] = DOUBLE_TURN[self._last_move]
                result["replace_last"] = True
                self._last_move = ""
                return result
            self._double_next = True
            return result

        # ── Arrow keys (camera rotation) ──
        if key in ("LEFT", "RIGHT", "UP", "DOWN"):
            if key == "LEFT":
                result["action"] = "move"
                result["move"] = "y'"
                return result
            if key == "RIGHT":
                result["action"] = "move"
                result["move"] = "y"
                return result
            if key == "UP":
                result["action"] = "move"
                result["move"] = "x'"
                return result
            if key == "DOWN":
                result["action"] = "move"
                result["move"] = "x"
                return result

        # ── Regular moves ──
        if key in KEY_MOVE_MAP:
            move = KEY_MOVE_MAP[key]
            if self._double_next:
                move = move + "2"
            elif self._prime_next:
                move = move + "'"
            result["action"] = "move"
            result["move"] = move
            self._last_move = move
            self._last_move_time = now
            self._prime_next = False
            self._double_next = False
            return result

        return result


# ── Help text ─────────────────────────────────────────────────────────────

HELP_TEXT = """
╭─────────────────────────────────────────╮
│            rubui — Controls             │
├─────────────────────────────────────────┤
│                                         │
│  Face Moves (single layer):             │
│    R L U D F B                           │
│                                         │
│  Wide Moves (lowercase):                │
│    r l u d f b  →  Rw Lw Uw Dw Fw Bw     │
│                                         │
│  Prime / Double Modifiers:              │
│    ' then move  →  X'                   │
│    2 then move  →  X2                   │
│    move then 2  →  X2                   │
│                                         │
│  Middle Layers:                         │
│    m e    →  M E                        │
│                                         │
│  Rotations:                             │
│    x y z  →  whole cube rotations       │
│                                         │
│  Camera (arrow keys):                   │
│    ← → ↑ ↓  →  rotate cube view         │
│                                         │
│  Actions:                               │
│    s      →  Scramble                   │
│    v      →  Solve (kociemba)           │
│    Ctrl+Z →  Undo                       │
│    Ctrl+Y →  Redo                       │
│    :  /   →  Command prompt             │
│    m      →  Switch mode                │
│    ?      →  This help                  │
│    q      →  Quit                       │
│                                         │
│  Command prompt:                        │
│    Type moves like: R U R' U'           │
│    Press Enter to execute               │
│    Press Escape to cancel               │
│                                         │
╰─────────────────────────────────────────╯
"""
