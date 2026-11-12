"""s00 voyage: one unbroken shot from deep space down to the edge of the shadow, then the quote on black."""
import numpy as np

from aion import *
from aion.comp.comp import hex_to_linear
from aion.core.track import Track

import flight as F
from beats import T
from voyage import VoyageLayer


def bh_look():
    """How the active design colours the disk (same tokens as video 004)."""
    return dict(u_Tpeak=C.bh_T, u_beam=C.bh_beam, u_shift=C.bh_shift, u_gain=C.bh_gain)


def nova_light(t):
    """Supernova light curve: a 0.3 s rise, then a slow exponential fade."""
    a = t - T.nova
    return 0.0 if a < 0 else float(1.6 * min(a / 0.3, 1.0) ** 2 * np.exp(-max(a - 0.3, 0.0) / 4.0))


LY0 = 1500.0     # the story's scale: the shot opens 1,500 light-years out (the flight path is in M, not ly)


def light_years(t):
    """Estimated distance still to go, in light-years: 1,500 at the first frame, a few light-days at the disk.
    It follows the camera's real distance from the hole, so it falls fastest in the dive."""
    d0, d = F.pose(0.0)["dist"], F.pose(t)["dist"]
    return LY0 * ((d - 20.0) / (d0 - 20.0)) ** 1.6


def clock(t):
    """`d ≈ 1,240 ly` in the top-right corner, left-anchored so the digits never shift the label."""
    ly = light_years(t)
    lab = Eqn(r"d \approx", size=34, color=C.muted)
    num = DecimalNumber(ly, num_decimal_places=0 if ly >= 100 else 1 if ly >= 10 else 2, group_with_commas=True,
                        font_size=34, color=C.text)
    unit = Tex("light-years", font_size=30, color=C.muted)
    lab.move_to([3.55, 3.38, 0], aligned_edge=LEFT)
    num.next_to(lab, RIGHT, buff=0.2).align_to(lab, DOWN)
    unit.next_to(num, RIGHT, buff=0.14).align_to(lab, DOWN)
    show = float(np.clip((t - T.start) / 1.0, 0, 1) * np.clip((T.black - 0.3 - t) / 0.8, 0, 1))
    return VGroup(lab, num, unit).set_opacity(show)      # fades in with the picture, out before the black


