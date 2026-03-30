"""Tests for rubui.moves — validates correctness of every move."""

import pytest

from rubui.cube_engine import Cube
from rubui.moves import INVERSE_MOVE, MOVE_TABLE, apply_move, redo, undo


class TestMoveIdentity:
    """Applying a move 4 times should return to the identity (original state)."""

    @pytest.mark.parametrize(
        "move",
        [
            "R",
            "L",
            "U",
            "D",
            "F",
            "B",
            "R'",
            "L'",
            "U'",
            "D'",
            "F'",
            "B'",
            "x",
            "x'",
            "y",
            "y'",
            "z",
            "z'",
        ],
    )
    def test_four_moves_identity(self, move):
        cube = Cube()
        original = cube.copy_state()
        for _ in range(4):
            apply_move(cube, move, record=False)
        assert cube.state == original, f"{move} × 4 ≠ identity"


class TestMoveInverse:
    """Applying a move then its inverse should return to the original state."""

    @pytest.mark.parametrize(
        "move",
        [
            "R",
            "L",
            "U",
            "D",
            "F",
            "B",
            "R'",
            "L'",
            "U'",
            "D'",
            "F'",
            "B'",
            "x",
            "x'",
            "y",
            "y'",
            "z",
            "z'",
        ],
    )
    def test_move_inverse(self, move):
        cube = Cube()
        original = cube.copy_state()
        apply_move(cube, move, record=False)
        apply_move(cube, INVERSE_MOVE[move], record=False)
        assert cube.state == original, f"{move} then {INVERSE_MOVE[move]} ≠ identity"


class TestDoubleMoves:
    """Double moves must equal two single moves."""

    @pytest.mark.parametrize("base", ["R", "L", "U", "D", "F", "B"])
    def test_double_equals_twice(self, base):
        c1 = Cube()
        c2 = Cube()
        apply_move(c1, f"{base}2", record=False)
        apply_move(c2, base, record=False)
        apply_move(c2, base, record=False)
        assert c1.state == c2.state, f"{base}2 ≠ {base}+{base}"

    @pytest.mark.parametrize("base", ["R", "L", "U", "D", "F", "B"])
    def test_double_move_twice_is_identity(self, base):
        cube = Cube()
        original = cube.copy_state()
        apply_move(cube, f"{base}2", record=False)
        apply_move(cube, f"{base}2", record=False)
        assert cube.state == original, f"{base}2 × 2 ≠ identity"


class TestMoveValidity:
    """After any move, the cube must have exactly 9 stickers per colour."""

    @pytest.mark.parametrize("move", list(MOVE_TABLE.keys()))
    def test_sticker_count_preserved(self, move):
        cube = Cube()
        apply_move(cube, move, record=False)
        all_stickers = []
        for stickers in cube.state.values():
            all_stickers.extend(stickers)
        assert len(all_stickers) == 54
        for color in "WYGROB":
            assert all_stickers.count(color) == 9, (
                f"After {move}: colour {color} has {all_stickers.count(color)} stickers"
            )


class TestSpecificMoves:
    """Test a few specific known move results."""

    def test_R_moves_specific_stickers(self):
        cube = Cube()
        apply_move(cube, "R", record=False)
        # After R, U's right column should now have F's right column colours
        # F right col was G G G → U right col should be G G G now
        assert cube.state["U"][2] == "G"
        assert cube.state["U"][5] == "G"
        assert cube.state["U"][8] == "G"

    def test_superflip_is_not_solved(self):
        """The superflip is a well-known sequence that produces a valid non-solved state."""
        cube = Cube()
        # Apply a known scramble
        seq = "R U R' U' R U2 R' U'".split()
        for m in seq:
            apply_move(cube, m, record=False)
        # Should not be solved after a non-trivial sequence
        assert not cube.is_solved()


class TestUndoRedo:
    """Test undo/redo through the moves module."""

    def test_undo_single_move(self):
        cube = Cube()
        original = cube.copy_state()
        apply_move(cube, "R")
        assert not cube.is_solved() or cube.state != original
        undone = undo(cube)
        assert undone == "R"
        assert cube.state == original

    def test_redo_after_undo(self):
        cube = Cube()
        apply_move(cube, "R")
        after_R = cube.copy_state()
        undo(cube)
        redone = redo(cube)
        assert redone == "R"
        assert cube.state == after_R

    def test_undo_multiple(self):
        cube = Cube()
        original = cube.copy_state()
        apply_move(cube, "R")
        apply_move(cube, "U")
        apply_move(cube, "F")
        for _ in range(3):
            undo(cube)
        assert cube.state == original

    def test_undo_empty(self):
        cube = Cube()
        assert undo(cube) is None

    def test_redo_empty(self):
        cube = Cube()
        assert redo(cube) is None


class TestUnknownMove:
    """Applying an unknown move must raise ValueError."""

    def test_unknown_raises(self):
        cube = Cube()
        with pytest.raises(ValueError, match="Unknown move"):
            apply_move(cube, "Z99")


class TestRecordFlag:
    """The record flag should control history recording."""

    def test_no_record(self):
        cube = Cube()
        apply_move(cube, "R", record=False)
        assert cube.move_count == 0

    def test_with_record(self):
        cube = Cube()
        apply_move(cube, "R", record=True)
        assert cube.move_count == 1
