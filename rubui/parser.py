"""
rubui.parser
~~~~~~~~~~~~
Parse and validate standard Rubik's Cube notation strings.

Accepted tokens:
    R L U D F B        – face moves (clockwise)
    R' L' U' D' F' B'  – prime moves (counter-clockwise)
    R2 L2 U2 D2 F2 B2  – double moves
    x y z x' y' z'     – whole-cube rotations
"""

from __future__ import annotations

from rubui.moves import MOVE_TABLE

VALID_MOVES = frozenset(MOVE_TABLE.keys())


class ParseError(Exception):
    """Raised when the move notation cannot be parsed."""

    def __init__(self, token: str, message: str | None = None) -> None:
        self.token = token
        msg = message or f"Invalid move notation: {token!r}"
        super().__init__(msg)


def parse(notation: str) -> list[str]:
    """Parse a space-separated move string into a list of canonical tokens.

    Parameters
    ----------
    notation : str
        E.g. ``"R U R' U'"`` or ``"F2 D L' U2 x y"``.

    Returns
    -------
    list[str]
        List of validated move tokens.

    Raises
    ------
    ParseError
        If any token is not a recognised move.
    """
    if not notation or not notation.strip():
        return []

    tokens: list[str] = []
    for raw in notation.strip().split():
        # Normalise unicode primes (′ → ')
        token = raw.replace("\u2019", "'").replace("\u2018", "'").replace("\u0060", "'")
        if token not in VALID_MOVES:
            raise ParseError(token)
        tokens.append(token)
    return tokens


def validate(notation: str) -> tuple[bool, str]:
    """Validate notation and return (ok, error_message)."""
    try:
        parse(notation)
        return True, ""
    except ParseError as exc:
        return False, str(exc)