@scene(T.start, T.end)
def s00_voyage(s):
    s.solid(C.bg, z=-200)
    cam = {k: Track(lambda t, k=k: F.pose(t)[k], label=f"flight.{k}") for k in F.pose(0.0)}

    # ── where things are on the sky: each object is placed where the camera looks at its beat ──
    neb_a = F.sky_dir(T.start, -0.22, 0.10)[0]
    snr, snr1, snr2 = F.sky_dir(T.remnant, 0.26, -0.02)
    psr, psr1, psr2 = F.sky_dir(T.pulsar, -0.04, 0.16)
    neb_b = F.sky_dir(T.centred - 0.8, 0.30, -0.30)[0]
    gal = F.hole_dir(T.einstein)                             # exactly behind the hole on that beat
    _, gal1, gal2 = F.sky_dir(T.einstein)
    a = np.radians(35.0)                                     # the galaxy's long axis, tilted on the sky
    gal1, gal2 = np.cos(a) * gal1 + np.sin(a) * gal2, -np.sin(a) * gal1 + np.cos(a) * gal2
    nova = F.sky_dir(T.nova + 1.1, 0.17, 0.085)[0]           # the orbit carries it behind the hole ~2 s later

    # ── the planet: a real position beside the flight path, so the camera's own motion sweeps it past ──
    pos, right, up, fwd = F.basis(T.start + 0.5)
    planet = pos + 450.0 * fwd - 40.0 * right - 130.0 * up        # closest approach 1.6 radii: it never fills the frame
    sun = 0.80 * right + 0.38 * up + 0.30 * fwd
    axis = 0.30 * right + 0.90 * up - 0.32 * fwd

    plunge = key(T.black, 0.0, 1.0, dur=T.black - T.skim, ease="in_cubic")     # 0 → 1 from the skim to black
    s.add(VoyageLayer(
        **cam, sky="galaxy", sky_center=F.SKY_CENTER, scale_res=2, z=-10,
        disk_rate=F.DISK_RATE, disk_t0=F.DISK_T0, **bh_look(),
        v_gain=1.0, v_time=Track(lambda t: t, label="voyage.t"),
        v_nebA=neb_a, v_nebB=neb_b, v_snr=snr, v_snrT1=snr1, v_snrT2=snr2,
        v_gal=gal, v_galT1=gal1, v_galT2=gal2, v_psr=psr, v_psrT1=psr1, v_psrT2=psr2,
        v_plC=planet, v_plR=80.0, v_plAxis=axis / np.linalg.norm(axis), v_plSun=sun / np.linalg.norm(sun),
        v_plAmt=key(T.centred, 1.0, 0.0, dur=0.5),          # behind the camera long before
        u_snDir=nova, u_snI=Track(nova_light, label="voyage.nova"),
        u_snAge=Track(lambda t: t - T.nova, label="voyage.nova_age"),
        u_snT=Track(lambda t: float(6000.0 + 11000.0 * np.exp(-max(t - T.nova, 0.0) / 2.5)), label="voyage.nova_T"),
        opacity=fade(T.start, dur=1.2, lead=0, out=T.black, out_dur=1.1),
        end=T.black,
        fx=[Bloom(C.bloom, threshold=0.9), Tonemap(), ZoomBlur(amount=0.22 * plunge),
            Lens(ca=0.5 * plunge, vignette=0.35 * plunge)]))

    # ── estimated light-years to the hole, in the top corner, for the length of the flight ──
    hud = s.manim(z=20)
    h = hud.redraw(clock, during=(T.start, T.black))
    hud.remove(h, at=T.black)

    # ── the far side: a slice of a 7-dimensional lattice opens out of the black and folds behind the quote ──
    out = T.card + 5.6                                       # then black again, for the cut into video 004
    lin = lambda c, k=1.0: tuple(k * x for x in hex_to_linear(c))                       # noqa: E731
    s.shader("hyperspace.frag", z=-5, start=T.card, u_colA=lin(C.horizon), u_colB=lin(C.ring), u_colC=lin(C.light),
             u_open=ramp(T.card, T.card + 3.2, 0.0, 1.0, ease="out_cubic"),
             u_amt=fade(T.card, dur=1.6, lead=0, out=out + 0.4, out_dur=1.2))

    # ── the quote, written, beside the man who said it ──
    side, centre = 3.5, np.array([-3.9, 0.15, 0.0])
    s.image("assets/images/einstein_card.png", height=side, pos=tuple(centre[:2]), z=5,
            opacity=fade(T.card + 1.2, dur=1.6, out=out, out_dur=1.0))
    m = s.manim(z=10)
    frame = Square(side + 0.22, color=C.light, stroke_width=C.thin).move_to(centre)
    m.play(Create(frame), at=T.card + 1.4, dur=1.6, ease="easy_ease")
    lines = VGroup(*[Tex(r"\textit{" + x + "}", font_size=54, color=C.text) for x in (
        r"``Look deep into nature,", r"and then you will understand", r"everything better.''")])
    lines.arrange(DOWN, buff=0.34, aligned_edge=LEFT).move_to([2.6, 0.55, 0])
    rule = Line(ORIGIN, 0.9 * RIGHT, color=C.light, stroke_width=C.thin)
    who = Tex(r"\textsc{Albert Einstein}", font_size=34, color=C.text)
    sig = VGroup(rule, who).arrange(RIGHT, buff=0.25).next_to(lines, DOWN, buff=0.6, aligned_edge=LEFT)
    for i, ln in enumerate(lines):
        m.play(FadeIn(ln, shift=0.18 * UP), at=T.card + 0.9 + 0.75 * i, dur=1.0, ease="out_cubic")
    m.play(Create(rule), FadeIn(who, shift=0.15 * RIGHT), at=T.card + 3.4, dur=0.9)
    m.play(FadeOut(lines), FadeOut(sig), FadeOut(frame), at=out, dur=1.0)
