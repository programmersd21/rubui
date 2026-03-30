"""
rubui.auto_mode
~~~~~~~~~~~~~~~
Animated screensaver mode for rubui.
"""

from __future__ import annotations

import random
import sys
import time
from typing import TYPE_CHECKING

from rubui.cube_engine import Cube
from rubui.moves import MOVE_TABLE, apply_move
from rubui.renderer import AnimationState, draw_frame
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
    pre_state = cube.copy_state()
    frames = max(6, int(config.fps * 0.12))
    frame_delay = 1.0 / max(config.fps, 30)
    for i in range(frames):
        progress = (i + 1) / frames
        elapsed = time.perf_counter() - start_time
        anim = AnimationState(move=move_name, progress=progress, pre_state=pre_state)
        draw_frame(
            buffer,
            cube,
            mode="auto",
            move_count=cube.move_count,
            elapsed=elapsed,
            theme_name=config.theme,
            fps=config.fps,
            speed=config.speed,
            use_color=use_color,
            last_move=move_name,
            animation=anim,
            size=config.size,
        )
        buffer.flush()
        time.sleep(frame_delay)

    apply_move(cube, move_name, record=True)
    # Final static frame to avoid any rounding gaps at progress=1.0
    elapsed = time.perf_counter() - start_time
    draw_frame(
        buffer,
        cube,
        mode="auto",
        move_count=cube.move_count,
        elapsed=elapsed,
        theme_name=config.theme,
        fps=config.fps,
        speed=config.speed,
        use_color=use_color,
        last_move=move_name,
        size=config.size,
    )
    buffer.flush()


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
    cube = Cube()
    use_color = config.color
    timer = FrameTimer(fps=config.fps)
    buffer = TerminalBuffer()

    sys.stdout.write(enter_alt_screen() + hide_cursor() + clear_screen())
    sys.stdout.flush()

    start_time = time.perf_counter()
    last_move = ""
    move_list = list(MOVE_TABLE.keys())

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
            move_name = random.choice(move_list)
            last_move = move_name
            _animate_move(
                cube,
                move_name,
                config=config,
                buffer=buffer,
                start_time=start_time,
                use_color=use_color,
            )

            time.sleep(config.speed)

            if sys.platform == "win32":
                import msvcrt

                if msvcrt.kbhit():
                    if msvcrt.getwch() in ("q", "Q", "\x1b"):
                        break

            timer.tick()

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(show_cursor() + exit_alt_screen() + reset_ansi())
        sys.stdout.flush()
