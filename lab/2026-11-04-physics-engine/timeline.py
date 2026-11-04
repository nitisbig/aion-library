"""Per-frame state: camera + a list of SDF primitives, built from the simulation for a given look.

`build(t, look)` → (camera (cx, cy, h_world), prims float32 (n, 20)). Nothing here invents motion:
positions, velocities and forces are sampled from physics.py's 1200 Hz tracks; this file only decides
what to show, how big, and when.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import labels as LB  # noqa: E402
import physics as P  # noqa: E402

DURATION = P.DURATION
D = P.load()
META = {k[5:]: D[k] for k in D if k.startswith("meta_")}
_, LTAB = LB.build()

# forward-fill the chain balls that stay behind on the floor after the last one leaves
for _nm in ["hero", "c1", "c2", "c3", "twin"]:
    _p, _v = D[f"{_nm}_p"], D[f"{_nm}_v"]
    _ok = np.nonzero(~np.isnan(_p[:, 0]))[0]
    if len(_ok):
        _p[_ok[-1] + 1:] = _p[_ok[-1]]; _v[_ok[-1] + 1:] = 0.0
        _p[:_ok[0]] = _p[_ok[0]]; _v[:_ok[0]] = _v[_ok[0]]

R = P.R
YB = P.Y_FLOOR + R                       # ball centre height when on the floor
X_EQ, X_C, X_WALL = float(META["x_eq"]), float(META["x_c"]), float(META["x_wall"])
T_REL, V_REL = float(META["t_rel"]), float(META["v_rel"])
STAR = META["star"].astype(float)
R_A, GM = float(META["r_a"]), float(META["gm"])
R_P = R_A * (1 - P.ECC) / (1 + P.ECC)
X_EDGE = float(META["x_edge"])
EVK, EV = D["ev_kind"], D["ev"]
BOUNCES = EV[EVK == "bounce"]                        # (t, x, impact speed)
CONTACTS = EV[EVK == "contact"]                      # (t, x, k)
T_CHAIN0 = float(CONTACTS[0, 0]) if len(CONTACTS) else T_REL + 1
T_CHAIN1 = float(CONTACTS[-1, 0]) + 0.06 if len(CONTACTS) else T_REL + 2
ENERGY = D["energy"]                                 # (t, K, U, Q) on the grid during the spring acts
E_TOT = float(ENERGY[0, 1] + ENERGY[0, 2] + ENERGY[0, 3])
T_STAR = T_EDGE_STAR = P.T_EDGE - 0.9                # the star ignites before the floor vanishes


def lin(hexc, k=1.0):
    h = hexc.lstrip("#")
    return np.array([(int(h[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4)]) * k


C = {k: lin(v) for k, v in LB.COL.items()}
C["steel"] = lin("#8C97A8"); C["warm"] = lin("#FF7A4D"); C["cool"] = lin("#5E9BFF")
C["chain"] = lin("#C9D3E0"); C["floor"] = lin("#4A5466"); C["star"] = lin("#FFE2A8")
C["twin1"] = lin("#58C4DD"); C["twin2"] = lin("#C08CFF"); C["grid"] = lin("#3E6A9A"); C["dust"] = lin("#8FA6C8")
C["rod"] = lin("#AEB8C8"); C["wedge1"] = lin("#58C4DD"); C["wedge2"] = lin("#B48CFF")

# ── looks ──────────────────────────────────────────────────────────────────
LOOKS = {
    # A: crisp neon. Solid lit discs, 1–4 px lines, short trails, restrained bloom
    "A": dict(ball_fill=1.0, ball_core=1.25, halo_px=6, halo_k=0.35, rim_px=2.0, lit=1.0, meridian=0.35,
              arrow_px=4.0, arrow_soft=0.0, arrow_gain=1.0, open_head=False, line_px=2.0,
              trail=0.5, trail_px=3.0, trail_soft=0.0, trail_gain=0.9, trail_add=0.0, trail_dash=0.0,
              strobe="fill", strobe_a=0.3, bg="none", bloom_levels=4, bloom=0.35, bloom_thresh=0.9, shutter=0.5, sub=6,
              vig=0.22, grain=0.012, exposure=1.0, star_k=2.2, pend_trail=1.4, sat=1.0),
    # B: light painting. HDR cores, long additive glowing trails, strong bloom, full shutter
    "B": dict(ball_fill=1.0, ball_core=1.6, halo_px=16, halo_k=0.55, rim_px=1.5, lit=0.6, meridian=0.2,
              arrow_px=4.0, arrow_soft=1.2, arrow_gain=1.5, open_head=False, line_px=2.0,
              trail=2.0, trail_px=4.0, trail_soft=3.0, trail_gain=1.8, trail_add=1.0, trail_dash=0.0,
              strobe="glow", strobe_a=0.35, bg="dust", bloom_levels=6, bloom=0.8, bloom_thresh=0.62, shutter=1.0, sub=8,
              vig=0.42, grain=0.025, exposure=1.05, star_k=4.0, pend_trail=3.5, sat=1.0),
    # C: blueprint ink. Hairline outlines, open arrowheads, dashed trails, strobe outlines as the motif
    "C": dict(cross=True, wedge_k=0.45, ball_fill=0.0, ball_core=1.0, halo_px=0, halo_k=0.0, rim_px=1.1, lit=0.0, meridian=0.0,
              arrow_px=2.2, arrow_soft=0.0, arrow_gain=1.0, open_head=True, line_px=1.3,
              trail=1.2, trail_px=1.4, trail_soft=0.0, trail_gain=0.9, trail_add=0.0, trail_dash=14.0,
              strobe="outline", strobe_a=0.55, bg="grid", bloom_levels=3, bloom=0.06, bloom_thresh=1.2, shutter=0.35, sub=4,
              vig=0.15, grain=0.0, exposure=1.0, star_k=1.2, pend_trail=2.0, sat=0.85),
    # D: mix of A and B, crisp. A's solid lit discs + B's long trails and dust; no motion blur, no bloom, no soft glow
    "D": dict(crisp=True, ball_fill=1.0, ball_core=1.1, halo_px=0, halo_k=0.0, rim_px=1.8, lit=1.0, meridian=0.3,
              arrow_px=4.0, arrow_soft=0.0, arrow_gain=1.0, open_head=False, line_px=2.0,
              trail=2.0, trail_px=2.6, trail_soft=0.0, trail_gain=1.0, trail_add=0.0, trail_dash=0.0,
              strobe="fill", strobe_a=0.3, bg="dust", bloom_levels=3, bloom=0.0, bloom_thresh=2.0, shutter=0.0, sub=1,
              vig=0.12, grain=0.0, exposure=1.0, star_k=1.15, pend_trail=3.5, sat=1.0),
}

# ── sampling ───────────────────────────────────────────────────────────────
def S(arr, t):
    f = float(t) * P.FS
    i = int(np.clip(np.floor(f), 0, P.N - 2)); u = f - i
    return arr[i] * (1 - u) + arr[i + 1] * u


def SV(arr, ts):
    f = np.asarray(ts) * P.FS
    i = np.clip(np.floor(f).astype(int), 0, P.N - 2); u = (f - i)[..., None]
    return arr[i] * (1 - u) + arr[i + 1] * u


def pos(nm, t): return S(D[f"{nm}_p"], t)
def vel(nm, t): return S(D[f"{nm}_v"], t)


def force(nm, f, t):
    k = f"{nm}_F_{f}"
    return S(D[k], t) if k in D else np.zeros(2)


def ss(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def win(t, t0, t1, fin=0.5, fout=0.5):
    return float(ss((t - t0) / fin) * (1 - ss((t - (t1 - fout)) / fout)))


def back(u, s=1.7):
    """Ease-out with overshoot (spring-like pop)."""
    u = np.clip(u, 0.0, 1.0) - 1
    return float(u * u * ((s + 1) * u + s) + 1)


# ── camera ─────────────────────────────────────────────────────────────────
CAM_FS = 240


def _camera_track():
    ts = np.arange(int(DURATION * CAM_FS) + 1) / CAM_FS
    cx = np.zeros_like(ts); cy = np.zeros_like(ts); h = np.zeros_like(ts)
    hp = SV(D["hero_p"], ts); tp = SV(D["twin_p"], ts)
    carrier = np.where(ts[:, None] < T_CHAIN0, hp, SV(D[f"c{P.CHAIN_N}_p"], ts))
    ec = STAR + [0.0, (R_A - R_P) / 2]
    for i, t in enumerate(ts):
        if t < 4.5:
            cx[i], cy[i], h[i] = -2.6 + 0.3 * t, 0.25, 8.6 - 0.18 * t
        elif t < 12.0:
            cx[i], cy[i], h[i] = 0.5 * (hp[i, 0] + tp[i, 0]) + 0.9, -0.3, 8.0
        elif t < 19.0:
            cx[i], cy[i], h[i] = hp[i, 0] + 1.6, -0.75, 8.2
        elif t < T_REL + 1.1:
            cx[i], cy[i], h[i] = X_EQ - 0.6, -0.8, 7.6 - 0.25 * ss((t - 22) / 12)
        elif t < P.T_EDGE - 0.6:
            cx[i], cy[i], h[i] = carrier[i, 0] - 1.0, -1.3, 6.2
        elif t < P.T_PEND - 0.4:
            cx[i], cy[i], h[i] = ec[0], ec[1] - 0.15, 6.9
        else:
            cx[i], cy[i], h[i] = STAR[0], STAR[1] + 0.1, 8.9 - 0.5 * ss((t - 53.5) / 5)
    # non-causal Gaussian smoothing: an operator who anticipates the action
    def smooth(a, sig):
        k = np.arange(-int(3 * sig * CAM_FS), int(3 * sig * CAM_FS) + 1) / CAM_FS
        w = np.exp(-0.5 * (k / sig) ** 2); w /= w.sum()
        pad = len(k) // 2
        ap = np.concatenate([np.full(pad, a[0]), a, np.full(pad, a[-1])])
        return np.convolve(ap, w, mode="valid")
    return ts, smooth(cx, 0.45), smooth(cy, 0.45), smooth(h, 0.5)


CAM_T, CAM_X, CAM_Y, CAM_H = _camera_track()
SHAKES = [(float(b[0]), min(float(b[2]) / 6.4, 1.0) * 0.045) for b in BOUNCES if b[2] > 2.0]
SHAKES += [(T_CHAIN0, 0.02), (T_STAR + 0.3, 0.03)]


def camera(t):
    i = t * CAM_FS
    j = int(np.clip(np.floor(i), 0, len(CAM_T) - 2)); u = i - j
    cx = CAM_X[j] * (1 - u) + CAM_X[j + 1] * u
    cy = CAM_Y[j] * (1 - u) + CAM_Y[j + 1] * u
    h = CAM_H[j] * (1 - u) + CAM_H[j + 1] * u
    for k, (ti, a) in enumerate(SHAKES):
        dt = t - ti
        if 0 <= dt < 0.5:
            e = a * np.exp(-dt / 0.085)
            cx += e * np.sin(2 * np.pi * 23 * dt + k)
            cy += e * np.sin(2 * np.pi * 29 * dt + 2 * k + 1)
    return cx, cy, h


# ── primitive buffer ───────────────────────────────────────────────────────
SEG, DISC, RING, TRI, LABEL, RECT, DOT = range(7)


class Prims:
    """Rows of 20 floats: (kind, r, alpha, add | ax, ay, bx, by | cx, cy, p0, p1 | R, G, B, p2 | p3..p6)."""

    def __init__(self, cam, look):
        self.cam, self.L = cam, look
        self.px = cam[2] / 1080.0                   # world units per reference (1080p) pixel
        self.rows = []

    def row(self, kind, r=0.0, alpha=1.0, add=0.0, a=(0, 0), b=(0, 0), c=(0, 0), p0=0.0, p1=0.0,
            col=(1, 1, 1), p2=0.0, p3=0.0, p4=0.0, p5=0.0, p6=0.0):
        if alpha <= 1e-4:
            return
        self.rows.append(np.array([[kind, r, alpha, add, a[0], a[1], b[0], b[1], c[0], c[1], p0, p1,
                                    col[0], col[1], col[2], p2, p3, p4, p5, p6]], "f4"))

    def segs(self, A, B, w_px, col, alpha, alpha_b=None, soft_px=0.0, add=0.0, dash_px=0.0, duty=0.55):
        """Vectorised capsules A[i]→B[i]. alpha may be an array; alpha_b = alpha at B (fades along)."""
        A = np.asarray(A, "f4"); B = np.asarray(B, "f4")
        n = len(A)
        if n == 0:
            return
        al = np.broadcast_to(np.asarray(alpha, "f4"), (n,))
        ab = np.ones(n, "f4") if alpha_b is None else np.broadcast_to(np.asarray(alpha_b, "f4"), (n,)) / np.maximum(al, 1e-6)
        col = np.broadcast_to(np.asarray(col, "f4"), (n, 3))
        rw = np.zeros((n, 20), "f4")
        rw[:, 0] = SEG; rw[:, 1] = 0.5 * w_px * self.px; rw[:, 2] = al; rw[:, 3] = add
        rw[:, 4:6] = A; rw[:, 6:8] = B; rw[:, 10] = soft_px * self.px; rw[:, 11] = ab
        rw[:, 12:15] = col; rw[:, 15] = dash_px * self.px; rw[:, 16] = duty
        self.rows.append(rw[al > 1e-4])

    def seg(self, a, b, w_px, col, alpha=1.0, **kw):
        self.segs([a], [b], w_px, col, alpha, **kw)

    def polyline(self, pts, w_px, col, alpha, **kw):
        pts = np.asarray(pts)
        if len(pts) < 2:
            return
        al = np.broadcast_to(np.asarray(alpha, "f4"), (len(pts),))
        self.segs(pts[:-1], pts[1:], w_px, col, al[:-1], alpha_b=al[1:], **kw)

    def disc(self, c, r, col, alpha=1.0, fill=None, core=None, halo_px=None, halo_k=None, spin=0.0,
             rim_px=None, lit=None, meridian=None, add=0.0):
        L = self.L
        fill = L["ball_fill"] if fill is None else fill
        core = L["ball_core"] if core is None else core
        self.row(DISC, r, alpha, add, a=c, p0=fill, p1=(L["rim_px"] if rim_px is None else rim_px) * self.px,
                 col=np.asarray(col) * core, p2=spin,
                 p3=(L["halo_px"] if halo_px is None else halo_px) * self.px,
                 p4=L["halo_k"] if halo_k is None else halo_k, p5=L["lit"] if lit is None else lit,
                 p6=L["meridian"] if meridian is None else meridian)

    def ring(self, c, r, w_px, col, alpha=1.0, soft_px=0.0, add=1.0):
        self.row(RING, r, alpha, add, a=c, p0=0.5 * w_px * self.px, p1=soft_px * self.px, col=col)

    def tri(self, a, b, c, col, alpha=1.0, add=0.0, soft_px=0.0):
        self.row(TRI, 0.0, alpha, add, a=a, b=b, c=c, col=col, p3=soft_px * self.px)

    def dot(self, c, sigma_px, col, alpha=1.0, add=1.0, world_sigma=None):
        self.row(DOT, world_sigma if world_sigma is not None else sigma_px * self.px, alpha, add, a=c, col=col)

    def rect(self, lo, hi, col, alpha=1.0, fill=1.0, outline_px=0.0, radius_px=0.0):
        self.row(RECT, 0.0, alpha, 0.0, a=lo, b=hi, p0=radius_px * self.px, p1=fill, col=col,
                 p2=0.5 * outline_px * self.px)

    def label(self, key, c, size_px, alpha=1.0, tint=(1, 1, 1), anchor=(0.0, 0.0)):
        e = LTAB[key]
        u = size_px * self.px / 0.62                # world per Manim unit ("F" + pad ≈ 0.62 units tall)
        hw, hh = 0.5 * e["w"] * u, 0.5 * e["h"] * u
        cx, cy = c[0] - anchor[0] * hw, c[1] - anchor[1] * hh
        self.row(LABEL, 0.0, alpha, 0.0, a=(cx, cy), b=(hw, hh), c=e["uv0"], p0=e["uv1"][0], p1=e["uv1"][1],
                 col=tint)
        return hw, hh

    def arrow(self, o, vec, col, alpha=1.0, w_px=None, label=None, label_at="tip", label_side=1.0,
              gain=None, lsize=34):
        L = self.L
        vec = np.asarray(vec, float); o = np.asarray(o, float)
        n_ = np.linalg.norm(vec)
        if n_ < 1e-5 or alpha <= 1e-3:
            return
        w = (L["arrow_px"] if w_px is None else w_px)
        g = L["arrow_gain"] if gain is None else gain
        d = vec / n_; nrm = np.array([-d[1], d[0]])
        hl = min(n_ * 0.5, 4.2 * w * self.px)
        hw = hl * 0.62
        tip = o + vec
        base = tip - d * hl
        colg = np.asarray(col) * g
        if L["open_head"]:
            self.seg(o, tip - d * w * 0.3 * self.px, w, colg, alpha)
            self.seg(tip, base + nrm * hw, w, colg, alpha)
            self.seg(tip, base - nrm * hw, w, colg, alpha)
        else:
            self.seg(o, base + d * 0.25 * hl, w, colg, alpha, soft_px=L["arrow_soft"])
            self.tri(tip, base + nrm * hw, base - nrm * hw, colg, alpha, soft_px=L["arrow_soft"] * 0.6)
        if label:
            sz = lsize * self.px
            if label_at == "tip":
                p = tip + d * (0.75 * sz) + nrm * label_side * 0.0
            else:
                p = o + 0.5 * vec + nrm * label_side * (0.55 * sz + 0.5 * w * self.px + 0.05)
            self.label(label, p, lsize, alpha)

    def out(self):
        return np.concatenate(self.rows) if self.rows else np.zeros((0, 20), "f4")


# ── scene pieces ───────────────────────────────────────────────────────────
GHOST_DT = 0.5
EQ_WINDOWS = [("eq1", 1.2, 4.4), ("eq2", 5.6, 11.9), ("eq3", 13.0, 19.6), ("eq4", 20.6, 29.3),
              ("eq5", 29.6, 35.6), ("eq6", 36.0, 40.0), ("eq7", 40.8, 51.9), ("eq8", 54.2, 58.7)]
# velocity / force / acceleration arrow scales per act (world units per unit of the quantity)
VS = [(0.0, 0.62), (12.0, 0.62), (12.9, 0.3)]


def vscale(t):
    ts, vs = zip(*VS)
    return float(np.interp(t, ts, vs))


def hero_vis(t):
    return float(ss((t - P.T_SPARK) / 0.35))


def warmth(nm, t):
    """1 = the hero's warm light; the light passes along the row with the momentum."""
    if nm == "hero":
        return 1.0 - ss((t - T_CHAIN0 - 0.05) / 0.5)
    if nm == f"c{P.CHAIN_N}":
        tc = CONTACTS[-1, 0] if len(CONTACTS) else 99
        return ss((t - tc) / 0.4)
    return 0.0


