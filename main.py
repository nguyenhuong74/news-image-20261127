#!/usr/bin/env python3
"""Draw a 1024x1024 summary of the world news of Friday 27 November 2026.

Pure standard library: canvas is a bytearray, text comes from a hand-written
5x7 bitmap font, and the PNG is encoded with zlib/struct. No network, no
installed packages, fully deterministic.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 241, 232)
NAVY = (20, 33, 61)
NAVY_LT = (38, 55, 92)
RED = (178, 34, 34)
GOLD = (212, 175, 55)
INK = (24, 24, 24)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
BORDER = (200, 192, 176)

ACCENTS = [
    (178, 34, 34),    # Gulf flashpoint - red
    (30, 80, 140),    # North Korea - steel blue
    (20, 90, 70),     # Ukraine - deep green
    (120, 70, 140),   # US storm - purple
    (180, 120, 20),   # UK migration - amber
    (150, 40, 90),    # Delhi rescue - magenta
]

# ------------------------------------------------------------------- font
# 5x7 bitmap font, rows top to bottom, '#' = pixel on.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
}

# ----------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

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

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r * 2:
                        self.set(xx, yy, c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)

    def star(self, cx, cy, r_out, r_in, points, c):
        import math
        verts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / points - math.pi / 2
            verts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
        for i in range(len(verts)):
            a, b = verts[i], verts[(i + 1) % len(verts)]
            self.triangle([(cx, cy), a, b], c)

# -------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT['?'])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == '1':
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx

def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)

# ------------------------------------------------------------------- icons
def icon_tanker(cv, x, y, s, accent):
    # hull
    cv.fill_rect(x, y + 58 * s // 10, 110 * s // 10, 22 * s // 10, NAVY)
    cv.triangle([(x, y + 58 * s // 10), (x + 14 * s // 10, y + 58 * s // 10),
                 (x, y + 80 * s // 10)], NAVY)
    # containers
    cv.fill_rect(x + 22 * s // 10, y + 40 * s // 10, 26 * s // 10, 18 * s // 10, accent)
    cv.fill_rect(x + 52 * s // 10, y + 40 * s // 10, 26 * s // 10, 18 * s // 10, GOLD)
    # funnel with smoke
    cv.fill_rect(x + 84 * s // 10, y + 34 * s // 10, 12 * s // 10, 24 * s // 10, INK)
    cv.circle(x + 90 * s // 10, y + 24 * s // 10, 7 * s // 10, GREY)
    cv.circle(x + 98 * s // 10, y + 14 * s // 10, 9 * s // 10, GREY)
    # explosion star above the deck
    cv.star(x + 60 * s // 10, y + 16 * s // 10, 16 * s // 10, 7 * s // 10, 8, RED)
    # waves
    for i, wx in enumerate((0, 30, 60, 90)):
        cv.line(x + wx * s // 10, y + 92 * s // 10,
                x + (wx + 16) * s // 10, y + 92 * s // 10, NAVY_LT, 2)

def icon_missile(cv, x, y, s, accent):
    # body
    cv.fill_rect(x + 44 * s // 10, y + 12 * s // 10, 22 * s // 10, 62 * s // 10, accent)
    cv.triangle([(x + 44 * s // 10, y + 12 * s // 10),
                 (x + 66 * s // 10, y + 12 * s // 10),
                 (x + 55 * s // 10, y - 6 * s // 10)], accent)
    cv.fill_rect(x + 50 * s // 10, y + 30 * s // 10, 10 * s // 10, 8 * s // 10, WHITE)
    # fins
    cv.triangle([(x + 44 * s // 10, y + 58 * s // 10),
                 (x + 44 * s // 10, y + 76 * s // 10),
                 (x + 30 * s // 10, y + 78 * s // 10)], accent)
    cv.triangle([(x + 66 * s // 10, y + 58 * s // 10),
                 (x + 66 * s // 10, y + 76 * s // 10),
                 (x + 80 * s // 10, y + 78 * s // 10)], accent)
    # flame
    cv.triangle([(x + 48 * s // 10, y + 76 * s // 10),
                 (x + 62 * s // 10, y + 76 * s // 10),
                 (x + 55 * s // 10, y + 100 * s // 10)], GOLD)
    cv.triangle([(x + 51 * s // 10, y + 76 * s // 10),
                 (x + 59 * s // 10, y + 76 * s // 10),
                 (x + 55 * s // 10, y + 92 * s // 10)], RED)

def icon_shield(cv, x, y, s, accent):
    # shield outline
    cv.fill_rect(x + 20 * s // 10, y, 70 * s // 10, 46 * s // 10, accent)
    cv.triangle([(x + 20 * s // 10, y + 46 * s // 10),
                 (x + 90 * s // 10, y + 46 * s // 10),
                 (x + 55 * s // 10, y + 100 * s // 10)], accent)
    # inner shield
    cv.fill_rect(x + 30 * s // 10, y + 10 * s // 10, 50 * s // 10, 34 * s // 10, WHITE)
    cv.triangle([(x + 30 * s // 10, y + 44 * s // 10),
                 (x + 80 * s // 10, y + 44 * s // 10),
                 (x + 55 * s // 10, y + 84 * s // 10)], WHITE)
    # lightning bolt
    cv.triangle([(x + 62 * s // 10, y + 12 * s // 10),
                 (x + 40 * s // 10, y + 52 * s // 10),
                 (x + 54 * s // 10, y + 52 * s // 10)], RED)
    cv.triangle([(x + 54 * s // 10, y + 52 * s // 10),
                 (x + 48 * s // 10, y + 80 * s // 10),
                 (x + 70 * s // 10, y + 40 * s // 10)], RED)

def icon_storm(cv, x, y, s, accent):
    # cloud
    cv.circle(x + 30 * s // 10, y + 34 * s // 10, 20 * s // 10, NAVY)
    cv.circle(x + 55 * s // 10, y + 24 * s // 10, 24 * s // 10, NAVY)
    cv.circle(x + 80 * s // 10, y + 36 * s // 10, 18 * s // 10, NAVY)
    cv.fill_rect(x + 14 * s // 10, y + 34 * s // 10, 82 * s // 10, 22 * s // 10, NAVY)
    # lightning bolt
    cv.triangle([(x + 60 * s // 10, y + 56 * s // 10),
                 (x + 40 * s // 10, y + 92 * s // 10),
                 (x + 54 * s // 10, y + 92 * s // 10)], GOLD)
    cv.triangle([(x + 54 * s // 10, y + 92 * s // 10),
                 (x + 46 * s // 10, y + 116 * s // 10),
                 (x + 68 * s // 10, y + 76 * s // 10)], GOLD)
    # rain drops
    for rx in (18, 88):
        cv.line(x + rx * s // 10, y + 66 * s // 10,
                x + (rx - 4) * s // 10, y + 82 * s // 10, accent, 3)
        cv.line(x + rx * s // 10, y + 90 * s // 10,
                x + (rx - 4) * s // 10, y + 104 * s // 10, accent, 3)

def icon_chart(cv, x, y, s, accent):
    # axes
    cv.line(x + 12 * s // 10, y + 8 * s // 10, x + 12 * s // 10, y + 96 * s // 10, INK, 3)
    cv.line(x + 12 * s // 10, y + 96 * s // 10, x + 104 * s // 10, y + 96 * s // 10, INK, 3)
    # descending bars, baseline at y+96, heights falling left to right
    for bx, hgt in ((20, 64), (42, 48), (64, 32), (86, 16)):
        cv.fill_rect(x + bx * s // 10, y + (96 - hgt) * s // 10,
                     14 * s // 10, hgt * s // 10, accent)
    # down arrow
    cv.line(x + 18 * s // 10, y + 14 * s // 10, x + 92 * s // 10, y + 78 * s // 10, RED, 4)
    cv.triangle([(x + 92 * s // 10, y + 78 * s // 10),
                 (x + 74 * s // 10, y + 76 * s // 10),
                 (x + 90 * s // 10, y + 92 * s // 10)], RED)

def icon_badge(cv, x, y, s, accent):
    # badge circle
    cv.circle(x + 55 * s // 10, y + 45 * s // 10, 42 * s // 10, accent)
    cv.circle(x + 55 * s // 10, y + 45 * s // 10, 33 * s // 10, WHITE)
    # check mark
    cv.line(x + 36 * s // 10, y + 46 * s // 10, x + 50 * s // 10, y + 62 * s // 10, accent, 6)
    cv.line(x + 50 * s // 10, y + 62 * s // 10, x + 76 * s // 10, y + 28 * s // 10, accent, 6)
    # ribbon tails
    cv.triangle([(x + 38 * s // 10, y + 78 * s // 10),
                 (x + 52 * s // 10, y + 78 * s // 10),
                 (x + 40 * s // 10, y + 104 * s // 10)], GOLD)
    cv.triangle([(x + 58 * s // 10, y + 78 * s // 10),
                 (x + 72 * s // 10, y + 78 * s // 10),
                 (x + 70 * s // 10, y + 104 * s // 10)], GOLD)

ICONS = [icon_tanker, icon_missile, icon_shield, icon_storm, icon_chart, icon_badge]

# ----------------------------------------------------------------- stories
# Each story: kicker, headline lines, body lines. Facts verified against
# news first reported on Friday 27 November 2026 (NDTV, Qatar Tribune,
# Economic Times, Reuters via Firstpost/Al Jazeera).
STORIES = [
    ("MIDDLE EAST",
     ["GULF FLASHPOINT"],
     ["Two Italians killed in a",
      "drone strike in Kuwait;",
      "blasts hit three tankers",
      "in the Strait of Hormuz.",
      "Iran denies any role."]),
    ("NORTH KOREA",
     ["KIM EXPANDS", "NUCLEAR DRIVE"],
     ["Kim Jong Un calls for a",
      "bigger nuclear programme",
      "and wider deployment of",
      "tactical nuclear weapons."]),
    ("UKRAINE WAR",
     ["ZELENSKY WARNS", "OF MASS STRIKE"],
     ["Zelensky warns of a new",
      "Russian mass strike in the",
      "coming days. Trump urges",
      "Putin to pull back."]),
    ("UNITED STATES",
     ["THANKSGIVING", "STORM HITS US"],
     ["About 400 flights",
      "cancelled; 724,000 homes",
      "without power. California",
      "coast floods in king tides"]),
    ("UNITED KINGDOM",
     ["UK MIGRATION", "AT 30-YEAR LOW"],
     ["Net migration falls to its",
      "lowest in almost 30 years",
      "outside the pandemic",
      "period, figures show."]),
    ("INDIA",
     ["164 FREED IN", "DELHI RAID"],
     ["Delhi police rescue 164",
      "foreigners from a cyber-",
      "slavery racket: 92",
      "Indonesians, 72 Malaysians."]),
]

# ------------------------------------------------------------------ layout
def draw_header(cv):
    cv.fill_rect(0, 0, W, 168, NAVY)
    # small globe at left, clear of the centred date line
    gx, gy, gr = 76, 84, 38
    cv.circle(gx, gy, gr, GOLD, fill=False)
    cv.line(gx - gr, gy, gx + gr, gy, GOLD, 2)
    cv.line(gx, gy - gr, gx, gy + gr, GOLD, 2)
    # kicker
    draw_text_centered(cv, W // 2, 20, "THE WORLD IN ONE DAY", 3, GOLD)
    # date
    draw_text_centered(cv, W // 2, 52, "FRIDAY 27 NOVEMBER 2026", 5, WHITE)
    # sub-line
    draw_text_centered(cv, W // 2, 122, "SIX STORIES THAT DEFINED THE DAY", 2, (200, 205, 220))
    cv.fill_rect(0, 164, W, 4, RED)

def draw_card(cv, x, y, w, h, accent, kicker, headline, body, icon_fn):
    cv.fill_rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, BORDER, 2)
    cv.fill_rect(x, y, w, 8, accent)
    draw_text(cv, x + 18, y + 20, kicker, 2, accent)
    hy = y + 44
    for line in headline:
        draw_text(cv, x + 18, hy, line, 3, INK)
        hy += 30
    # icon zone left, body text right
    icon_fn(cv, x + 16, y + 118, 10, accent)
    bx = x + 150
    by = y + 122
    for line in body:
        draw_text(cv, bx, by, line, 2, (52, 52, 52))
        by += 17

def draw_footer(cv):
    draw_text_centered(cv, W // 2, 1006,
                       "REPORTED 27 NOVEMBER 2026 - NDTV, QATAR TRIBUNE, ECONOMIC TIMES, REUTERS",
                       2, GREY)

def build():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    margin, gap = 16, 16
    cw = (W - 2 * margin - gap) // 2
    ch = 258
    gx, gy = margin, 184
    for i, (kicker, headline, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        draw_card(cv, x, y, cw, ch, ACCENTS[i], kicker, headline, body, ICONS[i])
    draw_footer(cv)
    return cv

# --------------------------------------------------------------------- png
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    n = write_png(cv, os.path.join(out_dir, "entry.png"))
    print(f"wrote {n} bytes to {out_dir}/entry.png")

if __name__ == "__main__":
    main()
