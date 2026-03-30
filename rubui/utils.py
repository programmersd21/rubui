"""
rubui.utils
~~~~~~~~~~~
Terminal utilities for high-density, zero-flicker rendering.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from typing import TextIO

# ── ANSI support detection ─────────────────────────────────────────────────


def supports_ansi(stream: TextIO | None = None) -> bool:
    stream = stream or sys.stdout
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
        except Exception:
            return False
    return True


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


# ── cursor / screen control ───────────────────────────────────────────────

_ESC = "\033"


def hide_cursor() -> str:
    return f"{_ESC}[?25l"


def show_cursor() -> str:
    return f"{_ESC}[?25h"


def clear_screen() -> str:
    return f"{_ESC}[2J{_ESC}[H"


def move_cursor(row: int, col: int) -> str:
    return f"{_ESC}[{row};{col}H"


def enter_alt_screen() -> str:
    return f"{_ESC}[?1049h"


def exit_alt_screen() -> str:
    return f"{_ESC}[?1049l"


def reset_ansi() -> str:
    return f"{_ESC}[0m"


def bg_rgb(r: int, g: int, b: int) -> str:
    return f"{_ESC}[48;2;{r};{g};{b}m"


def fg_rgb(r: int, g: int, b: int) -> str:
    return f"{_ESC}[38;2;{r};{g};{b}m"


def bold() -> str:
    return f"{_ESC}[1m"


def dim() -> str:
    return f"{_ESC}[2m"


# ── Official 6 Rubik's Cube colors ─────────────────────────────────────────

THEMES: dict[str, dict[str, tuple[int, int, int]]] = {
    "dark": {
        "W": (255, 255, 255),  # White
        "Y": (255, 255, 0),  # Yellow
        "G": (0, 255, 0),  # Green
        "B": (0, 0, 255),  # Blue
        "O": (255, 165, 0),  # Orange
        "R": (255, 0, 0),  # Red
    }
}

STICKER_SYMBOLS = {
    "W": "W",
    "Y": "Y",
    "G": "G",
    "B": "B",
    "O": "O",
    "R": "R",
}


class TerminalBuffer:
    """A high-performance 2D buffer for absolute zero-flicker TUI rendering."""

    def __init__(self) -> None:
        self.width, self.height = terminal_size()
        self.current = self._new_grid()
        self.previous = self._new_grid()

    def _new_grid(self):
        return [
            [(" ", None, None, False, False) for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def resize(self) -> bool:
        new_w, new_h = terminal_size()
        if new_w != self.width or new_h != self.height:
            self.width, self.height = new_w, new_h
            self.current = self._new_grid()
            self.previous = self._new_grid()
            sys.stdout.write(clear_screen())
            sys.stdout.flush()
            return True
        return False

    def put(
        self,
        x: int,
        y: int,
        char: str,
        fg: tuple | None = None,
        bg: tuple | None = None,
        is_bold: bool = False,
        is_dim: bool = False,
    ) -> None:
        if 0 <= y < self.height and 0 <= x < self.width:
            self.current[y][x] = (char, fg, bg, is_bold, is_dim)

    def write(
        self,
        x: int,
        y: int,
        text: str,
        fg: tuple | None = None,
        bg: tuple | None = None,
        is_bold: bool = False,
        is_dim: bool = False,
    ) -> None:
        for i, char in enumerate(text):
            self.put(x + i, y, char, fg, bg, is_bold, is_dim)

    def clear_line(self, y: int) -> None:
        if 0 <= y < self.height:
            for x in range(self.width):
                self.current[y][x] = (" ", None, None, False, False)

    def clear_rect(self, x: int, y: int, w: int, h: int) -> None:
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            row = self.current[yy]
            for xx in range(x0, x1):
                row[xx] = (" ", None, None, False, False)

    def flush(self) -> None:
        out = []
        l_fg, l_bg, l_bld, l_dm = None, None, False, False

        for y in range(self.height):
            jump = True
            for x in range(self.width):
                curr = self.current[y][x]
                prev = self.previous[y][x]

                if curr != prev:
                    if jump:
                        out.append(move_cursor(y + 1, x + 1))
                        jump = False

                    char, fg, bg, bld, dm = curr
                    if fg != l_fg or bg != l_bg or bld != l_bld or dm != l_dm:
                        out.append(reset_ansi())
                        if fg:
                            out.append(fg_rgb(*fg))
                        if bg:
                            out.append(bg_rgb(*bg))
                        if bld:
                            out.append(bold())
                        if dm:
                            out.append(dim())
                        l_fg, l_bg, l_bld, l_dm = fg, bg, bld, dm
                    out.append(char)
                else:
                    jump = True

        if out:
            sys.stdout.write("".join(out))
            sys.stdout.flush()

        for y in range(self.height):
            self.previous[y][:] = self.current[y][:]

    def clear(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.current[y][x] = (" ", None, None, False, False)


class FrameTimer:
    def __init__(self, fps: int = 60) -> None:
        self._interval = 1.0 / max(fps, 1)
        self._last = time.perf_counter()

    def tick(self) -> float:
        now = time.perf_counter()
        elapsed = now - self._last
        sleep_time = self._interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        dt = time.perf_counter() - self._last
        self._last = time.perf_counter()
        return dt


def format_time(seconds: float) -> str:
    s = int(seconds)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
