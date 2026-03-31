"""
rubui.renderer
~~~~~~~~~~~~~~
High-density 3D Rubik's Cube renderer for the terminal.

Renders exactly three faces at all times: Top (U), Front (F), Right (R).
The projection is an oblique 3D projection with a mathematically defined
tile coordinate system and true per-tile geometry.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from rubui.cube_engine import Cube
from rubui.utils import THEMES, TerminalBuffer, clear_screen, fg_rgb, reset_ansi

# ── Color helpers ─────────────────────────────────────────────────────────


def _darken(rgb: tuple[int, int, int], factor: float = 0.65) -> tuple[int, int, int]:
    return (int(rgb[0] * factor), int(rgb[1] * factor), int(rgb[2] * factor))


def _lighten(rgb: tuple[int, int, int], factor: float = 1.10) -> tuple[int, int, int]:
    return (
        min(255, int(rgb[0] * factor)),
        min(255, int(rgb[1] * factor)),
        min(255, int(rgb[2] * factor)),
    )


def _border(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return (max(0, rgb[0] - 55), max(0, rgb[1] - 55), max(0, rgb[2] - 55))


# ── Layout ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CubeLayout:
    tile_h: int
    tile_w: int
    slant_x: int
    slant_y: int
    origin_x: int  # front face top-left
    origin_y: int  # front face top-left
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int


@dataclass(frozen=True)
class AnimationState:
    move: str
    progress: float  # 0..1
    pre_state: dict[str, list[str]]


# ── Projection math ───────────────────────────────────────────────────────


def _project(p: tuple[float, float, float], layout: CubeLayout) -> tuple[float, float]:
    x, y, z = p
    sx = layout.origin_x + x * layout.tile_w + z * layout.slant_x
    sy = layout.origin_y + y * layout.tile_h - z * layout.slant_y
    return sx, sy


def _rotate_point(
    p: tuple[float, float, float],
    axis: str,
    angle: float,
    layer_center: float,
) -> tuple[float, float, float]:
    x, y, z = p
    c = math.cos(angle)
    s = math.sin(angle)

    if axis == "x":
        ox, oy, oz = layer_center, 1.5, 1.5
        y -= oy
        z -= oz
        y2 = y * c - z * s
        z2 = y * s + z * c
        return (x, y2 + oy, z2 + oz)
    if axis == "y":
        ox, oy, oz = 1.5, layer_center, 1.5
        x -= ox
        z -= oz
        x2 = x * c + z * s
        z2 = -x * s + z * c
        return (x2 + ox, y, z2 + oz)
    if axis == "z":
        ox, oy, oz = 1.5, 1.5, layer_center
        x -= ox
        y -= oy
        x2 = x * c - y * s
        y2 = x * s + y * c
        return (x2 + ox, y2 + oy, z)
    return p


def _inside_convex(pt: tuple[float, float], poly: list[tuple[float, float]]) -> bool:
    x, y = pt
    sign = None
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        if cross == 0:
            continue
        curr = cross > 0
        if sign is None:
            sign = curr
        elif sign != curr:
            return False
    return True


def _edge_char(p0: tuple[float, float], p1: tuple[float, float]) -> str:
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    if abs(dy) <= 0.25:
        return "─"
    if abs(dx) <= 0.25:
        return "│"
    if dx > 0 and dy < 0:
        return "╱"
    return "╲"


def _draw_line(
    buffer: TerminalBuffer,
    p0: tuple[float, float],
    p1: tuple[float, float],
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
    ch: str,
    *,
    clip: tuple[int, int, int, int] | None = None,
    inside: list[tuple[float, float]] | None = None,
) -> None:
    x0 = int(round(p0[0]))
    y0 = int(round(p0[1]))
    x1 = int(round(p1[0]))
    y1 = int(round(p1[1]))
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        ok = True
        if clip:
            x0c, y0c, x1c, y1c = clip
            ok = x0c <= x < x1c and y0c <= y < y1c
        if ok and inside:
            ok = _inside_convex((x + 0.5, y + 0.5), inside)
        if ok:
            buffer.put(x, y, ch, fg=fg, bg=bg)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


# ── Move animation definitions ─────────────────────────────────────────────


MOVE_DEF: dict[str, tuple[str, list[int], int]] = {
    "R": ("x", [2], -1),
    "L": ("x", [0], 1),
    "M": ("x", [1], -1),
    "Rw": ("x", [1, 2], -1),
    "Lw": ("x", [0, 1], 1),
    "x": ("x", [0, 1, 2], -1),
    "U": ("y", [0], 1),
    "D": ("y", [2], -1),
    "E": ("y", [1], 1),
    "Uw": ("y", [0, 1], 1),
    "Dw": ("y", [1, 2], -1),
    "y": ("y", [0, 1, 2], 1),
    "F": ("z", [0], 1),
    "B": ("z", [2], -1),
    "S": ("z", [1], 1),
    "Fw": ("z", [0, 1], 1),
    "Bw": ("z", [1, 2], -1),
    "z": ("z", [0, 1, 2], 1),
}


def _parse_move(move: str) -> tuple[str, bool, bool]:
    token = move.strip()
    double = token.endswith("2")
    if double:
        token = token[:-1]
    prime = token.endswith("'")
    if prime:
        token = token[:-1]
    if len(token) == 1 and token in "rludfb":
        token = token.upper() + "w"
    if len(token) == 2 and token[1] in "wW":
        token = token[0].upper() + "w"
    if token in ("x", "y", "z"):
        token = token.lower()
    return token, prime, double


# ── Face geometry ─────────────────────────────────────────────────────────


def _cubie_center(face: str, r: int, c: int) -> tuple[float, float, float]:
    if face == "F":
        return (c + 0.5, r + 0.5, 0.5)
    if face == "U":
        return (c + 0.5, 0.5, 2.5 - r)
    # R
    return (2.5, r + 0.5, c + 0.5)


def _tile_corners(face: str, r: int, c: int) -> list[tuple[float, float, float]]:
    if face == "F":
        x0, x1 = c, c + 1
        y0, y1 = r, r + 1
        z = 0.0
        return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    if face == "U":
        x0, x1 = c, c + 1
        z0, z1 = 2 - r, 3 - r
        y = 0.0
        return [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    # R
    y0, y1 = r, r + 1
    z0, z1 = c, c + 1
    x = 3.0
    return [(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)]


# ── Rendering ─────────────────────────────────────────────────────────────


def compute_layout(
    width: int,
    height: int,
    *,
    size_pref: int | None,
    top_reserved: int,
    bottom_reserved: int,
) -> CubeLayout:
    avail_h = max(1, height - top_reserved - bottom_reserved)
    avail_w = max(1, width)

    def fits(th: int) -> bool:
        tw = th * 2
        sx = max(1, tw // 2)
        sy = max(1, th // 2)
        cube_w = 3 * tw + 3 * sx
        cube_h = 3 * th + 3 * sy
        return cube_w <= avail_w and cube_h <= avail_h

    desired = size_pref if size_pref and size_pref > 0 else 999
    th = min(desired, max(1, avail_h))
    while th > 1 and not fits(th):
        th -= 1
    tw = th * 2
    sx = max(1, tw // 2)
    sy = max(1, th // 2)
    cube_w = 3 * tw + 3 * sx
    cube_h = 3 * th + 3 * sy

    bbox_x = (avail_w - cube_w) // 2
    bbox_y = top_reserved + (avail_h - cube_h) // 2
    origin_x = bbox_x
    origin_y = bbox_y + 3 * sy

    return CubeLayout(
        tile_h=th,
        tile_w=tw,
        slant_x=sx,
        slant_y=sy,
        origin_x=origin_x,
        origin_y=origin_y,
        bbox_x=bbox_x,
        bbox_y=bbox_y,
        bbox_w=cube_w,
        bbox_h=cube_h,
    )


class CubeRenderer:
    def __init__(self, use_color: bool = True, theme_name: str = "dark") -> None:
        self.use_color = use_color
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES["dark"])

    def render(
        self,
        buffer: TerminalBuffer,
        cube: Cube,
        layout: CubeLayout,
        *,
        clip: tuple[int, int, int, int] | None = None,
        animation: AnimationState | None = None,
    ) -> None:
        if self.use_color:
            self._render_color(buffer, cube, layout, animation=animation, clip=clip)
        else:
            self._render_plain(buffer, cube, layout)

    def _render_color(
        self,
        buffer: TerminalBuffer,
        cube: Cube,
        layout: CubeLayout,
        *,
        animation: AnimationState | None,
        clip: tuple[int, int, int, int] | None,
    ) -> None:
        state = animation.pre_state if animation else cube.state
        tiles = self._build_tiles(state, layout, animation)
        clip = _clip_bounds(layout) if clip is None else clip

        # draw far to near
        tiles.sort(key=lambda t: t["depth"], reverse=True)

        for tile in tiles:
            self._draw_tile(
                buffer,
                tile["poly"],
                tile["rgb"],
                tile["border"],
                clip=clip,
            )

    def _render_plain(
        self, buffer: TerminalBuffer, cube: Cube, layout: CubeLayout
    ) -> None:
        # Minimal monochrome mode: draw sticker letters at tile centers
        for face in ("U", "F", "R"):
            for r in range(3):
                for c in range(3):
                    corners = _tile_corners(face, r, c)
                    pts = [_project(p, layout) for p in corners]
                    cx = sum(p[0] for p in pts) / 4
                    cy = sum(p[1] for p in pts) / 4
                    ch = cube.state[face][r * 3 + c]
                    buffer.put(int(round(cx)), int(round(cy)), ch)

    def _draw_tile(
        self,
        buffer: TerminalBuffer,
        poly: list[tuple[float, float]],
        rgb: tuple[int, int, int],
        border: tuple[int, int, int],
        *,
        clip: tuple[int, int, int, int] | None = None,
    ) -> None:
        min_x = int(math.floor(min(p[0] for p in poly)))
        max_x = int(math.ceil(max(p[0] for p in poly)))
        min_y = int(math.floor(min(p[1] for p in poly)))
        max_y = int(math.ceil(max(p[1] for p in poly)))

        if clip:
            x0c, y0c, x1c, y1c = clip
            min_x = max(min_x, x0c)
            max_x = min(max_x, x1c)
            min_y = max(min_y, y0c)
            max_y = min(max_y, y1c)

        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                if _inside_convex((x + 0.5, y + 0.5), poly):
                    buffer.put(x, y, " ", bg=rgb)

        for i in range(4):
            p0 = poly[i]
            p1 = poly[(i + 1) % 4]
            ch = _edge_char(p0, p1)
            _draw_line(
                buffer,
                p0,
                p1,
                fg=border,
                bg=rgb,
                ch=ch,
                clip=clip,
                inside=poly,
            )

    def _build_tiles(
        self,
        state: dict[str, list[str]],
        layout: CubeLayout,
        animation: AnimationState | None,
    ) -> list[dict]:
        axis = None
        layers: list[int] = []
        angle = 0.0
        if animation:
            base, prime, double = _parse_move(animation.move)
            if base in MOVE_DEF:
                axis, layers, sign = MOVE_DEF[base]
                magnitude = math.pi if double else (math.pi / 2)
                if prime:
                    sign *= -1
                angle = sign * magnitude * animation.progress

        tiles: list[dict] = []
        for face in ("U", "F", "R"):
            for r in range(3):
                for c in range(3):
                    color_key = state[face][r * 3 + c]
                    rgb = self.theme[color_key]
                    if face == "U":
                        rgb = _lighten(rgb, 1.08)
                    elif face == "R":
                        rgb = _darken(rgb, 0.70)

                    corners = _tile_corners(face, r, c)
                    cubie = _cubie_center(face, r, c)

                    if axis:
                        if axis == "x":
                            layer_idx = int(round(cubie[0] - 0.5))
                            if layer_idx in layers:
                                corners = [
                                    _rotate_point(p, axis, angle, layer_idx + 0.5)
                                    for p in corners
                                ]
                        elif axis == "y":
                            layer_idx = int(round(cubie[1] - 0.5))
                            if layer_idx in layers:
                                corners = [
                                    _rotate_point(p, axis, angle, layer_idx + 0.5)
                                    for p in corners
                                ]
                        elif axis == "z":
                            layer_idx = int(round(cubie[2] - 0.5))
                            if layer_idx in layers:
                                corners = [
                                    _rotate_point(p, axis, angle, layer_idx + 0.5)
                                    for p in corners
                                ]

                    poly = [_project(p, layout) for p in corners]
                    depth = sum(p[0] + p[1] + p[2] for p in corners) / 4.0
                    tiles.append(
                        {
                            "poly": poly,
                            "rgb": rgb,
                            "border": _border(rgb),
                            "depth": depth,
                        }
                    )
        return tiles


def _clip_bounds(layout: CubeLayout) -> tuple[int, int, int, int]:
    pad_x = (layout.tile_w + layout.slant_x) * 2 + 2
    pad_y = (layout.tile_h + layout.slant_y) * 2 + 2
    x0 = layout.bbox_x - pad_x
    y0 = layout.bbox_y - pad_y
    x1 = layout.bbox_x + layout.bbox_w + pad_x
    y1 = layout.bbox_y + layout.bbox_h + pad_y
    return x0, y0, x1, y1


def _intersect_clip(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    x0 = max(ax0, bx0)
    y0 = max(ay0, by0)
    x1 = min(ax1, bx1)
    y1 = min(ay1, by1)
    return x0, y0, x1, y1


# ── Banner ────────────────────────────────────────────────────────────────


def render_banner(*, use_color: bool = True) -> None:
    """Optional startup banner, always cleared before rendering begins."""
    title = "rubui"
    if use_color:
        sys.stdout.write(clear_screen())
        sys.stdout.write(fg_rgb(137, 180, 250) + title + reset_ansi())
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        sys.stdout.write(clear_screen())
        sys.stdout.write(title + "\n")
        sys.stdout.flush()
    # Fully clear before the cube renders
    sys.stdout.write(clear_screen())
    sys.stdout.flush()


# ── Status bar and frame ──────────────────────────────────────────────────


def draw_status_bar(
    buffer: TerminalBuffer,
    mode: str,
    move_count: int,
    elapsed: float,
    theme: str,
    fps: int = 0,
    speed: float = 0.0,
    use_color: bool = True,
) -> None:
    parts = [
        f"Mode: {mode.capitalize()}",
        f"Moves: {move_count}",
    ]
    if fps > 0:
        parts.append(f"FPS: {fps}")
    if speed > 0:
        parts.append(f"Speed: {speed:.2f}s")
    h = int(elapsed // 3600)
    m = int((elapsed % 3600) // 60)
    s = int(elapsed % 60)
    parts.append(f"Time: {h:02d}:{m:02d}:{s:02d}")
    parts.append(f"Theme: {theme.capitalize()}")

    content = " │ ".join(parts)
    y = buffer.height - 1
    buffer.clear_line(y)

    if use_color:
        bar_bg = (25, 25, 36)
        bar_fg = (180, 190, 210)
        accent = (137, 180, 250)
        for x in range(buffer.width):
            buffer.put(x, y, " ", bg=bar_bg)
        buffer.write(0, y, " ◆ ", fg=accent, bg=bar_bg, is_bold=True)
        buffer.write(4, y, content[: max(0, buffer.width - 4)], fg=bar_fg, bg=bar_bg)
    else:
        buffer.write(0, y, f"[ {content} ]".ljust(buffer.width))


def draw_frame(
    buffer: TerminalBuffer,
    cube: Cube,
    *,
    mode: str = "manual",
    move_count: int = 0,
    elapsed: float = 0.0,
    theme_name: str = "dark",
    fps: int = 0,
    speed: float = 0.0,
    use_color: bool = True,
    command_line: str = "",
    last_move: str = "",
    animation: AnimationState | None = None,
    size: int | None = None,
) -> None:
    header_y = 0
    buffer.height - 1
    info_y = buffer.height - 3
    cmd_y = buffer.height - 2

    buffer.clear_line(header_y)
    if use_color:
        buffer.write(2, header_y, " ◆ rubui ", fg=(137, 180, 250), is_bold=True)
        buffer.write(12, header_y, "│", fg=(80, 85, 110))
        buffer.write(15, header_y, "Press ? for help  q to quit", fg=(100, 110, 140))
    else:
        buffer.write(2, header_y, " ◆ rubui  |  Press ? for help  q to quit")

    # Clear cube area only (full content region to avoid rotation artifacts)
    top_reserved = 1
    bottom_reserved = 3
    layout = compute_layout(
        buffer.width,
        buffer.height,
        size_pref=size,
        top_reserved=top_reserved,
        bottom_reserved=bottom_reserved,
    )
    content_clip = (0, top_reserved, buffer.width, buffer.height - bottom_reserved)
    cube_clip = _clip_bounds(layout)
    clip = _intersect_clip(cube_clip, content_clip)
    clip_x0, clip_y0, clip_x1, clip_y1 = clip
    buffer.clear_rect(clip_x0, clip_y0, clip_x1 - clip_x0, clip_y1 - clip_y0)

    renderer = CubeRenderer(use_color=use_color, theme_name=theme_name)
    renderer.render(buffer, cube, layout, animation=animation, clip=clip)

    # Last move and command line
    buffer.clear_line(info_y)
    buffer.clear_line(cmd_y)
    if last_move:
        if use_color:
            buffer.write(2, info_y, f"Last: {last_move}", fg=(166, 227, 161))
        else:
            buffer.write(2, info_y, f"Last: {last_move}")
    if command_line:
        if use_color:
            buffer.write(2, cmd_y, f":{command_line}▌", fg=(249, 226, 175))
        else:
            buffer.write(2, cmd_y, f":{command_line}_")

    draw_status_bar(
        buffer,
        mode=mode,
        move_count=move_count,
        elapsed=elapsed,
        theme=theme_name,
        fps=fps,
        speed=speed,
        use_color=use_color,
    )
