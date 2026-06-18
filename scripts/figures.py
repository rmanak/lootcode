"""Generate SVG figures for problem statements.

Hand-rolled SVG (no dependencies) so figures are reproducible and stay tied to the
actual example data. See docs/problem-images.md for when a figure is warranted and
how it is stored/served. Each public function returns a complete SVG document as a
string; build_bank.py writes them to content/problems/<slug>/assets/.
"""
from __future__ import annotations

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
INK = "#1f2430"
MUTED = "#6b7280"
BORDER = "#b9b4a8"
PRIMARY = "#0f766e"
ACCENT = "#b45309"

_DEFS = (
    f'<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
    f'markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{PRIMARY}"/></marker>'
    f'<marker id="arrowA" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
    f'markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
)


def _svg(w: int, h: int, parts: list[str], defs: str = _DEFS) -> str:
    body = "\n  ".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">\n'
            f'  <defs>{defs}</defs>\n  {body}\n</svg>\n')


def _text(s, x, y, fill=INK, size=14, anchor="middle", weight="400") -> str:
    return (f'<text x="{x:.0f}" y="{y:.0f}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def _label(s, x, y) -> str:
    return _text(s, x, y, MUTED, 13, weight="600")


def _grid(values, ox, oy, cell=46, numbers=True) -> list[str]:
    parts = []
    for r, row in enumerate(values):
        for c in range(len(row)):
            x, y = ox + c * cell, oy + r * cell
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#fff" '
                f'stroke="{BORDER}" stroke-width="1.5"/>')
    if numbers:
        parts += _grid_text(values, ox, oy, cell)
    return parts


def _grid_text(values, ox, oy, cell=46) -> list[str]:
    parts = []
    for r, row in enumerate(values):
        for c, v in enumerate(row):
            if v == "":
                continue
            x, y = ox + c * cell + cell / 2, oy + r * cell + cell / 2
            # White halo (paint-order: stroke) keeps digits legible over the path.
            parts.append(
                f'<text x="{x:.0f}" y="{y:.0f}" fill="{INK}" stroke="#fff" '
                f'stroke-width="3" paint-order="stroke" font-size="{int(cell * 0.38)}" '
                f'text-anchor="middle" dominant-baseline="central">{v}</text>')
    return parts


# --- Rotate Image: input grid -> arrow -> rotated grid ----------------------
def rotate_image_svg(before, after) -> str:
    cell, pad, top, gap = 46, 16, 36, 84
    n = len(before)
    gw = n * cell
    left_x, right_x = pad, pad + gw + gap
    width, height = pad * 2 + 2 * gw + gap, top + gw + pad
    parts = [_label("Input", left_x + gw / 2, 24),
             _label("Output", right_x + gw / 2, 24)]
    parts += _grid(before, left_x, top, cell)
    parts += _grid(after, right_x, top, cell)
    ay = top + gw / 2
    ax1, ax2 = left_x + gw + 14, right_x - 14
    parts.append(_text("rotate 90° ↻", (ax1 + ax2) / 2, ay - 12, PRIMARY, 13,
                       weight="700"))
    parts.append(f'<line x1="{ax1}" y1="{ay:.0f}" x2="{ax2}" y2="{ay:.0f}" '
                 f'stroke="{PRIMARY}" stroke-width="2.5" marker-end="url(#arrow)"/>')
    return _svg(width, height, parts)


# --- Spiral Matrix: grid with the traversal path ----------------------------
def _spiral_coords(rows, cols):
    res, top, bot, left, right = [], 0, rows - 1, 0, cols - 1
    while top <= bot and left <= right:
        for c in range(left, right + 1):
            res.append((top, c))
        top += 1
        for r in range(top, bot + 1):
            res.append((r, right))
        right -= 1
        if top <= bot:
            for c in range(right, left - 1, -1):
                res.append((bot, c))
            bot -= 1
        if left <= right:
            for r in range(bot, top - 1, -1):
                res.append((r, left))
            left += 1
    return res


