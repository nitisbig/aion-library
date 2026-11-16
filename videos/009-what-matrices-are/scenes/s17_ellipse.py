"""Ch7 · A rotation, a stretch, and a rotation (1/2): the hero A turns a circle of arrows into an ellipse; its axes come
from two perpendicular inputs. Replayed in three steps (rotate −30.1°, stretch 4.13 / 0.97, rotate +41.4°) it lands on
exactly the same grid: A = UΣVᵀ. In 3D (the hook box H) a lit sphere becomes an ellipsoid the same way."""
from scipy.spatial.transform import Rotation

from aion import *

from beats import T
from shots import (A, FRAME, I2, I3, Cam, Mat, arrow, backdrop, backing, finish, grid_lines, live, pt, rail, rot2,
                   shade, tex)

E = "smooth"
O, U_ = (1.75, -0.4), 0.9
NA = 24                                                 # arrows on the circle
H3 = np.array([[2, 1, 0], [0, 1, 1], [1, 0, 1]], float)  # the hook box


def proper_svd2(M):
    """U, sigma, Vt of a 2x2 with U, Vt proper rotations (first columns pointing right): returns their angles too."""
    U, s, Vt = np.linalg.svd(M)
    for i in range(2):
        if U[0, i] < 0:
            U[:, i] *= -1
            Vt[i] *= -1
    if np.linalg.det(U) < 0:
        U[:, 1] *= -1
        Vt[1] *= -1
    return U, s, Vt, np.degrees(np.arctan2(U[1, 0], U[0, 0])), np.degrees(np.arctan2(Vt[1, 0], Vt[0, 0]))


U2, S2, VT2, TH_U, TH_V = proper_svd2(A)                 # +41.4°, −30.1°; sigma 4.131, 0.968
assert np.allclose(rot2(TH_U) @ np.diag(S2) @ rot2(TH_V), A)
V1, V2 = VT2[0], VT2[1]                                 # the perpendicular inputs that land on the axes
U3, S3, VT3 = np.linalg.svd(H3)
assert np.linalg.det(U3) > 0 and np.linalg.det(VT3) > 0


