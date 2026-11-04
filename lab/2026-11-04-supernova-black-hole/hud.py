"""The mission clock (the scene's only text), drawn with skia at output resolution.

    T − 23 h 14 m          physical time from core bounce
    ▸▸ ×1.6·10⁴            clock rate (screen second → physical seconds); one ▸ in slow motion
    ├────●─────┼──────┤    log-time rail: −1 day … bounce … +300 yr

Returned as a premultiplied RGBA patch plus its position, for a cheap alpha blend on the frame.
"""

from __future__ import annotations

import numpy as np
import skia

import timeline as TL

TEXT = (0xEC, 0xEF, 0xF4)      # aion.style.TEXT
MUTED = (0x9A, 0xA5, 0xB1)     # aion.style.MUTED
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
MINUS = "−"


def fmt_time(T):
    sign = MINUS if T < 0 else "+"
    a = abs(T)
    yr, d, h, m = 3.156e7, 86400.0, 3600.0, 60.0
    if a >= yr:
        v = a / yr
        body = f"{v:.1f} yr" if v < 10 else f"{v:.0f} yr"
    elif a >= d:
        body = f"{int(a // d)} d {int(a % d // h):02d} h"
    elif a >= h:
        body = f"{int(a // h)} h {int(a % h // m):02d} m"
    elif a >= m:
        body = f"{int(a // m)} m {int(a % m):02d} s"
    elif a >= 1.0:
        body = f"{a:.2f} s"
    else:
        body = f"{a * 1e3:.1f} ms"
    return f"T {sign} {body}"


def fmt_rate(r):
    if r >= 100:
        e = int(np.floor(np.log10(r)))
        mant = r / 10**e
        if mant >= 9.95:
            mant, e = 1.0, e + 1
        return f"×{mant:.1f}·10{str(e).translate(SUP)}"
    if r >= 9.95:
        return f"×{r:.0f}"
    if r >= 0.995:
        return f"×{r:.1f}" if abs(r - 1) > 0.05 else "×1"
    return f"×{r:.2f}"


_RAIL_MIN = np.arcsinh(-TL.A.T_SI_BURN / TL.TAU0)
_RAIL_MAX = np.arcsinh(TL.A.T_END / TL.TAU0)


def rail_x(T):
    return float((np.arcsinh(T / TL.TAU0) - _RAIL_MIN) / (_RAIL_MAX - _RAIL_MIN))


class HUD:
    def __init__(self, width, height):
        self.W, self.H = width, height
        u = height / 1080.0
        self.u = u
        self.pw, self.ph = int(470 * u), int(150 * u)
        self.x0 = int(width - 0.05 * width - self.pw)                # 5% safe margin
        self.y0 = int(height - 0.06 * height - self.ph)
        tf = skia.Typeface.MakeFromName("Ubuntu Sans Mono", skia.FontStyle(300, 5, skia.FontStyle.kUpright_Slant))
        try:   # variable font: ask for the light instance explicitly
            wght = skia.FontArguments.VariationPosition.Coordinate(skia.FourByteTag.from_str("wght"), 300.0)
            args = skia.FontArguments()
            args.setVariationDesignPosition(skia.FontArguments.VariationPosition(
                skia.FontArguments.VariationPosition.Coordinates([wght])))
            tf = tf.makeClone(args)
        except Exception:
            pass
        self.f_main = skia.Font(tf, 30 * u)
        self.f_rate = skia.Font(tf, 21 * u)
        for f in (self.f_main, self.f_rate):
            f.setEdging(skia.Font.Edging.kAntiAlias)
            f.setSubpixel(True)
            f.setHinting(skia.FontHinting.kNone)

    def draw(self, s, alpha):
        """RGBA uint8 patch (premultiplied, top-down rows) and its top-left corner on the frame."""
        img = np.zeros((self.ph, self.pw, 4), np.uint8)
        if alpha <= 0.0:
            return img, (self.x0, self.y0)
        surf = skia.Surface(img, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
        cv = surf.getCanvas()
        u, W = self.u, self.pw
        T, rate = TL.T_of(s), TL.rate_of(s)
        right = W - 2 * u

        def paint(rgb, a):
            p = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(round(255 * a * alpha))))
            return p

        def shadowed(text, x, y, font, rgb, a):
            sh = paint((0, 0, 0), 0.55 * a)
            sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3.0 * u))
            cv.drawString(text, x, y + 1.0 * u, font, sh)
            cv.drawString(text, x, y, font, paint(rgb, a))

        # main time, right-aligned
        txt = fmt_time(T)
        shadowed(txt, right - self.f_main.measureText(txt), 52 * u, self.f_main, TEXT, 0.88)
        # rate with play arrows (drawn as paths: crisp at any size)
        rt = fmt_rate(rate)
        wr = self.f_rate.measureText(rt)
        y = 84 * u
        shadowed(rt, right - wr, y, self.f_rate, TEXT, 0.72)
        n_arrows = 1 if rate < 1.5 else 2
        ax = right - wr - 12 * u
        for k in range(n_arrows):
            x = ax - k * 10 * u
            path = skia.Path()
            path.moveTo(x - 8 * u, y - 13 * u)
            path.lineTo(x, y - 7 * u)
            path.lineTo(x - 8 * u, y - 1 * u)
            path.close()
            cv.drawPath(path, paint(TEXT, 0.72))
        # log-time rail
        L = 300 * u
        x0, yr = right - L, 112 * u
        line = paint(MUTED, 0.45)
        line.setStrokeWidth(1.2 * u)
        line.setStyle(skia.Paint.kStroke_Style)
        cv.drawLine(x0, yr, right, yr, line)
        for Tk, hgt in ((-TL.A.T_SI_BURN, 5), (-1.0, 3), (0.0, 8), (1.0, 3), (86400.0, 3), (3.156e7, 3), (TL.A.T_END, 5)):
            xk = x0 + L * rail_x(Tk)
            cv.drawLine(xk, yr - hgt * u, xk, yr + hgt * u, line)
        xd = x0 + L * rail_x(T)
        done = paint(TEXT, 0.75)
        done.setStrokeWidth(1.6 * u)
        done.setStyle(skia.Paint.kStroke_Style)
        cv.drawLine(x0, yr, xd, yr, done)
        cv.drawCircle(xd, yr, 6.0 * u, paint(TEXT, 0.18))
        cv.drawCircle(xd, yr, 3.2 * u, paint(TEXT, 0.95))
        surf.flushAndSubmit()
        return img, (self.x0, self.y0)


def blend(frame_bottom_up, hud_img, pos, H):
    """Alpha-blend a premultiplied top-down patch onto an RGB frame stored bottom-up (GL readback)."""
    x0, y0 = pos
    ph, pw = hud_img.shape[:2]
    rows = slice(H - y0 - ph, H - y0)
    patch = hud_img[::-1].astype(np.float32) / 255.0
    dst = frame_bottom_up[rows, x0:x0 + pw].astype(np.float32) / 255.0
    a = patch[..., 3:4]
    out = patch[..., :3] + dst * (1.0 - a)
    frame_bottom_up[rows, x0:x0 + pw] = np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    for s in (0, 3, 7, 9.5, 10.9, 11, 12, 13.3, 16, 19, 21, 23, 24.5, 27, 30):
        print(f"{s:5.1f}  {fmt_time(TL.T_of(s)):>18s}   {fmt_rate(TL.rate_of(s))}")