def spiral_matrix_svg(matrix) -> str:
    cell, pad, top = 48, 18, 18
    rows, cols = len(matrix), len(matrix[0])
    width, height = pad * 2 + cols * cell, top + pad + rows * cell
    parts = _grid(matrix, pad, top, cell, numbers=False)  # cells first
    pts = [(pad + c * cell + cell / 2, top + r * cell + cell / 2)
           for r, c in _spiral_coords(rows, cols)]
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    parts.append(f'<circle cx="{pts[0][0]:.0f}" cy="{pts[0][1]:.0f}" r="5" '
                 f'fill="{ACCENT}"/>')
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" '
                 f'stroke-width="2.5" stroke-linejoin="round" opacity="0.9" '
                 f'marker-end="url(#arrowA)"/>')
    parts += _grid_text(matrix, pad, top, cell)  # numbers on top of the path
    return _svg(width, height, parts)


# --- Unique Paths: grid with start, finish, a sample path -------------------
def unique_paths_svg(m, n) -> str:
    cell, pad, top = 46, 16, 32
    width, height = pad * 2 + n * cell, top + pad + m * cell
    parts = [_label(f"{m} × {n} grid — move right or down", pad + n * cell / 2, 22)]
    parts += _grid([["" for _ in range(n)] for _ in range(m)], pad, top, cell)
    sx, sy = pad, top
    fx, fy = pad + (n - 1) * cell, top + (m - 1) * cell
    parts.append(f'<rect x="{sx}" y="{sy}" width="{cell}" height="{cell}" '
                 f'fill="{PRIMARY}" opacity="0.16" stroke="{PRIMARY}" stroke-width="2"/>')
    parts.append(_text("Start", sx + cell / 2, sy + cell / 2 + 4, PRIMARY, 11, weight="700"))
    parts.append(f'<rect x="{fx}" y="{fy}" width="{cell}" height="{cell}" '
                 f'fill="{ACCENT}" opacity="0.16" stroke="{ACCENT}" stroke-width="2"/>')
    parts.append(_text("Finish", fx + cell / 2, fy + cell / 2 + 4, ACCENT, 11, weight="700"))
    pts = [(sx + cell / 2, sy + cell / 2)]
    pts += [(pad + c * cell + cell / 2, sy + cell / 2) for c in range(1, n)]
    pts += [(fx + cell / 2, top + r * cell + cell / 2) for r in range(1, m)]
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{PRIMARY}" '
                 f'stroke-width="2.5" stroke-dasharray="5 4" marker-end="url(#arrow)"/>')
    return _svg(width, height, parts)


# --- Binary trees: root and subRoot side by side ----------------------------
class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v, self.l, self.r = v, None, None


def _build(arr):
    if not arr or arr[0] is None:
        return None
    root = _N(arr[0])
    q, i = [root], 1
    while q and i < len(arr):
        node = q.pop(0)
        if i < len(arr):
            v = arr[i]; i += 1
            if v is not None:
                node.l = _N(v); q.append(node.l)
        if i < len(arr):
            v = arr[i]; i += 1
            if v is not None:
                node.r = _N(v); q.append(node.r)
    return root


