"""Tests for rubui.parser."""

import pytest

from rubui.parser import ParseError, parse, validate


class TestParse:
    """Test the notation parser."""

    def test_single_move(self):
        assert parse("R") == ["R"]

    def test_multiple_moves(self):
        assert parse("R U R' U'") == ["R", "U", "R'", "U'"]

    def test_double_moves(self):
        assert parse("R2 U2 F2") == ["R2", "U2", "F2"]

    def test_all_basic_moves(self):
        notation = "R R' R2 L L' L2 U U' U2 D D' D2 F F' F2 B B' B2"
        result = parse(notation)
        assert len(result) == 18

    def test_rotations(self):
        assert parse("x y z x' y' z'") == ["x", "y", "z", "x'", "y'", "z'"]

    def test_mixed_moves_and_rotations(self):
        result = parse("x R U R' y")
        assert result == ["x", "R", "U", "R'", "y"]

    def test_empty_string(self):
        assert parse("") == []

    def test_whitespace_only(self):
        assert parse("   ") == []

    def test_extra_whitespace(self):
        assert parse("  R   U   R'  ") == ["R", "U", "R'"]

    def test_unicode_prime(self):
        # Test with Unicode right single quotation mark
        assert parse("R\u2019") == ["R'"]

    def test_invalid_move_raises(self):
        with pytest.raises(ParseError) as exc_info:
            parse("R X U")
        assert exc_info.value.token == "X"

    def test_invalid_move_message(self):
        with pytest.raises(ParseError, match="Invalid move"):
            parse("HELLO")

    def test_partial_invalid(self):
        with pytest.raises(ParseError):
            parse("R U Z3 F")


class TestValidate:
    """Test the validate helper."""

    def test_valid_notation(self):
        ok, err = validate("R U R' U'")
        assert ok is True
        assert err == ""

    def test_invalid_notation(self):
        ok, err = validate("R X")
        assert ok is False
        assert "Invalid" in err or "X" in err

    def test_empty_is_valid(self):
        ok, _ = validate("")
        assert ok is True
