"""s26's pieces: a proof as a chain of steps down to Lean's three axioms, and Mathlib's RiemannHypothesis, verbatim
(research.md A10), split into the parts that map to the maths. end_frame() gives s26's last frame for s27."""
from types import SimpleNamespace

from aion import *

from look import lab, mono, tex
from status import buzzard_card

LEVELS = [                                   # (y, [(x, label)])
    (-2.9, [(-4.9, "propext"), (-2.75, "Classical.choice"), (-0.6, "Quot.sound")]),
    (-1.6, [(-5.0, "def"), (-2.9, "lemma"), (-0.8, "lemma")]),
    (-0.3, [(-4.0, "lemma"), (-1.8, "lemma")]),
    (1.0, [(-2.9, "theorem")]),
]
EDGES = [((1, 0), (0, 0)), ((1, 0), (0, 1)), ((1, 1), (0, 1)), ((1, 2), (0, 2)), ((1, 2), (0, 1)),
         ((2, 0), (1, 0)), ((2, 0), (1, 1)), ((2, 1), (1, 1)), ((2, 1), (1, 2)), ((3, 0), (2, 0)), ((3, 0), (2, 1))]
ORDER = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (3, 0)]     # the kernel's walk, bottom-up


def chain():
    """Boxes (dict (level, i) -> VGroup) and the dependency arrows."""
    boxes = {}
    for lv, (y, items) in enumerate(LEVELS):
        for i, (x, name) in enumerate(items):
            t = mono(name.replace("_", r"\_"), 22, C.lean if lv == 0 else C.text)
            b = RoundedRectangle(width=t.width + 0.4, height=0.5, corner_radius=0.08,
                                 stroke_color=C.lean if lv == 0 else C.muted, stroke_width=1.6).move_to([x, y, 0])
            t.move_to(b)
            boxes[(lv, i)] = VGroup(b, t)
    arrows = VGroup(*[Arrow(boxes[a][0].get_bottom(), boxes[b][0].get_top(), buff=0.05, stroke_width=1.8,
                            color=C.faint, max_tip_length_to_length_ratio=0.12, tip_length=0.14) for a, b in EDGES])
    return boxes, arrows


def code():
    """Mathlib's definition, four lines of CM typewriter. Parts .lines .zeta .trivial .pole .re"""
    tt = lambda s: r"\texttt{" + s + "}"                          # noqa: E731
    l1 = Tex(tt("def RiemannHypothesis : Prop :="), font_size=28)
    l2 = Tex(tt(r"\ \ ") + r"$\forall$" + tt(" (s : ") + r"$\mathbb{C}$" + tt(") "), tt(r"(\_ : riemannZeta s = 0)"),
             font_size=28)
    l3 = Tex(tt(r"\ \ (\_ : "), r"$\neg\exists$" + tt(" n : ") + r"$\mathbb{N}$" + tt(", s = -2 * (n + 1))"),
             font_size=28)
    l4 = Tex(tt(r"(\_ : "), tt("s ") + r"$\neq$" + tt(" 1"), tt("),"), font_size=28)
    l5 = Tex(tt("s.re = 1 / 2"), font_size=28)
    lines = VGroup(l1, l2, l3, l4, l5).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    for l in lines[1:]:
        l.shift(0.45 * RIGHT)
    lines.move_to([-6.3 + lines.width / 2, 0.85, 0])
    for l in lines:
        l.set_color(C.text)
    g = SimpleNamespace(lines=lines, zeta=l2[1], trivial=l3[1], pole=l4[1], re=l5[0], ends=[l2, l3, l4, l5])
    return g


def maths(c):
    """The maths each part says, in its role color, in a column on the right, with its mapping line."""
    items = [(c.zeta, tex(r"\zeta(s)=0", size=34, color=C.zeta)),
             (c.trivial, VGroup(lab("not a trivial zero", 24, C.trivial), tex(r"s\ne-2,-4,\ldots", size=30,
                                                                              color=C.trivial)).arrange(RIGHT, buff=0.2)),
             (c.pole, VGroup(lab("not the pole", 24, C.muted), tex(r"s\ne1", size=30, color=C.muted)).arrange(
                 RIGHT, buff=0.2)),
             (c.re, tex(r"\mathrm{Re}(s)=\tfrac12", size=34, color=C.crit))]
    out = []
    for (part, m), end in zip(items, c.ends):
        m.move_to([2.6 + m.width / 2, part.get_y(), 0])
        col = m.get_color() if isinstance(m, MathTex) else m[0].get_color()
        ln = Line([end.get_right()[0] + 0.1, part.get_y(), 0], m.get_left() + [-0.12, 0, 0], color=col, stroke_width=1.4,
                  stroke_opacity=0.8)
        part_col = col
        out.append((part, part_col, ln, m))
    return out


def mathlib_box(c):
    b = VGroup(lab("defined in Mathlib", 24, C.lean), lab("a shared library of Lean mathematics", 20, C.muted))
    b.arrange(DOWN, buff=0.1)
    box = RoundedRectangle(width=b.width + 0.4, height=b.height + 0.3, corner_radius=0.1, stroke_color=C.lean,
                           stroke_width=1.6).move_to(b)
    g = VGroup(box, b)
    zx = c.zeta.get_right()[0] - 0.45
    g.move_to([zx, 3.15, 0])
    if g.get_right()[0] > 0.7:
        g.shift((0.7 - g.get_right()[0]) * RIGHT)
    arr = Arrow([zx, c.zeta.get_top()[1] + 0.02, 0], [zx, g.get_bottom()[1] - 0.02, 0], buff=0.0, color=C.lean,
                stroke_width=2, tip_length=0.16)
    return g, arr


def four_chip():
    from status import chip
    return chip("+ 4 theorems: Dirichlet L-functions", C.lean).move_to([-3.25, -1.75, 0])


def end_frame():
    """s26's last frame minus what fades: only the Buzzard card stays (drawn by s27 itself)."""
    return buzzard_card()