def _tree_group(arr, label, highlight, highlight2=None):
    root = _build(arr)
    pos, order, counter = {}, [], [0]

    def walk(n, depth):
        if not n:
            return
        walk(n.l, depth + 1)
        pos[id(n)] = (counter[0], depth)
        order.append((n, counter[0], depth))
        counter[0] += 1
        walk(n.r, depth + 1)

    walk(root, 0)
    if not order:
        return ["" for _ in ()], 60, 60
    cols = counter[0]
    maxdepth = max(d for _, _, d in order)
    xstep, ystep, r, pad_top, pad_x = 48, 62, 18, 28, 22

    def px(col):
        return pad_x + col * xstep + r

    def py(depth):
        return pad_top + depth * ystep + r

    parts = [_label(label, (px(0) + px(cols - 1)) / 2, 16)]
    for n, col, depth in order:
        for child in (n.l, n.r):
            if child is not None and id(child) in pos:
                cc, cd = pos[id(child)]
                parts.append(f'<line x1="{px(col):.0f}" y1="{py(depth):.0f}" '
                             f'x2="{px(cc):.0f}" y2="{py(cd):.0f}" stroke="{BORDER}" '
                             f'stroke-width="2"/>')
    for n, col, depth in order:
        x, y = px(col), py(depth)
        hot = highlight is not None and n.v in highlight
        hot2 = highlight2 is not None and n.v in highlight2
        if hot2:
            fill, stroke = "#fbe3cf", ACCENT
        elif hot:
            fill, stroke = "#d6efea", PRIMARY
        else:
            fill, stroke = "#fff", INK
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x:.0f}" y="{y:.0f}" fill="{INK}" font-size="15" '
                     f'font-weight="700" text-anchor="middle" '
                     f'dominant-baseline="central">{n.v}</text>')
    width = pad_x * 2 + (cols - 1) * xstep + r * 2
    height = pad_top + maxdepth * ystep + r * 2 + 8
    return parts, width, height


def tree_pair_svg(root_arr, sub_arr, highlight=None) -> str:
    g1, w1, h1 = _tree_group(root_arr, "root", highlight)
    g2, w2, h2 = _tree_group(sub_arr, "subRoot", highlight)
    pad, gap, top = 16, 56, 8
    width = pad * 2 + w1 + gap + w2
    height = top + max(h1, h2) + pad
    parts = [f'<g transform="translate({pad},{top})">{"".join(g1)}</g>',
             f'<g transform="translate({pad + w1 + gap},{top})">{"".join(g2)}</g>']
    return _svg(width, height, parts)


def tree_svg(arr, highlight=None, highlight2=None, caption="") -> str:
    """A single binary tree (level-order array), optional highlighted nodes."""
    g, w, h = _tree_group(arr, caption, highlight, highlight2)
    pad, top = 16, 8
    return _svg(pad * 2 + w, top + h + pad,
                [f'<g transform="translate({pad},{top})">{"".join(g)}</g>'])


def tree_transform_svg(before, after, label_a="Input", label_b="Output",
                       highlight=None) -> str:
    """Two trees side by side with an arrow between (e.g. invert)."""
    g1, w1, h1 = _tree_group(before, label_a, highlight)
    g2, w2, h2 = _tree_group(after, label_b, highlight)
    pad, gap, top = 16, 72, 8
    width = pad * 2 + w1 + gap + w2
    height = top + max(h1, h2) + pad
    ay = top + max(h1, h2) / 2
    ax1, ax2 = pad + w1 + 14, pad + w1 + gap - 14
    parts = [f'<g transform="translate({pad},{top})">{"".join(g1)}</g>',
             f'<g transform="translate({pad + w1 + gap},{top})">{"".join(g2)}</g>',
             f'<line x1="{ax1:.0f}" y1="{ay:.0f}" x2="{ax2:.0f}" y2="{ay:.0f}" '
             f'stroke="{PRIMARY}" stroke-width="2.5" marker-end="url(#arrow)"/>']
    return _svg(width, height, parts)


# --- Grids of characters / 0-1 cells ----------------------------------------
def islands_svg(grid, caption="") -> str:
    """A 0/1 grid with land cells ('1') shaded."""
    cell, pad = 40, 16
    top = 30 if caption else 12
    rows, cols = len(grid), len(grid[0])
    width, height = pad * 2 + cols * cell, top + pad + rows * cell
    parts = [_label(caption, pad + cols * cell / 2, 20)] if caption else []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            x, y = pad + c * cell, top + r * cell
            land = str(v) == "1"
            fill = "#d6efea" if land else "#fff"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                         f'fill="{fill}" stroke="{BORDER}" stroke-width="1.5"/>')
            parts.append(_text(v, x + cell / 2, y + cell / 2 + 5,
                               INK if land else MUTED, 15,
                               weight="700" if land else "400"))
    return _svg(width, height, parts)