@scene(T.cut_ch7, T.cut_photo_svd)
def s17_ellipse(s):
    backdrop(s)
    t3 = T.sphere - 0.6                                 # 2D out, 3D in
    out2 = keys((t3, 1.0), (t3 + 0.7, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=out2)
    m = s.manim(z=1, opacity=out2)
    g = s.manim(z=3, opacity=out2)
    end = keys((T.cut_photo_svd - 0.7, 1.0), (T.cut_photo_svd - 0.05, 0.0), lead=0)
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 6)

    ghost.play(FadeIn(grid_lines(I2, O, U_, FRAME, color=C.ghost)), at=T.cut_ch7 + 0.4, dur=0.8)

    # ── the score: A forward, back, forward (follow back), rest; then rotate, stretch, rotate ──
    p0, p1 = T.circle + 2.1, T.circle + 4.1             # "apply our matrix"
    b0, b1 = T.follow_back + 0.6, T.follow_back + 2.4   # follow them back
    f0, f1 = T.right_angles + 1.2, T.right_angles + 2.8  # ... they land exactly on those axes
    z0, z1 = T.three_steps - 0.6, T.three_steps + 1.2   # back to rest
    u = keys((p0, 0.0), (p1, 1.0, E), (b0, 1.0), (b1, 0.0, E), (f0, 0.0), (f1, 1.0, E), (z0, 1.0), (z1, 0.0, E),
             lead=0)
    a0, a1 = T.rot1 + 0.5, T.rot1 + 2.1
    s0, s1 = T.stretch2 + 0.4, T.stretch2 + 2.2
    r0, r1 = T.rot2 + 0.6, T.rot2 + 2.3
    ka = keys((a0, 0.0), (a1, 1.0, E), lead=0)
    kb = keys((s0, 0.0), (s1, 1.0, E), lead=0)
    kc = keys((r0, 0.0), (r1, 1.0, E), lead=0)

    def M(t):
        if t < a0:
            return I2 + u(t) * (A - I2)
        st = np.diag([1 + kb(t) * (S2[0] - 1), 1 + kb(t) * (S2[1] - 1)])
        return rot2(TH_U * kc(t)) @ st @ rot2(TH_V * ka(t))
    assert np.allclose(M(r1 + 1), A)

    circ = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0, 2 * np.pi, 97)])
    dirs = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0, 2 * np.pi, NA, endpoint=False)])
    c_op = keys((T.circle, 0.0), (T.circle + 1.0, 1.0), lead=0)
    hl_op = keys((T.follow_back + 0.1, 0.0), (T.follow_back + 0.5, 1.0), lead=0)
    fan_op = keys((T.follow_back, 1.0), (T.follow_back + 0.5, 0.35), lead=0)   # the 24 arrows step back

    def stage(t):
        Mt = M(t)
        z = pt(O, U_, (0, 0))
        out = VGroup(grid_lines(Mt, O, U_, FRAME, opacity=0.4))
        co = c_op(t)
        if co > 0.01:
            fo = co * fan_op(t)
            out.add(VMobject(stroke_color=C.sigma, stroke_width=C.stroke, stroke_opacity=co)
                    .set_points_as_corners([pt(O, U_, Mt @ p) for p in circ]))
            for d in dirs:
                out.add(arrow(z, pt(O, U_, Mt @ d), C.sigma, width=C.thin + 0.8, tip=0.14, opacity=fo))
        ho = hl_op(t)
        if ho > 0.01:
            for v in (V1, V2):
                out.add(arrow(z, pt(O, U_, Mt @ v), C.sigma, width=C.stroke + 1.5, opacity=ho))
        return out
    wins = [(T.circle, T.circle + 1.1), (p0, p1), (T.follow_back, b1), (f0, f1), (z0, z1), (a0, a1), (s0, s1),
            (r0, r1)]
    m.add(grid_lines(I2, O, U_, FRAME, opacity=0.4), at=T.cut_ch7 + 0.4)
    live(m, stage, *wins)

    # the ellipse's two axes (at A): longest and shortest, at right angles; labelled σ₁, σ₂
    ax1 = Line(pt(O, U_, -S2[0] * U2[:, 0]), pt(O, U_, S2[0] * U2[:, 0]), color=C.sigma, stroke_width=C.stroke + 2)
    ax2 = Line(pt(O, U_, -S2[1] * U2[:, 1]), pt(O, U_, S2[1] * U2[:, 1]), color=C.sigma, stroke_width=C.stroke + 2)
    ax_op = keys((T.follow_back, 1.0), (T.follow_back + 0.5, 0.45), lead=0)
    g.play(Create(ax1), at=T.longest + 0.1, dur=0.7)
    g.play(Create(ax2), at=T.longest + 1.2, dur=0.5)
    l1 = tex(r"\sigma_1", size=48, color=C.sigma).move_to(pt(O, U_, 1.12 * S2[0] * U2[:, 0]) + np.array([0.15, 0.3, 0]))
    l2 = tex(r"\sigma_2", size=48, color=C.sigma).move_to(pt(O, U_, -1.0 * S2[1] * U2[:, 1]) + np.array([0.35, 0.3, 0]))
    g.play(FadeIn(l1, scale=1.3), FadeIn(l2, scale=1.3), at=T.longest + 2.0, dur=0.5, ease="out_back")
    g.play(VGroup(ax1, ax2).animate.set_stroke(opacity=0.45), at=T.follow_back, dur=0.5)
    ra = RightAngle(Line(pt(O, U_, (0, 0)), pt(O, U_, V1)), Line(pt(O, U_, (0, 0)), pt(O, U_, V2)), length=0.18,
                    color=C.sigma, stroke_width=2)
    g.play(Create(ra), at=b1 + 0.1, dur=0.4)
    g.play(FadeOut(ra), at=f0 - 0.3, dur=0.3)

    # ── the panel: A, then A = U Σ Vᵀ built right to left as the steps play ──
    Am = Mat(A, size=44, h_buff=0.85, v_buff=0.7)
    rowA = VGroup(tex("A", "=", size=48), Am).arrange(RIGHT, buff=0.2)
    usv = tex("A", "=", "U", r"\Sigma", r"V^{\top}", size=60)
    sig = tex(r"\sigma_1", r"\approx", f"{S2[0]:.2f}", r"\quad", r"\sigma_2", r"\approx", f"{S2[1]:.2f}", size=40,
              color=C.sigma)
    stack = VGroup(rowA, usv, sig).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    stack.move_to([-7.11 + C.margin + 0.35 + stack.width / 2, 3.55 - C.margin - stack.height / 2, 0])
    panel = backing(stack, pad=0.28)
    hb.play(FadeIn(panel), at=T.deepest, dur=0.5)
    hud.play(FadeIn(rowA), at=T.deepest + 0.2, dur=0.6)
    hud.play(FadeIn(usv[4], shift=0.1 * DOWN), at=a0 + 0.2, dur=0.5)
    hud.play(FadeIn(usv[3], shift=0.1 * DOWN), at=s0 + 0.2, dur=0.5)
    hud.play(FadeIn(usv[2], shift=0.1 * DOWN), at=r0 + 0.2, dur=0.5)
    hud.play(FadeIn(usv[:2]), at=T.rsr + 1.8, dur=0.5)
    for i, tt in ((4, T.rsr), (3, T.rsr + 0.7), (2, T.rsr + 1.5)):
        hud.play(Indicate(usv[i], color=C.sigma, scale_factor=1.25), at=tt, dur=0.6)
    hud.play(FadeIn(sig), at=T.singular_values + 0.2, dur=0.6)
    g.play(Flash(pt(O, U_, (0, 0)), color=C.sigma, line_length=0.25, flash_radius=0.4), at=r1 + 0.1, dur=0.6)

    # ── 3D: a lit sphere becomes an ellipsoid, the same three steps (the hook box H) ──
    w3 = s.manim(z=2, opacity=end)
    az = keys((t3, -40.0), (T.cut_photo_svd, -22.0, "linear"), lead=0)
    q0 = T.sphere + 1.2
    ka3 = keys((q0, 0.0), (q0 + 1.1, 1.0, E), lead=0)
    kb3 = keys((q0 + 1.3, 0.0), (q0 + 2.4, 1.0, E), lead=0)
    kc3 = keys((q0 + 2.6, 0.0), (q0 + 3.7, 1.0, E), lead=0)
    rv_v, rv_u = Rotation.from_matrix(VT3).as_rotvec(), Rotation.from_matrix(U3).as_rotvec()

    def M3(t):
        st = np.diag(1 + kb3(t) * (S3 - 1))
        return Rotation.from_rotvec(rv_u * kc3(t)).as_matrix() @ st @ Rotation.from_rotvec(rv_v * ka3(t)).as_matrix()
    assert np.allclose(M3(q0 + 10), H3)

    nl, nm = 12, 24
    th = np.linspace(0, np.pi, nl + 1)
    ph = np.linspace(0, 2 * np.pi, nm + 1)
    sph = np.array([[[np.sin(a) * np.cos(b), np.sin(a) * np.sin(b), np.cos(a)] for b in ph] for a in th])
    s3_op = keys((t3 + 0.5, 0.0), (t3 + 1.2, 1.0), lead=0)
    ax3_op = keys((T.sphere + 0.6, 0.0), (T.sphere + 1.1, 1.0), lead=0)

    def body(t):
        o = s3_op(t)
        if o < 0.01:
            return VGroup()
        cam = Cam(az(t), 20.0, origin=(1.4, -0.5), unit=1.25)
        Mt = M3(t)
        Minv_t = np.linalg.inv(Mt).T
        eye = cam.eye()
        faces = []
        for i in range(nl):
            for j in range(nm):
                q = [sph[i, j], sph[i + 1, j], sph[i + 1, j + 1], sph[i, j + 1]]
                ctr = sum(q) / 4
                nrm = Minv_t @ ctr
                if nrm @ eye <= 0:
                    continue
                P = [Mt @ p for p in q]
                col = shade(C.sigma, nrm)
                faces.append((cam.depth(Mt @ ctr), Polygon(*[cam.scr(p) for p in P], fill_color=col, fill_opacity=o,
                                                         stroke_color=C.bg, stroke_width=0.8, stroke_opacity=0.5 * o)))
        faces.sort(key=lambda f: -f[0])
        out = VGroup(*[f[1] for f in faces])
        ao = ax3_op(t) * o
        if ao > 0.01:
            for k in range(3):
                a_ = Mt @ VT3[k]
                out.add(Line(cam.scr(-1.35 * a_), cam.scr(1.35 * a_), color=C.text, stroke_width=C.stroke,
                             stroke_opacity=ao))
        return out
    w3.redraw(body, during=(t3 + 0.5, T.cut_photo_svd))
    finish(s)
