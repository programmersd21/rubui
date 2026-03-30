"""
rubui.manual_mode
~~~~~~~~~~~~~~~~~
Interactive manual mode — the default mode of rubui.
"""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

from rubui.cube_engine import Cube
from rubui.input_handler import HELP_TEXT, InputHandler, kbhit
from rubui.moves import apply_move, redo, undo
from rubui.parser import ParseError, parse
from rubui.renderer import AnimationState, draw_frame, render_banner
from rubui.solver import solve_cube
from rubui.utils import (
    FrameTimer,
    TerminalBuffer,
    clear_screen,
    enter_alt_screen,
    exit_alt_screen,
    hide_cursor,
    reset_ansi,
    show_cursor,
)

if TYPE_CHECKING:
    from rubui.config import AppConfig


def _animate_move(
    cube: Cube,
    move_name: str,
    *,
    config: "AppConfig",
    buffer: TerminalBuffer,
    start_time: float,
    use_color: bool,
) -> None:
    frames = max(6, int(config.fps * 0.12))
    frame_delay = 1.0 / max(config.fps, 30)
    pre_state = cube.copy_state()

    for i in range(frames):
        progress = (i + 1) / frames
        elapsed = time.perf_counter() - start_time
        anim = AnimationState(move=move_name, progress=progress, pre_state=pre_state)
        draw_frame(
            buffer,
            cube,
            mode="manual",
            move_count=cube.move_count,
            elapsed=elapsed,
            theme_name=config.theme,
            fps=config.fps,
            use_color=use_color,
            last_move=move_name,
            animation=anim,
            size=config.size,
        )
        buffer.flush()
        time.sleep(frame_delay)

    apply_move(cube, move_name, record=True)


def _solve_with_kociemba(
    cube: Cube,
    *,
    config: "AppConfig",
    buffer: TerminalBuffer,
    start_time: float,
    use_color: bool,
) -> str:
    try:
        moves = solve_cube(cube)
    except Exception as exc:
        return f"Solver error: {exc}"

    if not moves:
        return "Already solved"

    for move_name in moves:
        _animate_move(
            cube,
            move_name,
            config=config,
            buffer=buffer,
            start_time=start_time,
            use_color=use_color,
        )
    return "Solved"


def run(config: "AppConfig") -> None:
    """Run the manual mode main loop."""
    cube = Cube()
    use_color = config.color
    input_handler = InputHandler()
    timer = FrameTimer(fps=config.fps)
    show_help = False
    last_move = ""
    buffer = TerminalBuffer()

    if config.scramble_on_start:
        cube.scramble(
            length=config.scramble_length,
            seed=config.scramble_seed,
            apply_moves_fn=lambda c, m: apply_move(c, m, record=False),
        )

    sys.stdout.write(enter_alt_screen() + hide_cursor() + clear_screen())
    sys.stdout.flush()

    render_banner(use_color=use_color)

    if sys.platform != "win32":
        from rubui.input_handler import _init_raw

        _init_raw()

    start_time = time.perf_counter()

    if config.solve_on_start:
        last_move = _solve_with_kociemba(
            cube,
            config=config,
            buffer=buffer,
            start_time=start_time,
            use_color=use_color,
        )

    try:
        while True:
            buffer.resize()
            elapsed = time.perf_counter() - start_time

            if show_help:
                y = 2
                for line in HELP_TEXT.split("\n"):
                    buffer.clear_line(y)
                    if use_color:
                        buffer.write(2, y, line, fg=(180, 190, 210))
                    else:
                        buffer.write(2, y, line)
                    y += 1
                buffer.write(
                    2,
                    y + 1,
                    "Press Esc or any key to close help...",
                    fg=(137, 180, 250),
                )
            else:
                draw_frame(
                    buffer,
                    cube,
                    mode="manual",
                    move_count=cube.move_count,
                    elapsed=elapsed,
                    theme_name=config.theme,
                    fps=config.fps,
                    use_color=use_color,
                    command_line=(
                        input_handler.command_buffer
                        if input_handler.in_command_mode
                        else ""
                    ),
                    last_move=last_move,
                    size=config.size,
                )

            buffer.flush()

            # ── Input ──
            if sys.platform == "win32":
                import msvcrt

                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ("\x00", "\xe0"):
                        ch2 = msvcrt.getwch()
                        arrow_map = {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}
                        key = arrow_map.get(ch2, "")
                else:
                    timer.tick()
                    continue
            else:
                from rubui.input_handler import _getch_raw

                key = _getch_raw()
                if key is None:
                    timer.tick()
                    continue
                if key == "\x1b":
                    if kbhit():
                        nxt = _getch_raw()
                        if nxt == "[" and kbhit():
                            nxt2 = _getch_raw()
                            arrow_map = {
                                "A": "UP",
                                "B": "DOWN",
                                "C": "RIGHT",
                                "D": "LEFT",
                            }
                            key = arrow_map.get(nxt2, "")
                        else:
                            key = ""

            if show_help:
                show_help = False
                buffer.clear()
                continue

            result = input_handler.process_key(key)
            action = result["action"]

            if action == "quit":
                break
            if action == "move":
                move_name = result["move"]
                if result.get("replace_last"):
                    undo(cube)
                last_move = move_name
                _animate_move(
                    cube,
                    move_name,
                    config=config,
                    buffer=buffer,
                    start_time=start_time,
                    use_color=use_color,
                )
            elif action == "scramble":
                cube.scramble(
                    length=config.scramble_length,
                    seed=None,
                    apply_moves_fn=lambda c, m: apply_move(c, m, record=True),
                )
                last_move = "Scrambled!"
            elif action == "undo":
                undone = undo(cube)
                last_move = f"Undo {undone}" if undone else "Nothing to undo"
            elif action == "redo":
                redone = redo(cube)
                last_move = f"Redo {redone}" if redone else "Nothing to redo"
            elif action == "help":
                show_help = True
            elif action == "command_submit":
                cmd = result["command"].strip()
                if cmd:
                    try:
                        moves = parse(cmd)
                        for m in moves:
                            _animate_move(
                                cube,
                                m,
                                config=config,
                                buffer=buffer,
                                start_time=start_time,
                                use_color=use_color,
                            )
                        last_move = cmd
                    except ParseError as e:
                        last_move = f"Error: {e}"
            elif action == "solve":
                last_move = _solve_with_kociemba(
                    cube,
                    config=config,
                    buffer=buffer,
                    start_time=start_time,
                    use_color=use_color,
                )
            elif action == "mode_switch":
                from rubui.auto_mode import run as auto_run

                auto_run(config)
                start_time = time.perf_counter()

            timer.tick()

    except KeyboardInterrupt:
        pass
    finally:
        if sys.platform != "win32":
            from rubui.input_handler import _restore

            _restore()
        sys.stdout.write(show_cursor() + exit_alt_screen() + reset_ansi())
        sys.stdout.flush()