def ball_col(w):
    return C["chain"] * (1 - w) + C["ball"] * w


def ghosts(pr, nm, t, t0, t1, r, alpha):
    L = pr.L
    k0 = int(np.ceil(t0 / GHOST_DT)); k1 = int(np.floor(min(t, t1) / GHOST_DT))
    for k in range(k0, k1 + 1):
        tk = k * GHOST_DT
        age = t - tk
        if age < 0.06:
            continue
        a = alpha * (1 - ss((age - 4.5) / 2.0)) * ss((age - 0.06) / 0.25)
        if a <= 1e-3:
            continue
        p = pos(nm, tk)
        if L["strobe"] == "fill":
            pr.disc(p, r, C["ball"], a * L["strobe_a"], fill=0.35, core=0.8, halo_px=0, rim_px=1.2, lit=0, meridian=0)
        elif L["strobe"] == "glow":
            pr.dot(p, r / pr.px * 0.55, C["ball"] * 1.2, a * L["strobe_a"])
        else:
            pr.ring(p, r, 1.1, C["ball"], a * L["strobe_a"], add=0.0)
            pr.seg(p - [r * 0.35, 0], p + [r * 0.35, 0], 1.0, C["ball"], a * L["strobe_a"] * 0.7)
            pr.seg(p - [0, r * 0.35], p + [0, r * 0.35], 1.0, C["ball"], a * L["strobe_a"] * 0.7)
        if nm == "hero" and P.T_G - 0.01 <= tk <= P.T_SPRING:
            # the ghost's shadow on the floor: evenly spaced → vx is constant
            fa = a * win(t, 12.3, 20.6, 0.5, 0.8)
            pr.seg([p[0], P.Y_FLOOR - 0.02], [p[0], P.Y_FLOOR - 0.2], 2.0, C["v"], fa * 0.8)


