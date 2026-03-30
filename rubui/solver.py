"""
rubui.solver
~~~~~~~~~~~~
Kociemba-based solver integration.
"""

from __future__ import annotations

from rubui.cube_engine import Cube

FACELET_ORDER = ("U", "R", "F", "D", "L", "B")


def _color_to_face_map(cube: Cube) -> dict[str, str]:
    state = cube.state
    return {
        state["U"][4]: "U",
        state["R"][4]: "R",
        state["F"][4]: "F",
        state["D"][4]: "D",
        state["L"][4]: "L",
        state["B"][4]: "B",
    }


def cube_to_facelets(cube: Cube) -> str:
    """Convert cube state into a Kociemba facelet string (URFDLB order)."""
    color_map = _color_to_face_map(cube)
    facelets: list[str] = []
    for face in FACELET_ORDER:
        for sticker in cube.state[face]:
            facelet = color_map.get(sticker)
            if facelet is None:
                raise ValueError(f"Unknown sticker color: {sticker!r}")
            facelets.append(facelet)
    return "".join(facelets)


def solve_cube(cube: Cube) -> list[str]:
    """Return a list of moves that solve the cube using kociemba."""
    try:
        import kociemba  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError(
            "kociemba package not installed. Install with: pip install kociemba"
        ) from exc

    facelets = cube_to_facelets(cube)
    solution = kociemba.solve(facelets)
    if not solution:
        return []
    return solution.split()
