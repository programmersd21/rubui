"""
rubui.cube_engine
~~~~~~~~~~~~~~~~~
Core 3×3 Rubik's Cube state representation.

The cube is stored as a dict mapping face names to a flat list of 9 stickers
in row‑major order (index 0 = top‑left, index 8 = bottom‑right):

    0 1 2
    3 4 5
    6 7 8

Face names: U (Up/White), D (Down/Yellow), F (Front/Green),
            B (Back/Blue), L (Left/Orange), R (Right/Red)
"""

from __future__ import annotations

import copy
import random
from typing import Optional

# ── colour labels ──────────────────────────────────────────────────────────
FACE_COLORS = {
    "U": "W",  # White
    "D": "Y",  # Yellow
    "F": "G",  # Green
    "B": "B",  # Blue
    "L": "O",  # Orange
    "R": "R",  # Red
}

FACES = ("U", "D", "F", "B", "L", "R")

# All valid single moves (used by scramble generator)
BASIC_MOVES = [
    "R",
    "R'",
    "R2",
    "L",
    "L'",
    "L2",
    "U",
    "U'",
    "U2",
    "D",
    "D'",
    "D2",
    "F",
    "F'",
    "F2",
    "B",
    "B'",
    "B2",
]


class Cube:
    """A 3×3 Rubik's Cube simulation."""

    __slots__ = ("state", "_history", "_redo_stack")

    def __init__(self) -> None:
        self.state: dict[str, list[str]] = self._solved_state()
        self._history: list[str] = []
        self._redo_stack: list[str] = []

    # ── factories ──────────────────────────────────────────────────────
    @staticmethod
    def _solved_state() -> dict[str, list[str]]:
        return {face: [FACE_COLORS[face]] * 9 for face in FACES}

    def reset(self) -> None:
        """Restore the cube to the solved state."""
        self.state = self._solved_state()
        self._history.clear()
        self._redo_stack.clear()

    # ── queries ────────────────────────────────────────────────────────
    def is_solved(self) -> bool:
        return all(len(set(stickers)) == 1 for stickers in self.state.values())

    def copy_state(self) -> dict[str, list[str]]:
        return copy.deepcopy(self.state)

    def load_state(self, state: dict[str, list[str]]) -> None:
        self.state = copy.deepcopy(state)

    # ── move history ───────────────────────────────────────────────────
    @property
    def move_count(self) -> int:
        return len(self._history)

    @property
    def history(self) -> list[str]:
        return list(self._history)

    def record_move(self, move: str) -> None:
        """Record a move into history and clear the redo stack."""
        self._history.append(move)
        self._redo_stack.clear()

    def pop_history(self) -> Optional[str]:
        """Pop the last move from history for undo (returns the move name)."""
        if self._history:
            move = self._history.pop()
            self._redo_stack.append(move)
            return move
        return None

    def pop_redo(self) -> Optional[str]:
        """Pop a move from the redo stack."""
        if self._redo_stack:
            move = self._redo_stack.pop()
            self._history.append(move)
            return move
        return None

    # ── scramble ───────────────────────────────────────────────────────
    def scramble(
        self,
        length: int = 25,
        seed: Optional[int] = None,
        apply_moves_fn=None,
    ) -> list[str]:
        """Generate and optionally apply a scramble sequence.

        Parameters
        ----------
        length : int
            Number of random moves.
        seed : int | None
            If provided, makes the scramble deterministic.
        apply_moves_fn : callable | None
            A function ``(cube, move_name) -> None`` that applies a single
            move.  Passed in to avoid a circular import with ``moves.py``.

        Returns
        -------
        list[str]  – the generated scramble sequence
        """
        rng = random.Random(seed)
        seq: list[str] = []
        prev = ""
        for _ in range(length):
            # Avoid consecutive moves on the same face
            candidates = [m for m in BASIC_MOVES if m[0] != prev[:1]]
            move = rng.choice(candidates) if candidates else rng.choice(BASIC_MOVES)
            seq.append(move)
            prev = move
        if apply_moves_fn is not None:
            for m in seq:
                apply_moves_fn(self, m)
        return seq

    # ── helpers for moves.py ───────────────────────────────────────────
    def rotate_face_cw(self, face: str) -> None:
        """Rotate a face 90 ° clockwise (stickers only, no adjacent rows)."""
        f = self.state[face]
        self.state[face] = [
            f[6],
            f[3],
            f[0],
            f[7],
            f[4],
            f[1],
            f[8],
            f[5],
            f[2],
        ]

    def rotate_face_ccw(self, face: str) -> None:
        """Rotate a face 90 ° counter‑clockwise."""
        f = self.state[face]
        self.state[face] = [
            f[2],
            f[5],
            f[8],
            f[1],
            f[4],
            f[7],
            f[0],
            f[3],
            f[6],
        ]

    def rotate_face_180(self, face: str) -> None:
        """Rotate a face 180 °."""
        f = self.state[face]
        self.state[face] = [
            f[8],
            f[7],
            f[6],
            f[5],
            f[4],
            f[3],
            f[2],
            f[1],
            f[0],
        ]

    # ── dunder ─────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"Cube(solved={self.is_solved()}, moves={self.move_count})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cube):
            return NotImplemented
        return self.state == other.state
