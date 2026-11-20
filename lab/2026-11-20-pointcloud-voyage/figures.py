"""Graphic queen and king busts drawn as medallions (PIL, supersampled), sampled into points by overlays.py.

Conventional heraldic look: a gold coin ring, a crowned bust, and flat saturated colours that read well as additive
points. Dido wears Tyrian purple with a gold necklace; the king has a crimson robe with an ermine collar and a
sceptre. Returns an RGBA image (transparent outside the figure).
"""
from __future__ import annotations

from PIL import Image, ImageDraw

S = 1000          # drawing size (square)
GOLD, GOLD_HI = (255, 196, 70), (255, 232, 150)
SKIN, SKIN_SH = (238, 178, 132), (200, 130, 95)


def _crown(d, cx, y_base, w, h, n, jewel, tall=False):
    """A gold crown: a band with n points tipped by balls, jewels on the band."""
    x0, x1 = cx - w / 2, cx + w / 2
    pts = [(x0, y_base)]
    for i in range(n):
        a = x0 + w * i / n
        b = x0 + w * (i + 0.5) / n
        pts += [(a, y_base - h * 0.35), (b, y_base - h)]
    pts += [(x1, y_base - h * 0.35), (x1, y_base)]
    d.polygon(pts, fill=GOLD)
    d.rectangle([x0, y_base - h * 0.32, x1, y_base], fill=GOLD_HI)
    r = w * 0.035
    for i in range(n):
        b = x0 + w * (i + 0.5) / n
        d.ellipse([b - r, y_base - h - r, b + r, y_base - h + r], fill=GOLD_HI)
    for i in range(n):
        b = x0 + w * (i + 0.5) / n
        c = jewel[i % len(jewel)]
        d.ellipse([b - r * 1.1, y_base - h * 0.2 - r * 1.1, b + r * 1.1, y_base - h * 0.2 + r * 1.1], fill=c)
    if tall:                                  # a cross-ball finial on the king's crown
        d.rectangle([cx - 6, y_base - h - 60, cx + 6, y_base - h], fill=GOLD)
        d.rectangle([cx - 22, y_base - h - 46, cx + 22, y_base - h - 34], fill=GOLD)


def _face(d, cx, cy, rx, ry, lips):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=SKIN)
    for s in (-1, 1):                         # eyes, brows
        ex = cx + s * rx * 0.38
        d.ellipse([ex - 13, cy - 14, ex + 13, cy + 6], fill=(255, 245, 235))
        d.ellipse([ex - 7, cy - 10, ex + 7, cy + 4], fill=(40, 25, 20))
        d.line([ex - 24, cy - 32, ex + 22, cy - 36 + (4 if s > 0 else 0)], fill=(70, 40, 25), width=7)
    d.line([cx, cy - 5, cx - 8, cy + 38, cx + 6, cy + 42], fill=SKIN_SH, width=6)
    d.ellipse([cx - 26, cy + 62, cx + 26, cy + 82], fill=lips)


def _medallion(fig, ring):
    """Clip the figure to a disc and add the gold coin ring."""
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([40, 40, S - 40, S - 40], fill=255)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(fig, (0, 0), Image.composite(fig.getchannel("A"), m, m))
    d = ImageDraw.Draw(out)
    d.ellipse([22, 22, S - 22, S - 22], outline=ring, width=16)
    d.ellipse([52, 52, S - 52, S - 52], outline=(ring[0], int(ring[1] * 0.8), int(ring[2] * 0.6)), width=5)
    for i in range(36):                       # beaded rim, like an old coin
        import math
        a = i / 36 * 2 * math.pi
        x, y = S / 2 + 455 * math.cos(a), S / 2 + 455 * math.sin(a)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=GOLD_HI)
    return out


def queen():
    fig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    cx = S / 2
    hair = (70, 36, 22)
    d.ellipse([cx - 210, 250, cx + 210, 720], fill=hair)                       # hair behind
    d.polygon([(cx - 210, 480), (cx - 250, 900), (cx + 250, 900), (cx + 210, 480)], fill=hair)
    d.ellipse([cx - 360, 760, cx + 360, 1250], fill=(122, 38, 140))            # Tyrian purple gown
    d.polygon([(cx - 120, 770), (cx, 900), (cx + 120, 770)], fill=SKIN)       # neckline
    d.line([(cx - 130, 765), (cx, 905), (cx + 130, 765)], fill=GOLD, width=14)
    d.rectangle([cx - 55, 600, cx + 55, 800], fill=SKIN)                       # neck
    for i in range(9):                                                          # necklace
        x = cx - 88 + 22 * i
        y = 852 - 0.009 * (x - cx) ** 2
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=GOLD_HI if i % 2 else (40, 200, 190))
    _face(d, cx, 500, 145, 185, (200, 50, 70))
    d.chord([cx - 160, 300, cx + 160, 520], 180, 360, fill=hair)               # hair over the brow
    for s in (-1, 1):                                                           # earrings
        d.ellipse([cx + s * 150 - 12, 560, cx + s * 150 + 12, 600], fill=GOLD_HI)
    _crown(d, cx, 340, 300, 120, 5, [(220, 40, 60), (40, 200, 190)])
    return _medallion(fig, (255, 190, 90))


