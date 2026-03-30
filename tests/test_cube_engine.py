"""Tests for rubui.cube_engine."""

from rubui.cube_engine import FACE_COLORS, FACES, Cube


class TestCubeSolvedState:
    """Test the solved state factory and is_solved()."""

    def test_new_cube_is_solved(self):
        cube = Cube()
        assert cube.is_solved()

    def test_solved_state_has_correct_colors(self):
        cube = Cube()
        for face in FACES:
            expected = FACE_COLORS[face]
            assert all(s == expected for s in cube.state[face])

    def test_each_face_has_9_stickers(self):
        cube = Cube()
        for face in FACES:
            assert len(cube.state[face]) == 9

    def test_reset_restores_solved(self):
        cube = Cube()
        # Manually break the state
        cube.state["U"][0] = "R"
        assert not cube.is_solved()
        cube.reset()
        assert cube.is_solved()


class TestCubeStateManagement:
    """Test state copy, load, and equality."""

    def test_copy_state_is_independent(self):
        cube = Cube()
        state_copy = cube.copy_state()
        state_copy["U"][0] = "X"
        assert cube.state["U"][0] != "X"

    def test_load_state(self):
        cube = Cube()
        cube.state["F"][4] = "R"
        saved = cube.copy_state()
        cube.reset()
        assert cube.is_solved()
        cube.load_state(saved)
        assert cube.state["F"][4] == "R"

    def test_cube_equality(self):
        a = Cube()
        b = Cube()
        assert a == b
        a.state["U"][0] = "R"
        assert a != b

    def test_repr(self):
        cube = Cube()
        r = repr(cube)
        assert "solved=True" in r
        assert "moves=0" in r


class TestCubeHistory:
    """Test move history, undo stack, redo stack."""

    def test_initial_move_count_zero(self):
        cube = Cube()
        assert cube.move_count == 0

    def test_record_move(self):
        cube = Cube()
        cube.record_move("R")
        cube.record_move("U")
        assert cube.move_count == 2
        assert cube.history == ["R", "U"]

    def test_pop_history(self):
        cube = Cube()
        cube.record_move("R")
        cube.record_move("U")
        move = cube.pop_history()
        assert move == "U"
        assert cube.move_count == 1

    def test_pop_redo(self):
        cube = Cube()
        cube.record_move("R")
        cube.pop_history()
        move = cube.pop_redo()
        assert move == "R"
        assert cube.move_count == 1

    def test_pop_history_empty(self):
        cube = Cube()
        assert cube.pop_history() is None

    def test_pop_redo_empty(self):
        cube = Cube()
        assert cube.pop_redo() is None

    def test_record_clears_redo(self):
        cube = Cube()
        cube.record_move("R")
        cube.pop_history()
        cube.record_move("L")
        assert cube.pop_redo() is None


class TestScramble:
    """Test scramble generation."""

    def test_scramble_returns_moves(self):
        cube = Cube()
        seq = cube.scramble(length=10)
        assert len(seq) == 10

    def test_scramble_with_seed_deterministic(self):
        c1 = Cube()
        c2 = Cube()
        s1 = c1.scramble(length=20, seed=42)
        s2 = c2.scramble(length=20, seed=42)
        assert s1 == s2

    def test_scramble_different_seeds_differ(self):
        c1 = Cube()
        c2 = Cube()
        s1 = c1.scramble(length=20, seed=1)
        s2 = c2.scramble(length=20, seed=2)
        assert s1 != s2

    def test_scramble_avoids_same_face(self):
        cube = Cube()
        seq = cube.scramble(length=50, seed=99)
        for i in range(1, len(seq)):
            # First char is face letter
            assert seq[i][0] != seq[i - 1][0]

    def test_scramble_with_apply(self):
        from rubui.moves import apply_move

        cube = Cube()
        cube.scramble(
            length=25,
            seed=42,
            apply_moves_fn=lambda c, m: apply_move(c, m, record=False),
        )
        assert not cube.is_solved()
