"""
rubui.moves
~~~~~~~~~~~
Corrected official Rubik's Cube moves.
Every move follows official Singmaster notation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rubui.cube_engine import Cube

# ── Face moves ─────────────────────────────────────────────────────────────


def move_R(cube: Cube) -> None:
    cube.rotate_face_cw("R")
    s = cube.state
    # F[2,5,8], U[2,5,8], B[6,3,0], D[2,5,8]
    f2, f5, f8 = s["F"][2], s["F"][5], s["F"][8]
    s["F"][2], s["F"][5], s["F"][8] = s["D"][2], s["D"][5], s["D"][8]
    s["D"][2], s["D"][5], s["D"][8] = s["B"][6], s["B"][3], s["B"][0]
    s["B"][6], s["B"][3], s["B"][0] = s["U"][2], s["U"][5], s["U"][8]
    s["U"][2], s["U"][5], s["U"][8] = f2, f5, f8


def move_R_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("R")
    s = cube.state
    f2, f5, f8 = s["F"][2], s["F"][5], s["F"][8]
    s["F"][2], s["F"][5], s["F"][8] = s["U"][2], s["U"][5], s["U"][8]
    s["U"][2], s["U"][5], s["U"][8] = s["B"][6], s["B"][3], s["B"][0]
    s["B"][6], s["B"][3], s["B"][0] = s["D"][2], s["D"][5], s["D"][8]
    s["D"][2], s["D"][5], s["D"][8] = f2, f5, f8


def move_L(cube: Cube) -> None:
    cube.rotate_face_cw("L")
    s = cube.state
    # F[0,3,6], U[0,3,6], B[8,5,2], D[0,3,6]
    f0, f3, f6 = s["F"][0], s["F"][3], s["F"][6]
    s["F"][0], s["F"][3], s["F"][6] = s["U"][0], s["U"][3], s["U"][6]
    s["U"][0], s["U"][3], s["U"][6] = s["B"][8], s["B"][5], s["B"][2]
    s["B"][8], s["B"][5], s["B"][2] = s["D"][0], s["D"][3], s["D"][6]
    s["D"][0], s["D"][3], s["D"][6] = f0, f3, f6


def move_L_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("L")
    s = cube.state
    f0, f3, f6 = s["F"][0], s["F"][3], s["F"][6]
    s["F"][0], s["F"][3], s["F"][6] = s["D"][0], s["D"][3], s["D"][6]
    s["D"][0], s["D"][3], s["D"][6] = s["B"][8], s["B"][5], s["B"][2]
    s["B"][8], s["B"][5], s["B"][2] = s["U"][0], s["U"][3], s["U"][6]
    s["U"][0], s["U"][3], s["U"][6] = f0, f3, f6


def move_U(cube: Cube) -> None:
    cube.rotate_face_cw("U")
    s = cube.state
    f0, f1, f2 = s["F"][0], s["F"][1], s["F"][2]
    s["F"][0], s["F"][1], s["F"][2] = s["R"][0], s["R"][1], s["R"][2]
    s["R"][0], s["R"][1], s["R"][2] = s["B"][0], s["B"][1], s["B"][2]
    s["B"][0], s["B"][1], s["B"][2] = s["L"][0], s["L"][1], s["L"][2]
    s["L"][0], s["L"][1], s["L"][2] = f0, f1, f2


def move_U_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("U")
    s = cube.state
    f0, f1, f2 = s["F"][0], s["F"][1], s["F"][2]
    s["F"][0], s["F"][1], s["F"][2] = s["L"][0], s["L"][1], s["L"][2]
    s["L"][0], s["L"][1], s["L"][2] = s["B"][0], s["B"][1], s["B"][2]
    s["B"][0], s["B"][1], s["B"][2] = s["R"][0], s["R"][1], s["R"][2]
    s["R"][0], s["R"][1], s["R"][2] = f0, f1, f2


def move_D(cube: Cube) -> None:
    cube.rotate_face_cw("D")
    s = cube.state
    f6, f7, f8 = s["F"][6], s["F"][7], s["F"][8]
    s["F"][6], s["F"][7], s["F"][8] = s["L"][6], s["L"][7], s["L"][8]
    s["L"][6], s["L"][7], s["L"][8] = s["B"][6], s["B"][7], s["B"][8]
    s["B"][6], s["B"][7], s["B"][8] = s["R"][6], s["R"][7], s["R"][8]
    s["R"][6], s["R"][7], s["R"][8] = f6, f7, f8


def move_D_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("D")
    s = cube.state
    f6, f7, f8 = s["F"][6], s["F"][7], s["F"][8]
    s["F"][6], s["F"][7], s["F"][8] = s["R"][6], s["R"][7], s["R"][8]
    s["R"][6], s["R"][7], s["R"][8] = s["B"][6], s["B"][7], s["B"][8]
    s["B"][6], s["B"][7], s["B"][8] = s["L"][6], s["L"][7], s["L"][8]
    s["L"][6], s["L"][7], s["L"][8] = f6, f7, f8


def move_F(cube: Cube) -> None:
    cube.rotate_face_cw("F")
    s = cube.state
    # U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]
    u6, u7, u8 = s["U"][6], s["U"][7], s["U"][8]
    s["U"][6], s["U"][7], s["U"][8] = s["L"][8], s["L"][5], s["L"][2]
    s["L"][8], s["L"][5], s["L"][2] = s["D"][2], s["D"][1], s["D"][0]
    s["D"][2], s["D"][1], s["D"][0] = s["R"][0], s["R"][3], s["R"][6]
    s["R"][0], s["R"][3], s["R"][6] = u6, u7, u8


def move_F_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("F")
    s = cube.state
    u6, u7, u8 = s["U"][6], s["U"][7], s["U"][8]
    s["U"][6], s["U"][7], s["U"][8] = s["R"][0], s["R"][3], s["R"][6]
    s["R"][0], s["R"][3], s["R"][6] = s["D"][2], s["D"][1], s["D"][0]
    s["D"][2], s["D"][1], s["D"][0] = s["L"][8], s["L"][5], s["L"][2]
    s["L"][8], s["L"][5], s["L"][2] = u6, u7, u8


def move_B(cube: Cube) -> None:
    cube.rotate_face_cw("B")
    s = cube.state
    # U[2,1,0], L[0,3,6], D[6,7,8], R[8,5,2]
    u0, u1, u2 = s["U"][0], s["U"][1], s["U"][2]
    s["U"][0], s["U"][1], s["U"][2] = s["R"][2], s["R"][5], s["R"][8]
    s["R"][2], s["R"][5], s["R"][8] = s["D"][8], s["D"][7], s["D"][6]
    s["D"][8], s["D"][7], s["D"][6] = s["L"][6], s["L"][3], s["L"][0]
    s["L"][6], s["L"][3], s["L"][0] = u0, u1, u2


def move_B_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("B")
    s = cube.state
    u0, u1, u2 = s["U"][0], s["U"][1], s["U"][2]
    s["U"][0], s["U"][1], s["U"][2] = s["L"][6], s["L"][3], s["L"][0]
    s["L"][6], s["L"][3], s["L"][0] = s["D"][8], s["D"][7], s["D"][6]
    s["D"][8], s["D"][7], s["D"][6] = s["R"][2], s["R"][5], s["R"][8]
    s["R"][2], s["R"][5], s["R"][8] = u0, u1, u2


# ── Middle layer moves ─────────────────────────────────────────────────────


def move_M(cube: Cube) -> None:
    s = cube.state
    # F[1,4,7], U[1,4,7], B[7,4,1], D[1,4,7]
    f1, f4, f7 = s["F"][1], s["F"][4], s["F"][7]
    s["F"][1], s["F"][4], s["F"][7] = s["U"][1], s["U"][4], s["U"][7]
    s["U"][1], s["U"][4], s["U"][7] = s["B"][7], s["B"][4], s["B"][1]
    s["B"][7], s["B"][4], s["B"][1] = s["D"][1], s["D"][4], s["D"][7]
    s["D"][1], s["D"][4], s["D"][7] = f1, f4, f7


def move_M_prime(cube: Cube) -> None:
    s = cube.state
    f1, f4, f7 = s["F"][1], s["F"][4], s["F"][7]
    s["F"][1], s["F"][4], s["F"][7] = s["D"][1], s["D"][4], s["D"][7]
    s["D"][1], s["D"][4], s["D"][7] = s["B"][7], s["B"][4], s["B"][1]
    s["B"][7], s["B"][4], s["B"][1] = s["U"][1], s["U"][4], s["U"][7]
    s["U"][1], s["U"][4], s["U"][7] = f1, f4, f7


def move_E(cube: Cube) -> None:
    s = cube.state
    f3, f4, f5 = s["F"][3], s["F"][4], s["F"][5]
    s["F"][3], s["F"][4], s["F"][5] = s["L"][3], s["L"][4], s["L"][5]
    s["L"][3], s["L"][4], s["L"][5] = s["B"][3], s["B"][4], s["B"][5]
    s["B"][3], s["B"][4], s["B"][5] = s["R"][3], s["R"][4], s["R"][5]
    s["R"][3], s["R"][4], s["R"][5] = f3, f4, f5


def move_E_prime(cube: Cube) -> None:
    s = cube.state
    f3, f4, f5 = s["F"][3], s["F"][4], s["F"][5]
    s["F"][3], s["F"][4], s["F"][5] = s["R"][3], s["R"][4], s["R"][5]
    s["R"][3], s["R"][4], s["R"][5] = s["B"][3], s["B"][4], s["B"][5]
    s["B"][3], s["B"][4], s["B"][5] = s["L"][3], s["L"][4], s["L"][5]
    s["L"][3], s["L"][4], s["L"][5] = f3, f4, f5


def move_S(cube: Cube) -> None:
    s = cube.state
    u3, u4, u5 = s["U"][3], s["U"][4], s["U"][5]
    s["U"][3], s["U"][4], s["U"][5] = s["L"][7], s["L"][4], s["L"][1]
    s["L"][7], s["L"][4], s["L"][1] = s["D"][5], s["D"][4], s["D"][3]
    s["D"][5], s["D"][4], s["D"][3] = s["R"][1], s["R"][4], s["R"][7]
    s["R"][1], s["R"][4], s["R"][7] = u3, u4, u5


def move_S_prime(cube: Cube) -> None:
    s = cube.state
    u3, u4, u5 = s["U"][3], s["U"][4], s["U"][5]
    s["U"][3], s["U"][4], s["U"][5] = s["R"][1], s["R"][4], s["R"][7]
    s["R"][1], s["R"][4], s["R"][7] = s["D"][5], s["D"][4], s["D"][3]
    s["D"][5], s["D"][4], s["D"][3] = s["L"][7], s["L"][4], s["L"][1]
    s["L"][7], s["L"][4], s["L"][1] = u3, u4, u5


# ── Wide moves ─────────────────────────────────────────────────────────────


def move_Rw(cube: Cube) -> None:
    move_R(cube)
    move_M_prime(cube)


def move_Rw_prime(cube: Cube) -> None:
    move_R_prime(cube)
    move_M(cube)


def move_Lw(cube: Cube) -> None:
    move_L(cube)
    move_M(cube)


def move_Lw_prime(cube: Cube) -> None:
    move_L_prime(cube)
    move_M_prime(cube)


def move_Uw(cube: Cube) -> None:
    move_U(cube)
    move_E_prime(cube)


def move_Uw_prime(cube: Cube) -> None:
    move_U_prime(cube)
    move_E(cube)


def move_Dw(cube: Cube) -> None:
    move_D(cube)
    move_E(cube)


def move_Dw_prime(cube: Cube) -> None:
    move_D_prime(cube)
    move_E_prime(cube)


def move_Fw(cube: Cube) -> None:
    move_F(cube)
    move_S(cube)


def move_Fw_prime(cube: Cube) -> None:
    move_F_prime(cube)
    move_S_prime(cube)


def move_Bw(cube: Cube) -> None:
    move_B(cube)
    move_S_prime(cube)


def move_Bw_prime(cube: Cube) -> None:
    move_B_prime(cube)
    move_S(cube)


# ── Double moves helper ────────────────────────────────────────────────────


def _double(fn):
    def wrapper(cube: Cube):
        fn(cube)
        fn(cube)

    return wrapper


# ── Rotations ──────────────────────────────────────────────────────────────


def rotate_x(cube: Cube) -> None:
    cube.rotate_face_cw("R")
    cube.rotate_face_ccw("L")
    s = cube.state
    tmp_f = list(s["F"])
    s["F"] = list(s["D"])
    s["D"] = [s["B"][8 - i] for i in range(9)]
    s["B"] = [s["U"][8 - i] for i in range(9)]
    s["U"] = tmp_f


def rotate_x_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("R")
    cube.rotate_face_cw("L")
    s = cube.state
    tmp_f = list(s["F"])
    s["F"] = list(s["U"])
    s["U"] = [s["B"][8 - i] for i in range(9)]
    s["B"] = [s["D"][8 - i] for i in range(9)]
    s["D"] = tmp_f


def rotate_y(cube: Cube) -> None:
    cube.rotate_face_cw("U")
    cube.rotate_face_ccw("D")
    s = cube.state
    tmp_f = list(s["F"])
    s["F"] = list(s["R"])
    s["R"] = list(s["B"])
    s["B"] = list(s["L"])
    s["L"] = tmp_f


def rotate_y_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("U")
    cube.rotate_face_cw("D")
    s = cube.state
    tmp_f = list(s["F"])
    s["F"] = list(s["L"])
    s["L"] = list(s["B"])
    s["B"] = list(s["R"])
    s["R"] = tmp_f


def rotate_z(cube: Cube) -> None:
    cube.rotate_face_cw("F")
    cube.rotate_face_ccw("B")
    s = cube.state
    tmp_u = list(s["U"])
    # U gets L rotated CW
    s["U"] = [
        s["L"][6],
        s["L"][3],
        s["L"][0],
        s["L"][7],
        s["L"][4],
        s["L"][1],
        s["L"][8],
        s["L"][5],
        s["L"][2],
    ]
    # L gets D rotated CW
    s["L"] = [
        s["D"][6],
        s["D"][3],
        s["D"][0],
        s["D"][7],
        s["D"][4],
        s["D"][1],
        s["D"][8],
        s["D"][5],
        s["D"][2],
    ]
    # D gets R rotated CW
    s["D"] = [
        s["R"][6],
        s["R"][3],
        s["R"][0],
        s["R"][7],
        s["R"][4],
        s["R"][1],
        s["R"][8],
        s["R"][5],
        s["R"][2],
    ]
    # R gets U rotated CW
    s["R"] = [
        tmp_u[6],
        tmp_u[3],
        tmp_u[0],
        tmp_u[7],
        tmp_u[4],
        tmp_u[1],
        tmp_u[8],
        tmp_u[5],
        tmp_u[2],
    ]


def rotate_z_prime(cube: Cube) -> None:
    cube.rotate_face_ccw("F")
    cube.rotate_face_cw("B")
    s = cube.state
    tmp_u = list(s["U"])
    # U gets R rotated CCW
    s["U"] = [
        s["R"][2],
        s["R"][5],
        s["R"][8],
        s["R"][1],
        s["R"][4],
        s["R"][7],
        s["R"][0],
        s["R"][3],
        s["R"][6],
    ]
    # R gets D rotated CCW
    s["R"] = [
        s["D"][2],
        s["D"][5],
        s["D"][8],
        s["D"][1],
        s["D"][4],
        s["D"][7],
        s["D"][0],
        s["D"][3],
        s["D"][6],
    ]
    # D gets L rotated CCW
    s["D"] = [
        s["L"][2],
        s["L"][5],
        s["L"][8],
        s["L"][1],
        s["L"][4],
        s["L"][7],
        s["L"][0],
        s["L"][3],
        s["L"][6],
    ]
    # L gets U rotated CCW
    s["L"] = [
        tmp_u[2],
        tmp_u[5],
        tmp_u[8],
        tmp_u[1],
        tmp_u[4],
        tmp_u[7],
        tmp_u[0],
        tmp_u[3],
        tmp_u[6],
    ]


# ── Dispatch table ──────────────────────────────────────────────────────────

MOVE_TABLE = {
    "R": move_R,
    "R'": move_R_prime,
    "R2": _double(move_R),
    "L": move_L,
    "L'": move_L_prime,
    "L2": _double(move_L),
    "U": move_U,
    "U'": move_U_prime,
    "U2": _double(move_U),
    "D": move_D,
    "D'": move_D_prime,
    "D2": _double(move_D),
    "F": move_F,
    "F'": move_F_prime,
    "F2": _double(move_F),
    "B": move_B,
    "B'": move_B_prime,
    "B2": _double(move_B),
    "M": move_M,
    "M'": move_M_prime,
    "M2": _double(move_M),
    "E": move_E,
    "E'": move_E_prime,
    "E2": _double(move_E),
    "S": move_S,
    "S'": move_S_prime,
    "S2": _double(move_S),
    "Rw": move_Rw,
    "Rw'": move_Rw_prime,
    "Rw2": _double(move_Rw),
    "Lw": move_Lw,
    "Lw'": move_Lw_prime,
    "Lw2": _double(move_Lw),
    "Uw": move_Uw,
    "Uw'": move_Uw_prime,
    "Uw2": _double(move_Uw),
    "Dw": move_Dw,
    "Dw'": move_Dw_prime,
    "Dw2": _double(move_Dw),
    "Fw": move_Fw,
    "Fw'": move_Fw_prime,
    "Fw2": _double(move_Fw),
    "Bw": move_Bw,
    "Bw'": move_Bw_prime,
    "Bw2": _double(move_Bw),
    "r": move_Rw,
    "r'": move_Rw_prime,
    "r2": _double(move_Rw),
    "l": move_Lw,
    "l'": move_Lw_prime,
    "l2": _double(move_Lw),
    "u": move_Uw,
    "u'": move_Uw_prime,
    "u2": _double(move_Uw),
    "d": move_Dw,
    "d'": move_Dw_prime,
    "d2": _double(move_Dw),
    "f": move_Fw,
    "f'": move_Fw_prime,
    "f2": _double(move_Fw),
    "b": move_Bw,
    "b'": move_Bw_prime,
    "b2": _double(move_Bw),
    "x": rotate_x,
    "x'": rotate_x_prime,
    "x2": _double(rotate_x),
    "y": rotate_y,
    "y'": rotate_y_prime,
    "y2": _double(rotate_y),
    "z": rotate_z,
    "z'": rotate_z_prime,
    "z2": _double(rotate_z),
}

INVERSE_MOVE = {
    "R": "R'",
    "R'": "R",
    "R2": "R2",
    "L": "L'",
    "L'": "L",
    "L2": "L2",
    "U": "U'",
    "U'": "U",
    "U2": "U2",
    "D": "D'",
    "D'": "D",
    "D2": "D2",
    "F": "F'",
    "F'": "F",
    "F2": "F2",
    "B": "B'",
    "B'": "B",
    "B2": "B2",
    "M": "M'",
    "M'": "M",
    "M2": "M2",
    "E": "E'",
    "E'": "E",
    "E2": "E2",
    "S": "S'",
    "S'": "S",
    "S2": "S2",
    "Rw": "Rw'",
    "Rw'": "Rw",
    "Rw2": "Rw2",
    "Lw": "Lw'",
    "Lw'": "Lw",
    "Lw2": "Lw2",
    "Uw": "Uw'",
    "Uw'": "Uw",
    "Uw2": "Uw2",
    "Dw": "Dw'",
    "Dw'": "Dw",
    "Dw2": "Dw2",
    "Fw": "Fw'",
    "Fw'": "Fw",
    "Fw2": "Fw2",
    "Bw": "Bw'",
    "Bw'": "Bw",
    "Bw2": "Bw2",
    "r": "r'",
    "r'": "r",
    "r2": "r2",
    "l": "l'",
    "l'": "l",
    "l2": "l2",
    "u": "u'",
    "u'": "u",
    "u2": "u2",
    "d": "d'",
    "d'": "d",
    "d2": "d2",
    "f": "f'",
    "f'": "f",
    "f2": "f2",
    "b": "b'",
    "b'": "b",
    "b2": "b2",
    "x": "x'",
    "x'": "x",
    "x2": "x2",
    "y": "y'",
    "y'": "y",
    "y2": "y2",
    "z": "z'",
    "z'": "z",
    "z2": "z2",
}


def apply_move(cube: Cube, move_name: str, *, record: bool = True) -> None:
    fn = MOVE_TABLE.get(move_name)
    if not fn:
        raise ValueError(f"Unknown move: {move_name}")
    fn(cube)
    if record:
        cube.record_move(move_name)


def undo(cube: Cube) -> str | None:
    m = cube.pop_history()
    if not m:
        return None
    MOVE_TABLE[INVERSE_MOVE[m]](cube)
    return m


def redo(cube: Cube) -> str | None:
    m = cube.pop_redo()
    if not m:
        return None
    MOVE_TABLE[m](cube)
    return m