def trail(pr, nm, t, length, col, alpha, t_min=0.0, w_px=None, gain=None, n=90):
    L = pr.L
    t0 = max(t - length, t_min)
    if t - t0 < 1e-3:
        return
    ts = np.linspace(t0, t, n)
    pts = SV(D[f"{nm}_p"], ts)
    age = (t - ts) / max(length, 1e-3)
    a = alpha * (1 - age) ** 1.6
    g = L["trail_gain"] if gain is None else gain
    pr.polyline(pts, L["trail_px"] if w_px is None else w_px, np.asarray(col) * g, a,
                soft_px=L["trail_soft"], add=L["trail_add"], dash_px=L["trail_dash"])


def floor_span():
    return pos("hero", 12.0)[0] - 4.0, X_WALL + 0.8


def draw_floor(pr, t, cam):
    x0, x1 = floor_span()
    xc = pos("hero", 12.0)[0] + 3.0
    grow = ss((t - 12.0) / 0.9)
    gone = ss((t - (P.T_EDGE - 0.15)) / 0.8)
    if grow <= 0 or gone >= 1:
        return
    a0, a1 = xc - (xc - x0) * grow, xc + (x1 - xc) * grow
    vx0, vx1 = cam[0] - cam[2], cam[0] + cam[2]       # visible x range (generous)
    lo, hi = max(a0, vx0), min(a1, vx1)
    if hi <= lo:
        return
    al = 1 - gone
    pr.seg([lo, P.Y_FLOOR], [hi, P.Y_FLOOR], pr.L["line_px"] + 0.6, C["floor"] * 1.6, al)
    xs = np.arange(np.ceil(lo / 0.3) * 0.3, hi, 0.3)
    pr.segs(np.stack([xs, np.full_like(xs, P.Y_FLOOR - 0.04)], 1),
            np.stack([xs - 0.16, np.full_like(xs, P.Y_FLOOR - 0.2)], 1), 1.2, C["floor"], al * 0.7)
    if gone > 0:                                       # crumble: seeded flecks falling away
        rng = np.random.default_rng(11)
        fx = rng.uniform(lo, hi, 140); vy0 = rng.uniform(0.2, 1.2, 140); dl = rng.uniform(0, 0.35, 140)
        tt = np.clip(t - (P.T_EDGE - 0.15) - dl, 0, None)
        fy = P.Y_FLOOR - vy0 * tt - 1.5 * tt * tt
        for x, y, q in zip(fx, fy, tt):
            if q > 0:
                pr.dot((x, y), 1.6, C["floor"] * 2.5, (1 - gone) * 0.8)