def king():
    fig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    cx = S / 2
    hair, beard = (110, 70, 40), (120, 75, 42)
    d.ellipse([cx - 380, 740, cx + 380, 1250], fill=(178, 34, 40))             # crimson robe
    d.ellipse([cx - 300, 720, cx + 300, 880], fill=(245, 240, 230))            # ermine collar
    for i in range(10):
        x = cx - 250 + 55 * i
        y = 790 + (18 if i % 2 else -8)
        d.polygon([(x, y - 14), (x - 7, y + 10), (x + 7, y + 10)], fill=(20, 20, 20))
    d.rectangle([cx - 60, 620, cx + 60, 760], fill=SKIN)                       # neck
    d.ellipse([cx - 175, 300, cx + 175, 560], fill=hair)                       # hair
    _face(d, cx, 500, 150, 180, (170, 60, 55))
    d.polygon([(cx - 150, 540), (cx - 120, 690), (cx, 790), (cx + 120, 690), (cx + 150, 540),
               (cx + 80, 600), (cx, 620), (cx - 80, 600)], fill=beard)          # beard
    d.line([(cx - 70, 575), (cx, 560), (cx + 70, 575)], fill=beard, width=22)  # moustache
    d.chord([cx - 158, 330, cx + 158, 520], 180, 360, fill=hair)
    _crown(d, cx, 350, 330, 160, 5, [(220, 30, 50), (60, 120, 230), (40, 190, 110)], tall=True)
    d.rectangle([cx + 255, 380, cx + 275, 960], fill=GOLD)                     # sceptre
    d.ellipse([cx + 230, 330, cx + 300, 400], fill=GOLD_HI)
    d.ellipse([cx + 252, 352, cx + 278, 378], fill=(220, 30, 50))
    return _medallion(fig, (255, 190, 90))


def hide():
    """A stretched ox hide (four legs, neck, tail) with a few dark patches, a stitched rim and a dashed spiral:
    the cut Dido will make into strips."""
    import numpy as np
    cx = cy = S / 2
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)

    def bump(a, w, h):
        dd = np.angle(np.exp(1j * (th - a)))
        return h * np.exp(-(dd / w) ** 2)

    r = 225 + 10 * np.sin(7 * th + 1.0) + 6 * np.sin(13 * th)
    for a in (np.radians(35), np.radians(145), np.radians(215), np.radians(325)):
        r = r + bump(a, 0.14, 165)                     # legs
    r = r + bump(np.radians(270), 0.30, 70) + bump(np.radians(90), 0.06, 95)   # neck (up), tail (down)
    rx = r * 1.08
    outline = [(cx + a * np.cos(t), cy + 20 + b * np.sin(t)) for a, b, t in zip(rx, r, th)]
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(outline, fill=255)
    fig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    body = Image.new("RGBA", (S, S), (198, 138, 78, 255))
    d = ImageDraw.Draw(body)
    for (x, y, a, b) in [(-120, -90, 110, 80), (150, 40, 90, 120), (-40, 170, 130, 70), (60, -180, 70, 50)]:
        d.ellipse([cx + x - a, cy + y - b, cx + x + a, cy + y + b], fill=(110, 64, 34, 255))
    k = np.linspace(0, 9.5 * np.pi, 1400)               # dashed spiral cut
    rs = 14 + 7.6 * k
    sp = [(cx + 1.08 * q * np.cos(t), cy + 20 + q * np.sin(t)) for q, t in zip(rs, k)]
    for i in range(0, len(sp) - 8, 16):
        d.line(sp[i:i + 9], fill=(255, 226, 150, 255), width=7)
    fig.paste(body, (0, 0), m)
    d = ImageDraw.Draw(fig)
    inner = [(cx + (x - cx) * 0.94, cy + 20 + (y - cy - 20) * 0.94) for x, y in outline]
    for i in range(0, len(inner), 10):                  # stitches
        d.line(inner[i:i + 5], fill=(255, 238, 200), width=6)
    d.line(outline + outline[:1], fill=(255, 196, 120), width=8)
    return _medallion(fig, (255, 190, 90))


if __name__ == "__main__":                    # preview sheet
    from pathlib import Path
    sheet = Image.new("RGB", (3 * S, S), (0, 0, 0))
    sheet.paste(queen(), (0, 0), queen())
    sheet.paste(king(), (S, 0), king())
    sheet.paste(hide(), (2 * S, 0), hide())
    p = Path(__file__).parent / "out/figures.png"
    sheet.resize((3 * S // 2, S // 2)).save(p)
    print(p)
