#!/usr/bin/env python3
"""news-image-20261125: one-page newspaper front page summing up the world
news of Wednesday 25 November 2026.

Pure standard library. Draws everything programmatically (hand-rolled PNG
encoder, hand-rolled 5x7 bitmap typeface, hand-drawn pictograms) and writes
one image to $MAKEFUN_OUTPUT_DIR/entry.png.

Stories verified against Reuters / RFE-RL reporting dated 25 Nov 2026:
  1. China launches Shenzhou-24; first Pakistani astronaut to Tiangong.
  2. Australia and Solomon Islands sign a security pact.
  3. Australia formally apologises to LGBTQ veterans.
  4. Shanghai leaders pledge loyalty as party chief Chen Jining is probed.
  5. New analysis: more than 700,000 Russian soldiers killed in Ukraine.
  6. Gold slips and the dollar steadies ahead of US inflation data.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (22, 38, 78)          # navy masthead / borders
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (90, 90, 84)
GOLD = (201, 162, 39)
RED = (176, 58, 46)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '#' = on.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def rect_outline(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, c)
                elif not fill and abs(d - r * r) <= r * 2:
                    self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle via scanline
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
                self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for r, row in enumerate(glyph):
                for col, bit in enumerate(row):
                    if bit == '#':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)


def wrap(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- pictograms
def pic_rocket(cv, bx, by, col):
    # body
    cv.rect(bx + 38, by + 18, 20, 44, col)
    cv.tri(bx + 38, by + 18, bx + 58, by + 18, bx + 48, by + 2, col)
    cv.tri(bx + 38, by + 62, bx + 30, by + 78, bx + 38, by + 70, RED)
    cv.tri(bx + 58, by + 62, bx + 66, by + 78, bx + 58, by + 70, RED)
    cv.tri(bx + 42, by + 62, bx + 54, by + 62, bx + 48, by + 88, (232, 126, 32))
    cv.circle(bx + 48, by + 34, 6, WHITE)
    cv.circle(bx + 48, by + 34, 3, (120, 180, 220))
    cv.circle(bx + 14, by + 14, 2, GOLD)
    cv.circle(bx + 80, by + 10, 2, GOLD)
    cv.circle(bx + 84, by + 40, 2, GOLD)


def pic_shield(cv, bx, by, col):
    pts_top = [(bx + 48, by + 4), (bx + 82, by + 16), (bx + 82, by + 48),
               (bx + 48, by + 88), (bx + 14, by + 48), (bx + 14, by + 16)]
    # fill shield by scanlines
    for y in range(by + 4, by + 89):
        if y <= by + 16:
            x0, x1 = bx + 48 - (y - by - 4) * 34 // 12, bx + 48 + (y - by - 4) * 34 // 12
        elif y <= by + 48:
            x0, x1 = bx + 14, bx + 82
        else:
            t = (y - by - 48) / 40.0
            x0 = int(bx + 14 + t * 34)
            x1 = int(bx + 82 - t * 34)
        for x in range(x0, x1 + 1):
            cv.set(x, y, col)
    cv.line(bx + 34, by + 48, bx + 44, by + 60, WHITE, 4)
    cv.line(bx + 44, by + 60, bx + 66, by + 32, WHITE, 4)


def pic_heart(cv, bx, by, col):
    cv.circle(bx + 34, by + 34, 16, col)
    cv.circle(bx + 62, by + 34, 16, col)
    cv.tri(bx + 20, by + 40, bx + 76, by + 40, bx + 48, by + 84, col)
    cv.rect(bx + 20, by + 34, 56, 10, col)
    cv.circle(bx + 34, by + 30, 5, WHITE)
    cv.circle(bx + 62, by + 30, 5, WHITE)


def pic_skyline(cv, bx, by, col):
    cv.circle(bx + 74, by + 18, 10, GOLD)
    cv.rect(bx + 8, by + 46, 20, 44, col)
    cv.rect(bx + 32, by + 28, 24, 62, col)
    cv.rect(bx + 60, by + 56, 28, 34, col)
    cv.rect(bx + 40, by + 16, 8, 12, col)
    for wy in (36, 50, 64, 78):
        for wx in (12, 20, 36, 48, 64, 76):
            if (wx + wy) % 3 == 0:
                cv.rect(wx + bx, wy + by, 4, 5, GOLD)
    cv.rect(bx + 4, by + 90, 88, 4, col)


def pic_memorial(cv, bx, by, col):
    # memorial cross with a red poppy
    cv.rect(bx + 42, by + 12, 12, 72, col)
    cv.rect(bx + 22, by + 26, 52, 12, col)
    cv.rect(bx + 28, by + 84, 40, 6, col)
    cv.circle(bx + 74, by + 20, 9, RED)
    cv.circle(bx + 74, by + 20, 3, BLACK)


def pic_gold(cv, bx, by, col):
    # three gold bars + rising chart arrow
    for i, (x, y) in enumerate([(bx + 8, by + 62), (bx + 32, by + 62), (bx + 56, by + 62)]):
        cv.tri(x, y, x + 24, y, x + 20, y - 16, GOLD)
        cv.rect(x + 2, y - 16, 16, 16, GOLD)
        cv.rect(x + 2, y - 16, 16, 4, (240, 200, 90))
    cv.line(bx + 8, by + 44, bx + 30, by + 30, RED, 3)
    cv.line(bx + 30, by + 30, bx + 52, by + 38, RED, 3)
    cv.line(bx + 52, by + 38, bx + 82, by + 12, RED, 3)
    cv.tri(bx + 82, by + 12, bx + 70, by + 12, bx + 82, by + 24, RED)


# ---------------------------------------------------------------- stories
STORIES = [
    dict(kicker="SPACE", colour=(27, 79, 114), pic=pic_rocket,
         head=["CHINA LAUNCHES", "SHENZHOU-24"],
         body="First Pakistani astronaut heads for the Tiangong space station.",
         fact="CREW OF THREE, INCLUDING PAKISTAN'S FIRST ASTRONAUT"),
    dict(kicker="PACIFIC", colour=(17, 122, 101), pic=pic_shield,
         head=["CANBERRA SIGNS", "SOLOMONS PACT"],
         body="Australia becomes the Solomons' defence partner of choice.",
         fact="SOLOMONS PREVIOUSLY SIGNED A SECURITY DEAL WITH CHINA"),
    dict(kicker="AUSTRALIA", colour=(125, 60, 152), pic=pic_heart,
         head=["AUSTRALIA SAYS SORRY", "TO LGBTQ VETERANS"],
         body="Formal apology for decades of discrimination in the military.",
         fact="APOLOGY COVERS SERVING AND FORMER LGBTQ MEMBERS"),
    dict(kicker="CHINA", colour=(176, 58, 46), pic=pic_skyline,
         head=["SHANGHAI CHIEF", "UNDER PROBE"],
         body="City leaders pledge loyalty to Beijing as Chen Jining is investigated.",
         fact="FOURTH POLITBURO MEMBER PROBED SINCE 2025"),
    dict(kicker="UKRAINE WAR", colour=(147, 81, 22), pic=pic_memorial,
         head=["700,000 RUSSIAN", "TROOPS KILLED"],
         body="New analysis counts the war dead in nearly five years of war.",
         fact="THE WAR IS NOW IN ITS FIFTH YEAR"),
    dict(kicker="MARKETS", colour=(125, 102, 8), pic=pic_gold,
         head=["GOLD SLIPS AS", "FED HIKE LOOMS"],
         body="Dollar steadies as traders await US inflation data.",
         fact="GOLD AT $3,544 AN OUNCE; FED MEETS IN DECEMBER"),
]


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead
    cv.rect(0, 0, W, 168, INK)
    cv.rect(0, 168, W, 4, GOLD)
    # globe pictogram
    cv.circle(86, 84, 52, (40, 80, 140))
    cv.circle(86, 84, 52, WHITE, fill=False)
    cv.line(34, 84, 138, 84, WHITE, 2)
    cv.line(86, 32, 86, 136, WHITE, 2)
    for k in (-1, 1):
        cv.line(86 + k * 26, 36, 86 + k * 26, 132, WHITE, 1)
    cv.text_centred(560, 18, "WEDNESDAY - THE WORLD IN ONE PAGE", 2, GOLD)
    cv.text(196, 52, "25 NOVEMBER 2026", 6, WHITE)
    cv.text_centred(560, 116, "SIX STORIES THAT DEFINED THE DAY", 2, (200, 210, 235))

    # ---- story grid: 2 cols x 3 rows
    mx, my, gap = 16, 188, 16
    cw = (W - 2 * mx - gap) // 2
    ch = (984 - my - 2 * gap) // 3
    for i, st in enumerate(STORIES):
        x = mx + (i % 2) * (cw + gap)
        y = my + (i // 2) * (ch + gap)
        cv.rect(x, y, cw, ch, WHITE)
        cv.rect_outline(x, y, cw, ch, INK, 2)
        # kicker band
        cv.rect(x, y, cw, 32, st['colour'])
        cv.text(x + 12, y + 8, st['kicker'], 2, WHITE)
        # pictogram
        st['pic'](cv, x + 14, y + 48, st['colour'])
        # headline (scale 3) and body (scale 2)
        tx = x + 124
        hy = y + 52
        for j, line in enumerate(st['head']):
            cv.text(tx, hy + j * 26, line, 3, BLACK)
        by = hy + len(st['head']) * 26 + 10
        for j, line in enumerate(wrap(st['body'], 29)):
            cv.text(tx, by + j * 18, line.upper(), 2, GREY)
        # key-fact strip at the bottom of the cell
        fy = y + ch - 46
        cv.rect(x + 14, fy - 8, cw - 28, 2, GOLD)
        for j, line in enumerate(wrap(st['fact'], 38)):
            cv.text(x + 14, fy + j * 18, line, 2, st['colour'])
        # thin rule under kicker
        cv.rect(x, y + 32, cw, 2, GOLD)

    # ---- footer
    cv.text_centred(W // 2, 994,
                    "ALL STORIES FIRST REPORTED ON WEDNESDAY 25 NOVEMBER 2026",
                    2, INK)
    return cv


# ---------------------------------------------------------------- PNG writer
def png_bytes(cv):
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    print(f"wrote {path}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