def spring_tip(t):
    if t < 18.6:
        return None
    if t < P.T_SPRING:
        grow = ss((t - 18.6) / 1.0)
        return X_WALL - P.L0 * grow
    if t < T_REL:
        return pos("hero", t)[0] + R
    dt = t - T_REL
    return X_C - 0.11 * np.exp(-dt / 0.45) * np.sin(2 * np.pi * 2.6 * dt)


def draw_spring(pr, t, alpha):
    tip = spring_tip(t)
    if tip is None or alpha <= 0:
        return
    y = YB
    Lc = X_WALL - tip
    strain = (Lc - P.L0) / P.L0
    col = C["steel"] * 1.3
    col = col * (1 - ss(-strain * 2.2)) + C["warm"] * ss(-strain * 2.2)
    col = col * (1 - ss(strain * 1.6)) + C["cool"] * ss(strain * 1.6)
    ncoil, rc, lead = 10, 0.2, 0.14
    s = np.linspace(0, 1, ncoil * 28 + 1)
    phi = 2 * np.pi * ncoil * s
    xs = tip + lead + (Lc - 2 * lead) * s
    ys = y + rc * np.sin(phi)
    front = 0.5 + 0.5 * np.cos(phi)
    pts = np.stack([xs, ys], 1)
    a = alpha * (0.35 + 0.65 * front)
    pr.polyline(pts, pr.L["line_px"] + 0.6 * front.mean(), col, a)
    pr.seg([tip, y], [tip + lead, y], pr.L["line_px"], col, alpha)
    pr.seg([X_WALL - lead, y], [X_WALL, y], pr.L["line_px"], col, alpha)
    pr.seg([tip, y - 0.17], [tip, y + 0.17], pr.L["line_px"] + 1.5, col * 1.2, alpha)   # latch plate


def draw_wall(pr, t, alpha):
    g = ss((t - 18.3) / 0.8)
    if g <= 0 or alpha <= 0:
        return
    top = P.Y_FLOOR + 1.25 * g
    pr.seg([X_WALL, P.Y_FLOOR], [X_WALL, top], pr.L["line_px"] + 1.0, C["floor"] * 1.8, alpha)
    ys = np.arange(P.Y_FLOOR + 0.05, top, 0.22)
    pr.segs(np.stack([np.full_like(ys, X_WALL), ys], 1), np.stack([np.full_like(ys, X_WALL + 0.16), ys - 0.14], 1),
            1.2, C["floor"], alpha * 0.7)


