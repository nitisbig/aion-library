"""s07 outro: the real 2019 picture (our render, blurred to telescope sharpness), the lesson as a
visual callback (radius → idea → path → picture), and the one thing left out: real black holes spin."""
from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_eq, badge_rs, bh_look

INC, FOV = 84.0, 36.0
DIST = key(T.cut_outro + 0.2, 44.0, 54.0, dur=3.0, ease="easy_ease", lead=0)       # ease back: room for the badges
CAM = dict(dist=DIST, inclination=INC, azimuth=ramp(T.cut_outro, T.end, 13.0, 21.0), fov=FOV, scale_res=2,
           disk_rate=2.0, disk_t0=T.disk + 25.0)          # same camera, gas clock and look as the end of s06
OUT = 1.0 - key(T.next_video + 1.5, 0.0, 1.0, dur=1.9, lead=0)                     # final fade to black


def shadow_radius(dist):
    return float(np.tan(np.arcsin(S.B_C * np.sqrt(1 - 2 / dist) / dist)) / np.tan(np.radians(FOV / 2)) * 4.0)


def funnel_icon():
    """A small Flamm funnel: rings at fixed radii dropped by the exact height, plus four profile lines."""
    g, rs, k = VGroup(), 0.22, 0.95
    drop = lambda r: k * 0.55 * float(S.flamm(1.3, rs) - S.flamm(r, rs))            # noqa: E731
    for r in (1.3, 0.95, 0.65, 0.42, 0.27):
        g.add(Ellipse(width=2 * k * r, height=2 * k * r * 0.36, color=C.muted, stroke_width=C.thin)
              .move_to([0, -drop(r), 0]))
    for a in (0.0, PI):
        rr = np.linspace(0.27, 1.3, 24)
        g.add(VMobject(stroke_color=C.muted, stroke_width=C.thin).set_points_as_corners(
            [[k * r * np.cos(a), -drop(r), 0] for r in rr]))
    g.add(VMobject(stroke_color=C.light, stroke_width=C.thin + 1).set_points_smoothly(
        [[-1.2, 0.03, 0], [-0.55, -0.18, 0], [0.15, -0.3, 0], [0.75, -0.08, 0], [1.2, 0.18, 0]]))
    return g


@scene(T.cut_outro, T.end)
def s07_outro(s):
    # ── our own image, blurred to what a telescope the size of the Earth can resolve ──
    blur = keys((T.telescope - 0.4, 0.0), (T.telescope + 1.8, 4.0), (T.as_said - 0.4, 4.0), (T.as_said + 1.0, 0.0),
                default_ease="easy_ease")
    look = dict(bh_look(), u_ring=0.7)
    stars = keys((T.telescope - 0.4, 1.0), (T.telescope + 1.4, 0.1), (T.as_said - 0.4, 0.1), (T.as_said + 1.0, 1.0))
    s.add(BlackHoleLayer(**CAM, **look, sky="galaxy", sky_center=(INC, 6.0), z=-10, opacity=OUT, name="full",
                         u_stars=stars, u_skyAmt=stars,           # a telescope sees the hole, not the star field
                         fx=[Bloom(C.bloom, threshold=0.9), Tonemap(), Blur(radius=blur)]))
    # "a map of where straight lines go": the same view with the sky's coordinate grid, bent by the hole
    s.add(BlackHoleLayer(**CAM, **look, sky="grid", u_gas=0.3, z=-9, name="map",
                         opacity=fade(T.map - 0.5, to=0.8, dur=1.2, out=T.l_radius - 0.2, out_dur=1.0, lead=0),
                         fx=[Bloom(C.bloom, threshold=0.9), Tonemap()]))

    m = s.manim(z=3)
    note = Label("our simulation, blurred to the telescope's sharpness", color=C.muted, size=26)
    note.to_edge(DOWN, buff=C.margin + 0.1)
    m.play(FadeIn(note, shift=0.15 * UP), at=T.telescope + 1.6, dur=0.7)
    m.play(FadeOut(note), at=T.as_said - 0.3, dur=0.7)

    # ── the lesson, as a callback: radius → idea → path → picture ────────
    y = -3.12
    radius = badge_rs().move_to([-4.7, y, 0])
    idea = funnel_icon().move_to([0.0, y + 0.05, 0])
    path_ = badge_eq().move_to([4.4, y, 0])
    m.play(FadeIn(radius, shift=0.2 * UP), at=T.l_radius, dur=0.6)
    m.play(FadeIn(idea, shift=0.2 * UP), at=T.l_idea, dur=0.6)
    m.play(FadeIn(path_, shift=0.2 * UP), at=T.l_path, dur=0.6)
    target = np.array([0.0, 0.0, 0.0])
    m.play(*[FadeOut(b, target_position=target, scale=0.25) for b in (radius, idea, path_)], at=T.l_picture + 0.2,
           dur=1.3, ease="easy_ease")

    # ── one thing left out: real black holes spin → the shadow goes lopsided ──
    R = shadow_radius(54.0)
    edge = Circle(radius=R, color=C.shadow, stroke_width=C.thin + 1)
    a = np.linspace(0, TAU, 120)
    flat = np.where(np.cos(a) < 0, 0.4, 1.0)                           # a D-shape: the side turning toward us is flattened
    lop = VMobject(stroke_color=C.shadow, stroke_width=C.stroke).set_points_smoothly(
        [[R * (0.32 + flat[i] * np.cos(a[i])), R * np.sin(a[i]), 0] for i in range(len(a))])
    spin_arrow = CurvedArrow([-0.55 * R, 1.35 * R, 0], [0.55 * R, 1.35 * R, 0], angle=-1.3, color=C.text,
                             stroke_width=C.thin + 1, tip_length=0.18)
    sketch = Label("a spinning hole · sketch, not computed", color=C.muted, size=26).to_edge(DOWN, buff=C.margin + 0.1)
    m.play(Create(edge), at=T.left_out, dur=1.0)
    m.play(Create(spin_arrow), at=T.spin, dur=0.9)
    m.play(ReplacementTransform(edge, lop), FadeIn(sketch), at=T.lopsided - 0.5, dur=1.4, ease="easy_ease")
    m.play(FadeOut(lop), FadeOut(spin_arrow), FadeOut(sketch), at=T.next_video + 1.4, dur=1.2)
