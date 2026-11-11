"""s06 chapter 5: building the image. Rays run backwards from a camera; each pixel's ray ends in the
hole (shadow), in the sky (bent stars) or on the disk. The top arc is the far side of the same disk."""
from aion import *
from aion.layers.blackhole import camera_basis
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_eq, bh_look, brief, glow_fx, scan_tint

RC, INC, FOV, AZ = 30.0, 84.0, 36.0, 4.0                  # camera: distance (M), inclination, vertical fov, azimuth
TH = float(np.tan(np.radians(FOV / 2)))
PC, PH_ = np.array([2.85, -0.35, 0.0]), 4.3               # image panel: centre and height (16:9)
HS, KM = np.array([-3.75, -0.35, 0.0]), 0.094             # side view: hole centre, frame units per M
EL = np.radians(90.0 - INC)                               # camera elevation above the disk plane
E1 = np.array([-np.cos(EL), np.sin(EL)])                  # hole → camera, in the side view
E2 = np.array([np.sin(EL), np.cos(EL)])                   # "up" on the camera's screen
CAM = HS + KM * RC * np.array([E1[0], E1[1], 0.0])
R_SHADOW = float(np.tan(np.arcsin(S.B_C * np.sqrt(1 - 2 / RC) / RC)) / TH * PH_ / 2)   # shadow radius in the panel

t_grow = T.brighter - 1.3                                 # the panel grows to fill the frame
GROW = key(t_grow, 0.0, 1.0, dur=2.4, ease="easy_ease", lead=0)


def back_ray(A):
    """Light traced backwards from the camera at angle A (rad) above the line to the hole.
    Returns (side-view points in frame units, fate) with fate in {"hole", "front", "back", "under", "sky"}."""
    b = RC * np.sin(abs(A)) / np.sqrt(1 - 2 / RC)
    ph, u, fate = S.orbit(max(b, 1e-3), rs=2.0, phi_max=10 * PI, h=0.003)
    i_peak = int(np.argmax(u))
    i0 = int(np.searchsorted(u[: i_peak + 1], 1.0 / RC))  # where the incoming branch passes the camera
    psi = ph[i0:] - np.interp(1.0 / RC, u[: i_peak + 1], ph[: i_peak + 1])
    r = 1.0 / np.maximum(u[i0:], 1e-9)
    xy = r[:, None] * (np.cos(psi)[:, None] * E1 + np.sign(A) * np.sin(psi)[:, None] * E2)
    xy = np.vstack([RC * E1, xy])
    r = np.hypot(xy[:, 0], xy[:, 1])
    out = "hole" if fate == "capture" else "sky"
    cross = np.where((np.sign(xy[:-1, 1]) != np.sign(xy[1:, 1])) & (r[1:] > 6.0) & (r[1:] < 19.0))[0]
    end = len(xy)
    if len(cross):                                        # lands on the disk
        j = cross[0]
        f = xy[j, 1] / (xy[j, 1] - xy[j + 1, 1])
        hit = xy[j] + f * (xy[j + 1] - xy[j])
        xy, end = np.vstack([xy[: j + 1], hit]), j + 2
        out = "front" if hit[0] < 0 else ("back" if xy[j, 1] > 0 else "under")
    else:
        far = np.where(r > 46.0)[0]
        far = far[far > 2]
        if len(far):
            xy = xy[: far[0]]
    p = np.column_stack([HS[0] + KM * xy[:, 0], HS[1] + KM * xy[:, 1], np.zeros(len(xy))])
    keep = (p[:, 0] > -6.95) & (p[:, 0] < -1.25) & (np.abs(p[:, 1] - HS[1]) < 2.3)
    bad = np.where(~keep)[0]
    return (p[: bad[0]] if len(bad) else p), out


def pixel(A):
    """Where the ray at angle A lands in the image panel (centre column)."""
    return PC + np.array([0.0, np.tan(A) / TH * PH_ / 2, 0.0])