def draw_trace(pr, t, alpha):
    """x(t) written upward from the ball: time scrolls up, so the oscillation paints a sine wave."""
    if alpha <= 0 or t <= P.T_SPRING:
        return
    speed, y0, ytop = 0.40, YB + 0.62, 2.45
    tend = min(t, T_REL)
    t0 = max(P.T_SPRING, t - (ytop - y0) / speed)
    if tend <= t0:
        return
    ts = np.linspace(t0, tend, 600)
    xs = SV(D["hero_p"], ts)[:, 0]
    ys = y0 + (t - ts) * speed
    fade = ss((ytop - ys) / 0.6)
    pr.polyline(np.stack([xs, ys], 1), 2.4, C["ball"] * 1.1, alpha * fade)
    # stylus: a short link from the ball to the start of the trace
    if t < T_REL:
        p = pos("hero", t)
        pr.seg([p[0], p[1] + R + 0.04], [p[0], y0 + (t - tend) * speed], 1.0, C["ball"], alpha * 0.45)
        pr.dot([p[0], y0], 3.0, C["ball"] * 2.0, alpha)
    # equilibrium (dashed)
    pr.seg([X_EQ, y0], [X_EQ, ytop], 1.2, C["muted"], alpha * 0.45, dash_px=10)
    # damping envelope: ±A·e^(−ζωτ) from the exact solution's amplitude at T_D0
    if t > P.T_D0:
        j0 = P.idx(P.T_D0)
        x0 = D["hero_p"][j0, 0] - X_EQ; v0 = D["hero_v"][j0, 0]
        wd = P.OMEGA * np.sqrt(1 - P.ZETA ** 2)
        A0 = np.hypot(x0, (v0 + P.ZETA * P.OMEGA * x0) / wd)
        te = np.linspace(P.T_D0, min(t, P.T_D1, T_REL), 120)
        env = A0 * np.exp(-P.ZETA * P.OMEGA * (te - P.T_D0))
        ye = y0 + (t - te) * speed
        fe = alpha * ss((ytop - ye) / 0.6) * 0.7
        for sgn in (1, -1):
            pr.polyline(np.stack([X_EQ + sgn * env, ye], 1), 1.6, C["U"], fe, dash_px=8)


def draw_energy(pr, t, alpha):
    if alpha <= 0:
        return
    j = np.clip(int(round((t - ENERGY[0, 0]) * P.FS)), 0, len(ENERGY) - 1)
    _, Kk, Uu, Qq = ENERGY[j]
    x0, w, yb, H = X_EQ - 3.75, 0.5, -1.75, 3.6
    s = H / E_TOT
    pr.rect([x0 - 0.04, yb - 0.04], [x0 + w + 0.04, yb + H + 0.04], C["muted"], alpha * 0.8, fill=0.0,
            outline_px=1.3, radius_px=3)
    segs = [("U", Uu), ("K", Kk), ("Q", Qq)]
    y = yb
    for key, e in segs:
        hgt = e * s
        if hgt > 1e-3:
            pr.rect([x0, y], [x0 + w, y + hgt], C[key] * 1.05, alpha * 0.9, radius_px=2)
            la = alpha * ss(hgt / 0.35)
            pr.label(key, (x0 - 0.12, y + hgt / 2), 28, la, anchor=(1.0, 0.0))
        y += hgt
    pr.seg([x0 - 0.12, yb + H], [x0 + w + 0.12, yb + H], 2.0, C["text"] * 1.4, alpha)   # the constant total


def draw_heat(pr, t):
    if t < P.T_D0 or t > P.T_D1 + 1.6:
        return
    rng = np.random.default_rng(5)
    ts = np.arange(P.T_D0, P.T_D1, 1 / 60)
    jit = rng.normal(0, 0.07, (len(ts), 2)); drift = rng.uniform(0.25, 0.6, len(ts))
    side = rng.normal(0, 0.12, len(ts)); life = rng.uniform(0.9, 1.5, len(ts))
    for k, tk in enumerate(ts):
        age = t - tk
        if age <= 0 or age > life[k]:
            continue
        v = vel("hero", tk)[0]
        pw = P.C_DRAG * v * v / (P.C_DRAG * 3.5 ** 2)
        p0 = pos("hero", tk) + jit[k]
        p = p0 + [side[k] * age, drift[k] * age + 0.1]
        a = pw * (1 - age / life[k]) * ss(age / 0.1)
        pr.dot(p, 1.6 if pr.L.get("crisp") else 2.4, C["Q"] * 2.5, min(a, 1.0))


def draw_star(pr, t):
    ign = ss((t - T_STAR) / 0.7)
    if ign <= 0:
        return 0.0
    coll = ss((t - (P.T_PEND - 0.45)) / 0.45)
    k = pr.L["star_k"]
    rad = 0.26 * back((t - T_STAR) / 0.8, 2.2) * (1 - 0.75 * coll)
    a = ign
    crisp = pr.L.get("crisp", False)
    if crisp:
        pr.ring(STAR, rad + 0.12, 1.4, C["star"], a * 0.55 * (1 - coll), add=0.0)
    else:
        pr.dot(STAR, 0, C["star"] * 0.35 * k, a * (1 - coll) * 0.3, world_sigma=0.45 * (1 - 0.5 * coll))
    pr.disc(STAR, max(rad, 1e-3), C["star"], a, fill=1.0, core=k, halo_px=0 if crisp else 14,
            halo_k=0.0 if crisp else 0.45 * (1 - coll), lit=0,
            meridian=0)
    if pr.L["open_head"]:
        pr.ring(STAR, 0.42, 1.0, C["star"], a * 0.6 * (1 - coll), add=0.0)
    else:
        ang = 0.15 * t
        for q in range(2):
            d = np.array([np.cos(ang + q * np.pi / 2), np.sin(ang + q * np.pi / 2)])
            pr.seg(STAR - d * 1.1, STAR + d * 1.1, 1.0, C["star"] * 0.6 * k, a * 0.35 * (1 - coll),
                   soft_px=0.0 if crisp else 2.0, add=1.0)
    sw = t - (T_STAR + 0.25)
    if 0 < sw < 1.0:
        pr.ring(STAR, 0.3 + 2.5 * sw, 2.0, C["star"] * 1.5, (1 - sw) ** 2 * 0.8, soft_px=1.5)
    return coll