def matrix_zeroes_svg(before, after) -> str:
    """Before/after grids; cells zeroed in the output are tinted."""
    cell, pad, top, gap = 40, 16, 36, 96
    rows, cols = len(before), len(before[0])
    gw, gh = cols * cell, rows * cell
    left_x, right_x = pad, pad + gw + gap
    width, height = pad * 2 + 2 * gw + gap, top + gh + pad
    parts = [_label("Input", left_x + gw / 2, 24),
             _label("Output", right_x + gw / 2, 24)]
    parts += _grid(before, left_x, top, cell)
    for r, row in enumerate(after):
        for c, v in enumerate(row):
            x, y = right_x + c * cell, top + r * cell
            fill = "#fbe3cf" if v == 0 else "#fff"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                         f'fill="{fill}" stroke="{BORDER}" stroke-width="1.5"/>')
    parts += _grid_text(after, right_x, top, cell)
    ay = top + gh / 2
    ax1, ax2 = left_x + gw + 14, right_x - 14
    parts.append(_text("set zeroes", (ax1 + ax2) / 2, ay - 12, PRIMARY, 12,
                       weight="700"))
    parts.append(f'<line x1="{ax1}" y1="{ay:.0f}" x2="{ax2}" y2="{ay:.0f}" '
                 f'stroke="{PRIMARY}" stroke-width="2.5" marker-end="url(#arrow)"/>')
    return _svg(width, height, parts)


def falling_path_svg(matrix, path) -> str:
    """A numeric grid with one chosen cell per row (the falling path) highlighted."""
    cell, pad, top = 48, 18, 30
    rows, cols = len(matrix), len(matrix[0])
    width, height = pad * 2 + cols * cell, top + pad + rows * cell
    parts = [_label("pick one cell per row; next row is the same or an adjacent column",
                    pad + cols * cell / 2, 20)]
    pset = set(map(tuple, path))
    for r in range(rows):
        for c in range(cols):
            x, y = pad + c * cell, top + r * cell
            hot = (r, c) in pset
            fill = "#d6efea" if hot else "#fff"
            stroke = PRIMARY if hot else BORDER
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                         f'fill="{fill}" stroke="{stroke}" '
                         f'stroke-width="{2 if hot else 1.5}"/>')
    pts = [(pad + c * cell + cell / 2, top + r * cell + cell / 2) for r, c in path]
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" '
                 f'stroke-width="2.5" stroke-linejoin="round" '
                 f'marker-end="url(#arrowA)"/>')
    parts += _grid_text(matrix, pad, top, cell)
    return _svg(width, height, parts)


def word_search_svg(board, word, path) -> str:
    """A letter grid with the matching path (list of (row, col)) drawn over it."""
    cell, pad, top = 46, 16, 32
    rows, cols = len(board), len(board[0])
    width, height = pad * 2 + cols * cell, top + pad + rows * cell
    parts = [_label(f'word = "{word}"', pad + cols * cell / 2, 22)]
    parts += _grid(board, pad, top, cell, numbers=False)
    pts = [(pad + c * cell + cell / 2, top + r * cell + cell / 2) for r, c in path]
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    parts.append(f'<circle cx="{pts[0][0]:.0f}" cy="{pts[0][1]:.0f}" r="6" '
                 f'fill="{ACCENT}"/>')
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" '
                 f'stroke-width="3" stroke-linejoin="round" opacity="0.85" '
                 f'marker-end="url(#arrowA)"/>')
    parts += _grid_text(board, pad, top, cell)
    return _svg(width, height, parts)