def find(kind, r_goal, lo, hi, n=240):
    """The angle whose backward ray has fate `kind`, landing nearest r_goal (M) on the disk."""
    best, best_d = None, 1e9
    for A in np.linspace(lo, hi, n):
        p, out = back_ray(A)
        if out == kind:
            d = abs(np.hypot(*(p[-1, :2] - HS[:2])) / KM - r_goal)
            if d < best_d:
                best, best_d = A, d
    return best


def in_panel(xy, grow=0.0):
    """Full-frame coordinates (frame units, 8 high) → the panel (or the grown, full-frame panel)."""
    k = (PH_ / 8.0) * (1 - grow) + grow
    return np.column_stack([PC[0] * (1 - grow) + k * xy[:, 0], PC[1] * (1 - grow) + k * xy[:, 1], np.zeros(len(xy))])


@scene(T.cut_ch5, T.cut_outro)
def s06_image(s):
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim(z=3)
    brief(m, badge_eq(), T.cut_ch5 + 2.4)

    # ── the image: two looks of the same ray-traced camera ───────────────
    cam = dict(dist=key(t_grow, RC, 44.0, dur=2.6, ease="easy_ease", lead=0), inclination=INC,
               azimuth=ramp(T.cut_ch5, T.cut_outro, AZ, AZ + 9.0), fov=FOV, height=PH_, scale_res=2, z=-10,
               pos=key(t_grow, PC[:2], [0.0, 0.0], dur=2.4, ease="easy_ease", lead=0),
               scale=key(t_grow, 1.0, 8.0 / PH_, dur=2.4, ease="easy_ease", lead=0),
               disk_rate=2.0, disk_t0=T.disk + 25.0,                 # gas least sheared mid-chapter
                fx=[Bloom(C.bloom, threshold=0.9), Tonemap()])
    t_x = T.disk - 0.3                                           # crossfade: bare sky → sky with the disk
    s.add(BlackHoleLayer(**cam, sky="grid", u_gas=0.0, u_ring=0.0, name="sky_only",
                         opacity=fade(T.stars - 1.2, dur=0.5, out=t_x + 1.6, out_dur=1.2, lead=0),
                         u_reveal=key(T.stars - 1.0, 0.0, 1.0, dur=3.4, ease="easy_ease", lead=0),
                         u_scanTint=scan_tint(1.5)))
    s.add(BlackHoleLayer(**cam, sky="galaxy", sky_center=(INC, AZ + 2.0), name="full",
                         **bh_look(),
                         opacity=fade(t_x + 0.4, dur=1.2, lead=0),
                         u_gas=key(t_x + 0.6, 0.0, 1.0, dur=2.6, ease="easy_ease", lead=0),
                         u_ring=key(T.thin_line - 0.6, 0.12, 0.7, dur=1.0, lead=0)))

    # ── side view: the hole from chapter 4 moves left; a camera looks at it ──
    hole = Circle(radius=2 * KM, stroke_color=C.horizon, stroke_width=C.thin + 1, fill_color=C.bg, fill_opacity=1.0)
    hole.move_to(HS)
    old_edge = Circle(radius=S.critical_b(1.0) * 0.55, color=C.shadow, stroke_width=C.thin + 1).move_to([0.3, -0.3, 0])
    old_in = DashedVMobject(Circle(radius=0.55, color=C.horizon, stroke_width=C.thin + 1), num_dashes=28)
    old_in.move_to([0.3, -0.3, 0])
    m.add(old_edge, old_in)
    m.play(FadeOut(old_edge, target_position=HS, scale=0.3), ReplacementTransform(old_in, hole),
           at=T.cut_ch5 + 0.2, dur=1.2, ease="easy_ease")
    cam_dot = Dot(radius=0.1, color=C.text).move_to(CAM)
    look = np.array([-E1[0], -E1[1], 0.0])
    up2 = np.array([E2[0], E2[1], 0.0])
    fov_lines = VGroup(*[Line(CAM, CAM + 1.5 * (look + sg * TH * up2), color=C.muted, stroke_width=C.thin)
                         for sg in (1, -1)])
    cam_lab = Label("camera", color=C.muted, size=26).move_to(CAM + [0.35, -0.75, 0])
    m.play(FadeIn(cam_dot, scale=0.5), Create(fov_lines), FadeIn(cam_lab), at=T.camera, dur=0.8)

    frame = Rectangle(width=PH_ * 16 / 9, height=PH_, stroke_color=C.faint, stroke_width=C.thin).move_to(PC)
    m.play(Create(frame), at=T.each_pixel - 0.4, dur=1.0)
    A0 = 0.265                                                   # the first pixel we follow
    px = Square(side_length=0.16, stroke_color=C.text, stroke_width=C.thin + 1).move_to(pixel(A0))
    link = DashedLine(CAM, pixel(A0), color=C.muted, stroke_width=C.thin, stroke_opacity=0.6)
    m.play(FadeIn(px, scale=2.5), at=T.each_pixel + 0.3, dur=0.6)
    aim = Arrow(CAM, CAM + 1.3 * (np.cos(A0) * look + np.sin(A0) * up2), buff=0.0, color=C.text,
                stroke_width=C.thin + 1, max_tip_length_to_length_ratio=0.18)
    m.play(Create(link), GrowArrow(aim), at=T.each_pixel + 1.6, dur=0.9)
    q = Eqn("?", size=64).next_to(px, RIGHT, buff=0.2)
    m.play(FadeIn(q, scale=0.6), at=T.backwards - 3.4, dur=0.5, ease="out_back")
    m.play(FadeOut(q), FadeOut(aim), at=T.backwards, dur=0.5)

    def trace(A, t0, dur, t_out, color=None, width=None):
        """Draw a backward ray progressively from the camera; fade it at t_out."""
        p, out = back_ray(A)

        def f(t):
            u = float(np.clip((t - t0) / dur, 0.0, 1.0))
            op = float(1.0 - key(t_out, 0.0, 1.0, dur=0.6, lead=0)(t))
            return VMobject(stroke_color=color or C.light, stroke_width=width or C.stroke, stroke_opacity=op) \
                .set_points_as_corners(p[: max(int(u * len(p)), 2)])
        h = glow.redraw(f, during=(t0, t_out + 0.7))
        glow.remove(h, at=t_out + 0.7)
        return p, out

    def mark(A, t0, t_out, fill=None):
        sq = Square(side_length=0.16, stroke_color=C.text, stroke_width=C.thin + 1, fill_color=fill or C.bg,
                    fill_opacity=1.0 if fill else 0.0).move_to(pixel(A))
        ln = DashedLine(CAM, pixel(A), color=C.muted, stroke_width=C.thin, stroke_opacity=0.5)
        m.play(FadeIn(sq, scale=2.5), Create(ln), at=t0, dur=0.6)
        m.play(FadeOut(sq), FadeOut(ln), at=t_out, dur=0.5)

    # run the light backwards: start a ray at the pixel and let the equation bend it
    trace(A0, T.start_ray + 0.4, 4.0, T.fall_in - 1.0)
    m.play(FadeOut(px), FadeOut(link), at=T.fall_in - 1.0, dur=0.5)

    # some rays fall into the hole → those pixels stay black → the shadow
    for i, A in enumerate((0.03, -0.06, 0.1, -0.13, 0.15)):
        trace(A, T.fall_in - 0.6 + 0.35 * i, 1.6, T.stars - 1.6, width=C.thin + 1)
        mark(A, T.fall_in + 0.6 + 0.35 * i, T.shadow + 1.2)
    shadow = Circle(radius=R_SHADOW, color=C.shadow, stroke_width=C.thin + 1).move_to(PC)
    m.play(Create(shadow), at=T.shadow - 0.3, dur=1.2, ease="easy_ease")
    sh_lab = Eqn(r"b = 2.6\,r_s", colors={"r_s": C.horizon}, size=40).move_to(PC + [0.0, R_SHADOW + 0.4, 0])
    sh_lab[0].set_color(C.shadow)
    m.play(FadeIn(sh_lab, shift=0.15 * UP), at=T.shadow + 1.3, dur=0.6)
    m.play(FadeOut(sh_lab), FadeOut(shadow), at=T.stars - 1.3, dur=0.6)

    # some rays escape to the stars, but arrive bent
    for i, A in enumerate((0.3, -0.29, 0.245, -0.235)):
        trace(A, T.stars - 0.4 + 0.5 * i, 2.4, T.disk - 0.9, width=C.thin + 1)

    # ── now add the disk ─────────────────────────────────────────────────
    disk = VGroup(*[Line(HS + [sg * 6 * KM, 0, 0], HS + [sg * 19 * KM, 0, 0], color=C.disk, stroke_width=C.stroke + 2)
                    for sg in (-1, 1)])
    m.play(Create(disk[0]), Create(disk[1]), at=T.disk, dur=1.2)
    A_front = find("front", 11.0, -0.3, -0.01)
    A_back = find("back", 10.0, 0.16, 0.3)
    A_under = find("under", 9.0, -0.3, -0.16)
    A_ring = float(np.arcsin(S.B_C * 1.0015 * np.sqrt(1 - 2 / RC) / RC))
    trace(A_front, T.front - 0.9, 1.8, T.follow_ray - 0.7)
    mark(A_front, T.front + 0.9, T.follow_ray - 0.7)

    # the ray aimed just above the hole: over the top, down behind, onto the far side
    trace(A_back, T.follow_ray + 0.4, T.back - 3.0 - (T.follow_ray + 0.4), T.underside - 0.9)
    mark(A_back, T.back - 0.6, T.underside - 0.9)

    def arc_curve(order, lo, hi):
        pos, right, up, fwd = camera_basis(RC, INC, AZ)
        pts = S.disk_image(16.5, pos, right, up, fwd, fov_deg=FOV, order=order, n=361)[lo:hi]
        pts = pts[np.isfinite(pts[:, 0])]
        return VMobject(stroke_color=C.text, stroke_width=C.thin + 1).set_points_smoothly(in_panel(pts))
    arc = arc_curve(0, 6, 175)                                   # the far side of the disk, lifted over the hole
    over = s.manim(fx=[glow_fx(C.text, 0.8)], z=4)
    over.play(Create(arc), at=T.the_arc - 0.2, dur=1.5, ease="easy_ease")
    over.play(FadeOut(arc), at=T.underside - 0.8, dur=0.6)

    # beneath it: the underside, seen from below
    trace(A_under, T.underside - 0.9, 2.4, T.thin_line - 0.8)
    mark(A_under, T.underside + 1.0, T.thin_line - 0.8)

    # the thin ring: light that circled the photon sphere before escaping toward us
    ring = Circle(radius=R_SHADOW, color=C.ring, stroke_width=C.thin + 1).move_to(PC)
    over.play(Create(ring), at=T.thin_line, dur=1.2)
    over.play(FadeOut(ring), at=T.circled + 1.6, dur=0.7)
    trace(A_ring, T.circled - 1.2, 3.0, t_grow - 0.3)

    # ── the image takes the whole frame; one side is brighter ────────────
    side = VGroup(hole, cam_dot, fov_lines, cam_lab, disk, frame)
    m.play(FadeOut(side), at=t_grow - 0.3, dur=0.8)
    toward = Label("gas moving toward us", color=C.text, size=26).move_to([-4.2, -2.15, 0])
    away = Label("moving away", color=C.muted, size=26).move_to([4.6, -1.75, 0])
    m.play(FadeIn(toward, shift=0.15 * UP), at=T.rushing - 0.4, dur=0.6)
    m.play(FadeIn(away, shift=0.15 * UP), at=T.rushing + 2.0, dur=0.6)
    m.play(FadeOut(toward), FadeOut(away), at=T.reason - 1.0, dur=0.9)