def draw_wedges(pr, t, alpha):
    """Kepler II: six wedges swept in equal times T/6. Equal areas (asserted in physics.check)."""
    if alpha <= 0 or t < P.T_EDGE:
        return
    T6 = P.T_ORBIT / 6
    op = D[f"c{P.CHAIN_N}_p"]
    cur = int((t - P.T_EDGE) // T6) % 6
    for k in range(6):
        a0 = P.T_EDGE + k * T6
        if t <= a0:
            break
        a1 = min(a0 + T6, t)
        ts = np.linspace(a0, a1, 28)
        pts = SV(op, ts)
        col = C["wedge1"] if k % 2 == 0 else C["wedge2"]
        hl = 1.0
        if t > P.T_EDGE + P.T_ORBIT and k == cur:          # second orbit: the wedge being re-swept lights up
            hl = 1.8
        for i in range(len(pts) - 1):
            pr.tri(STAR, pts[i], pts[i + 1], col * 0.9, alpha * 0.16 * hl * pr.L.get("wedge_k", 1.0), add=1.0)
        pr.seg(STAR, pts[0], 1.2, col, alpha * 0.55)
        if a1 >= a0 + T6 - 1e-6:
            pr.seg(STAR, pts[-1], 1.2, col, alpha * 0.55)


def draw_body(pr, nm, t, r, col, alpha, glow_p=0.0):
    p = pos(nm, t)
    spin = -(p[0] / r) if nm != "pout0" else 0.0
    if glow_p > 0:
        if pr.L.get("crisp"):
            pr.ring(p, r + 0.07, 2.2, C["p"] * 1.2, min(glow_p, 1.0) * alpha, add=0.0)
        else:
            pr.dot(p, 0, C["p"] * 1.6, glow_p * alpha * 0.55, world_sigma=r * 1.25)
    pr.disc(p, r, col, alpha, spin=spin)
    if pr.L.get("cross"):
        q = r * 0.45
        pr.seg(p - [q, 0], p + [q, 0], 1.0, col, alpha * 0.8)
        pr.seg(p - [0, q], p + [0, q], 1.0, col, alpha * 0.8)
    return p


def build(t, look="A"):
    L = LOOKS[look]
    cam = camera(t)
    pr = Prims(cam, L)
    px = pr.px

    # ── background ──
    if L["bg"] == "grid":
        x0, x1 = cam[0] - cam[2] * 0.95, cam[0] + cam[2] * 0.95
        y0, y1 = cam[1] - cam[2] * 0.55, cam[1] + cam[2] * 0.55
        xs = np.arange(np.floor(x0), x1 + 1); ys = np.arange(np.floor(y0), y1 + 1)
        maj = lambda v: np.isclose(np.mod(v, 5), 0)  # noqa: E731
        pr.segs(np.stack([xs, np.full_like(xs, y0)], 1), np.stack([xs, np.full_like(xs, y1)], 1), 1.0, C["grid"],
                np.where(maj(xs), 0.22, 0.1))
        pr.segs(np.stack([np.full_like(ys, x0), ys], 1), np.stack([np.full_like(ys, x1), ys], 1), 1.0, C["grid"],
                np.where(maj(ys), 0.22, 0.1))
    elif L["bg"] == "dust":
        rng = np.random.default_rng(3)
        q = np.column_stack([rng.uniform(-30, 30, 420), rng.uniform(-12, 8, 420)])
        b = rng.uniform(0.15, 1.0, 420) ** 2
        rho = 0.35
        w = q + np.array(cam[:2]) * (1 - rho)
        vis = (np.abs(w[:, 0] - cam[0]) < cam[2]) & (np.abs(w[:, 1] - cam[1]) < cam[2] * 0.6)
        for p_, bb in zip(w[vis], b[vis]):
            pr.dot(p_, 1.3, C["dust"], 0.35 * bb * win(t, 0.0, 60.0, 1.5, 1.0))

    # ── act 1: spark ──
    if 0.2 < t < 1.4:
        u = (t - 0.25) / 0.5
        pr.dot((P.X0, P.Y0), 2 + 10 * ss(u), C["ball"] * 3.0, ss(u) * (1 - ss((t - 0.6) / 0.6)))
        sw = t - P.T_SPARK
        if 0 < sw < 0.9:
            pr.ring((P.X0 + sw * P.V0, P.Y0), 0.1 + 1.4 * sw, 2.0, C["ball"] * 1.3, (1 - sw / 0.9) ** 2)

    # ── floor, wall, spring ──
    draw_floor(pr, t, cam)
    rig = 1 - ss((t - (P.T_EDGE - 0.3)) / 0.8)
    draw_wall(pr, t, rig)
    draw_spring(pr, t, rig * ss((t - 18.6) / 0.3))
    if P.T_SPRING <= t < P.T_SPRING + 0.6:
        u = (t - P.T_SPRING) / 0.6
        pr.ring((X_C, YB), 0.1 + 0.6 * u, 1.6, C["F"] * 1.4, (1 - u) ** 2)
    if T_REL <= t < T_REL + 0.5:
        u = (t - T_REL) / 0.5
        pr.ring((X_C, YB), 0.1 + 0.5 * u, 1.6, C["v"] * 1.4, (1 - u) ** 2)

    # bounce shockwaves
    for bt, bx, bs in BOUNCES:
        u = (t - bt) / 0.55
        if 0 <= u < 1:
            k = min(bs / 6.4, 1.0)
            pr.ring((bx, P.Y_FLOOR), 0.05 + 1.1 * k * (1 - (1 - u) ** 3), 2.0, C["ball"] * 1.2, (1 - u) ** 2 * k)
            if not pr.L.get("crisp"):
                pr.dot((bx, P.Y_FLOOR), 6 + 14 * u, C["ball"] * 1.5, (1 - u) ** 3 * k * 0.8)

    # ── strobe ghosts (acts 1–3) ──
    sa = win(t, 0.0, 20.6, 0.1, 0.9)
    ghosts(pr, "hero", t, P.T_SPARK + GHOST_DT, 20.0, R, sa)
    tw = win(t, P.T_SPLIT0, 12.8, 0.3, 0.8)
    ghosts(pr, "twin", t, P.T_SPLIT1, 12.3, R * np.sqrt(2) * ss((t - P.T_SPLIT0) / 0.7) ** 0 , sa * tw)

    # ── energy, trace, heat ──
    draw_trace(pr, t, win(t, P.T_SPRING, T_REL + 0.7, 0.3, 0.7))
    draw_energy(pr, t, win(t, 21.2, T_REL + 0.7, 0.8, 0.7))
    draw_heat(pr, t)

    # ── orbit: wedges, path, star ──
    wa = win(t, P.T_EDGE + 0.3, P.T_PEND - 0.4, 0.4, 0.9)
    draw_wedges(pr, t, wa)
    if P.T_EDGE < t < P.T_PEND + 0.5:
        op = D[f"c{P.CHAIN_N}_p"]
        ts = np.linspace(P.T_EDGE, min(t, P.T_PEND), 400)
        pr.polyline(SV(op, ts), 1.3, C["ball"] * 0.8, 0.28 * win(t, P.T_EDGE, P.T_PEND + 0.5, 0.3, 0.8))
    coll = draw_star(pr, t)

    # ── trails ──
    if t < P.T_SPRING:
        trail(pr, "hero", t, L["trail"], C["ball"], 0.7 * hero_vis(t), t_min=P.T_SPARK)
        if P.T_SPLIT1 < t < 12.8:
            trail(pr, "twin", t, L["trail"], C["ball"], 0.6 * tw, t_min=P.T_SPLIT1)
    if T_REL - 0.2 < t < P.T_EDGE + 1:
        for k in range(1, P.CHAIN_N + 1):
            trail(pr, f"c{k}", t, L["trail"] * 0.8, ball_col(warmth(f"c{k}", t)), 0.6, t_min=T_REL)
    if P.T_EDGE <= t < P.T_PEND + 0.3:
        trail(pr, f"c{P.CHAIN_N}", t, L["trail"] * 1.3, C["ball"], 0.8, t_min=P.T_EDGE - 1)

    # ── bodies ──
    endf = 1 - ss((t - 58.9) / 0.9)
    if t < P.T_EDGE + 1.0:
        va = hero_vis(t) * (1 - ss((t - (P.T_EDGE - 0.1)) / 0.8))
        r = R * (0.2 + 0.8 * back((t - P.T_SPARK) / 0.45)) if t < P.T_SPARK + 0.5 else R
        if va > 0:
            draw_body(pr, "hero", t, r, ball_col(warmth("hero", t)), va,
                      glow_p=(abs(vel("hero", t)[0]) / abs(V_REL)) * ss((t - T_REL) / 0.2) if t > T_REL else 0)
    if P.T_SPLIT0 <= t < 12.8:
        rt = R * (1 + (np.sqrt(2) - 1) * back((t - P.T_SPLIT0) / 0.7))
        draw_body(pr, "twin", t, rt, C["ball"], tw)
    if 33.4 < t < P.T_PEND + 0.01:
        for k in range(1, P.CHAIN_N + 1):
            nm = f"c{k}"
            app = back((t - 33.6 - 0.12 * k) / 0.5)
            if app <= 0:
                continue
            last = k == P.CHAIN_N
            fa = 1.0 if last else 1 - ss((t - (P.T_EDGE - 0.1)) / 0.8)
            if fa <= 0:
                continue
            v = abs(vel(nm, t)[0])
            draw_body(pr, nm, t, R * max(app, 0.01), ball_col(warmth(nm, t)), fa,
                      glow_p=(v / abs(V_REL)) if t < P.T_EDGE + 0.5 else 0)

    # ── pendulum ──
    if t >= P.T_PEND - 0.05:
        piv = STAR
        grow = ss((t - P.T_PEND + 0.05) / 0.35)
        twa = ss((t - (P.T_PEND + 0.6)) / 0.8) * endf
        for k, col in ((1, C["twin1"]), (2, C["twin2"]), (0, C["ball"])):
            a = (endf if k == 0 else twa)
            if a <= 0:
                continue
            trail(pr, f"pout{k}", t, L["pend_trail"], col, a * 0.85, t_min=P.T_PEND, n=160)
        for k, col in ((1, C["twin1"]), (2, C["twin2"]), (0, C["ball"])):
            a = (endf if k == 0 else twa)
            if a <= 0:
                continue
            p1, p2 = pos(f"pin{k}", t), pos(f"pout{k}", t)
            m1 = piv + (p1 - piv) * grow
            pr.seg(piv, m1, L["line_px"] + 0.5, C["rod"] if k == 0 else col * 0.8, a * 0.9)
            if grow > 0.5:
                pr.seg(p1, p1 + (p2 - p1) * ss((grow - 0.5) / 0.5), L["line_px"] + 0.5,
                       C["rod"] if k == 0 else col * 0.8, a * 0.9)
            pr.disc(p1, 0.12 * grow, C["rod"] if k == 0 else col, a, spin=0)
            pr.disc(p2, R, C["ball"] if k == 0 else col, a, spin=0)
        pr.ring(piv, 0.09, 1.6, C["rod"], 0.9 * endf * grow, add=0.0)
        pr.dot(piv, 2.5, C["rod"] * 1.5, endf * grow)

    # ── arrows ──
    vs = vscale(t)
    if P.T_SPARK + 0.5 < t < 12.4:
        a = win(t, P.T_SPARK + 0.5, 12.6, 0.5, 0.6)
        p = pos("hero", t)
        pr.arrow(p + [R + 0.02, 0], vel("hero", t) * vs, C["v"], a, label="v")
    if P.T_SPLIT1 < t < 12.4:
        a = win(t, P.T_SPLIT1, 12.6, 0.4, 0.6)
        p = pos("twin", t); rt = R * np.sqrt(2)
        pr.arrow(p + [rt + 0.02, 0], vel("twin", t) * vs, C["v"], a, label="v")
    if P.T_F0 - 0.05 < t < P.T_F1 + 0.4:
        sf = 2.6
        g = back((t - P.T_F0) / 0.4) * (1 - ss((t - P.T_F1) / 0.3))
        for nm, rr, mlab in (("hero", R, "m"), ("twin", R * np.sqrt(2), "2m")):
            p = pos(nm, t)
            Lf = P.F_APP * sf * g
            tail = p - [rr + 0.06 + Lf, 0]
            pr.arrow(tail, [Lf, 0], C["F"], min(g, 1.0), label="F", label_at="mid")
            acc = P.F_APP / (1 if nm == "hero" else 2)
            pr.arrow(p + [-acc * 2.2 * g / 2, rr + 0.2], [acc * 2.2 * g, 0], C["a"], min(g, 1.0), w_px=3.0,
                     label="a", label_at="tip")
    if P.T_SPLIT0 < t < 12.4:                       # mass labels inside the discs
        ma = win(t, P.T_SPLIT0 + 0.3, 12.5, 0.4, 0.5)
        pr.label("m", pos("hero", t), 30, ma)
        pr.label("2m", pos("twin", t), 32, ma * tw)
    if P.T_G - 0.1 < t < P.T_SPRING + 0.2:
        a = win(t, P.T_G - 0.1, P.T_SPRING + 0.2, 0.35, 0.4)
        p = pos("hero", t)
        sg = 0.2
        g = back((t - P.T_G) / 0.45)
        rolling = force("hero", "normal", t)[1] > 0
        pr.arrow(p - [0, R + 0.02], [0, -P.G * sg * g], C["F"], a, label="F", label_at="mid", label_side=-1)
        if rolling:
            pr.arrow(p + [0, R + 0.02], [0, P.G * sg], C["F"], a * 0.9, label="N", label_at="mid", label_side=-1)
        else:
            pr.arrow(p + [R + 0.22, -0.1], [0, -P.G * 0.12 * g], C["a"], a, w_px=3.0, label="a", label_at="mid",
                     label_side=-1)
        if t > 12.9:
            pr.arrow(p + [0.0, 0.0] + [R * 0.7, R * 0.7] * (vel("hero", t) / max(np.linalg.norm(vel("hero", t)), 1e-6)),
                     vel("hero", t) * vs, C["v"], a * win(t, 12.9, 20.0, 0.4, 0.3), label="v")
    if P.T_SPRING - 0.05 < t < T_REL + 0.3:
        a = win(t, P.T_SPRING, T_REL + 0.3, 0.3, 0.3)
        p = pos("hero", t)
        fs = force("hero", "spring", t)
        if abs(fs[0]) > 1e-3:
            d = np.sign(fs[0])
            pr.arrow(p + [d * (R + 0.02), 0.0], fs * 0.16, C["F"], a, label="F", label_at="tip")
        fd = force("hero", "drag", t)
        if abs(fd[0]) > 1e-3:
            d = np.sign(fd[0])
            ad = a * win(t, P.T_D0, P.T_D1 + 0.2, 0.3, 0.3)
            pr.arrow(p + [d * 0.02, R + 0.2], fd * 0.6, C["F"] * 0.85, ad, w_px=3.0, label="drag",
                     label_at="tip", lsize=26)
    # act 6: momentum arrows on the moving balls, Newton III pairs at contacts
    if T_REL - 0.1 < t < P.T_EDGE + 0.2:
        a6 = win(t, T_REL - 0.1, P.T_EDGE + 0.4, 0.2, 0.5)
        first_label = t < T_CHAIN0 + 1.6
        for nm in ["hero", *[f"c{k}" for k in range(1, P.CHAIN_N + 1)]]:
            v = vel(nm, t)
            if abs(v[0]) > 0.05:
                p = pos(nm, t)
                pr.arrow(p + [np.sign(v[0]) * (R + 0.02), 0], v * 0.55, C["p"], a6 * ss(abs(v[0]) / 0.4),
                         label="p")
        for nm in ["hero", *[f"c{k}" for k in range(1, P.CHAIN_N + 1)]]:
            fd = FC_DISP[nm]
            f = S(fd, t)
            if np.linalg.norm(f) > 0.5:
                p = pos(nm, t)
                pr.arrow(p + [0, R + 0.22], f * 0.022, C["F"], a6 * ss(np.linalg.norm(f) / 6),
                         label=("-F" if f[0] < 0 else "F") if (first_label and nm in ("hero", "c1")) else None,
                         label_at="tip", lsize=28)
    # act 7: star gravity ∝ 1/r² and tangent velocity
    if P.T_EDGE - 0.05 < t < P.T_PEND - 0.2:
        a = win(t, P.T_EDGE - 0.05, P.T_PEND - 0.2, 0.4, 0.4)
        p = pos(f"c{P.CHAIN_N}", t)
        Fv = force(f"c{P.CHAIN_N}", "star", t)
        d = Fv / np.linalg.norm(Fv)
        pr.arrow(p + d * (R + 0.02), Fv * 0.085, C["F"], a, label="F", label_at="tip")
        v = vel(f"c{P.CHAIN_N}", t)
        dv = v / np.linalg.norm(v)
        pr.arrow(p + dv * (R + 0.02), v * 0.3, C["v"], a, label="v")

    # ── equations: bottom centre, inside the 5 % safe margin ──
    for key, t0, t1 in EQ_WINDOWS:
        a = win(t, t0, t1, 0.6, 0.5)
        if a > 0:
            lift = (1 - ss((t - t0) / 0.6)) * 0.15
            # act 3's gravity arrows reach below the floor at each bounce, so its equation sits at the top
            ey = cam[1] + cam[2] * 0.5 - cam[2] * 0.095 if key == "eq3" else cam[1] - cam[2] * 0.5 + cam[2] * 0.095
            pr.label(key, (cam[0], ey + lift * cam[2] / 8), 46, a * 0.95)

    prims = pr.out()
    fade = 1 - ss((t - 59.2) / 0.8)
    return cam, prims, fade


def _contact_display():
    """Contact forces last ~3 frames; show them with a short afterglow (peak-hold, τ = 0.2 s)."""
    out = {}
    j0, j1 = P.idx(T_REL) - 2, P.idx(P.T_EDGE) + 2
    decay = np.exp(-1 / (P.FS * 0.2))
    for nm in ["hero", *[f"c{k}" for k in range(1, P.CHAIN_N + 1)]]:
        F = D.get(f"{nm}_F_contact", np.zeros((P.N, 2)))
        Fd = np.zeros((P.N, 2))
        cur = np.zeros(2)
        for j in range(j0, j1):
            cur = cur * decay
            if np.linalg.norm(F[j]) >= np.linalg.norm(cur):
                cur = F[j].copy()
            Fd[j] = cur
        out[nm] = Fd
    return out


FC_DISP = _contact_display()


def framing_report(look="A", fps=30):
    """Check that the moving bodies stay inside the 5 % safe margin in every frame."""
    bad = []
    for i in range(int(DURATION * fps)):
        t = i / fps
        cx, cy, h = camera(t)
        w = h * 16 / 9
        nm = ("hero" if t < T_CHAIN0 else f"c{P.CHAIN_N}") if t < P.T_PEND else "pout0"
        if t < P.T_SPARK:
            continue
        p = pos(nm, t)
        if abs(p[0] - cx) > 0.45 * w or abs(p[1] - cy) > 0.45 * h:
            bad.append(round(t, 2))
    return bad
