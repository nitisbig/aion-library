"""s01 news (P01-P04): the hook, stated exactly. A November 2026 calendar lights the 20th and docks in the corner.
L. Alpoge (photo, Anthropic wordmark) posts a four-page note: its pages fan out as unreadable thumbnails, the claim
sentence highlighted; the claim sits in an amber outline, never filled; the Claude symbol sits on the path from him
to the note. Instead of a paper: Lean files. The card dissolves into one teal tile and the camera pulls back
to the wall of all 175,187 (419 to a row); a row of check rings, some still open. 1859; $1,000,000. Then the wall
collapses into one gold dot that drops onto the number line: s02's first frame. (The line of zeros waits for s02's first wave.)"""
from aion import *

from beats import T
from look import EASE, X, caps, lab, live, number_line, pin, tex
from media_assets import alpoge, note_page, paper_1859, riemann, svg_logo
from status import GAP, N_FILES, PER_ROW, TILE, chip, ring, wall_rgba, wall_tile_xy

WH = 5.4                                    # the wall's height once pulled back
P1 = np.array([-1.7, 0.25])                 # its centre
K = 209 * PER_ROW + 209                     # the tile the card becomes (the middle of the wall)
Q = np.array([-3.3, -0.35])                 # where that tile first appears
TW = WH * TILE / ((-(-N_FILES // PER_ROW)) * (TILE + GAP) + GAP)     # one tile's side once pulled back
SC0 = 0.55 / TW                             # the tile starts 0.55 units wide


@scene(T.start, T.cut_staircase)
def s01_news(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    w = s.manim(z=2)                        # the line of zeros, the number line, the gold dot (s02's layer)
    h = s.manim(z=6, parallax=0.0)
    tiles = s.manim(z=4, parallax=0.0)

    # ── 20 Nov 2026: a calendar, one day lit ──
    CELL, GAPC = 0.34, 0.12
    cells = VGroup()
    for d in range(1, 31):                                  # 1 Nov 2026 is a Sunday: column 0, Sunday first
        r_, c_ = divmod(d - 1, 7)
        sq = RoundedRectangle(width=CELL, height=CELL, corner_radius=0.05, stroke_color=C.muted, stroke_width=1.2,
                              stroke_opacity=0.7, fill_opacity=0.0)
        cells.add(sq.move_to([c_ * (CELL + GAPC), -r_ * (CELL + GAPC), 0]))
    month = caps(r"November 2026", 30, C.ink).next_to(cells, UP, buff=0.3)
    cal = VGroup(month, cells).move_to([0, 0.2, 0])
    day = cells[19]
    h.play(FadeIn(month, shift=0.06 * UP), at=T.nw_nov, dur=0.6)
    h.play(LaggedStart(*[FadeIn(c_, scale=0.6) for c_ in cells], lag_ratio=0.04), at=T.nw_nov + 0.1, dur=1.0)
    lit = RoundedRectangle(width=CELL, height=CELL, corner_radius=0.05, stroke_width=0, fill_color=C.claimed,
                           fill_opacity=1.0).move_to(day)
    num20 = tex(r"20", size=20, color=C.bg).move_to(day)
    h.play(FadeIn(lit, scale=1.8), at=T.nw_nov + 0.75, dur=0.5, ease="out_back")
    h.play(FadeIn(num20), at=T.nw_nov + 1.1, dur=0.4, lead=0)
    cal.add(lit, num20)
    h.play(cal.animate.scale(0.5).move_to([-5.45, 3.0, 0]), at=T.nw_alpoge - 0.15, dur=0.8, ease=EASE)

    # ── L. Alpoge, a mathematician at Anthropic ──
    PH = 3.0
    pxy = (-4.3, 0.45)
    out = (T.nw_instead + 0.2, T.nw_instead + 0.8)
    show = lambda a, b=out: keys((a - 0.1, 0.0), (a + 0.5, 1.0), (b[0], 1.0), (b[1], 0.0), lead=0)   # noqa: E731
    s.add(ArrayLayer(alpoge(), height=PH, pos=pxy, z=5, parallax=0.0, opacity=show(T.nw_alpoge + 0.3)))
    who = caps(r"L. Alp\"oge", 30, C.ink).move_to([pxy[0], pxy[1] - PH / 2 - 0.32, 0])
    h.play(FadeIn(who, shift=0.05 * UP), at=T.nw_alpoge + 0.4, dur=0.6)
    mark = svg_logo("anthropic_logo.svg", 0.17, C.ink).next_to(who, DOWN, buff=0.22)
    h.play(FadeIn(mark, shift=0.05 * UP), at=T.nw_anthropic, dur=0.6)

    # ── posted a four-page note: the pages fan out; the claim sentence is highlighted ──
    arrow = Arrow([pxy[0] + 1.3, pxy[1], 0], [0.35, pxy[1], 0], buff=0, stroke_width=2.5, color=C.muted,
                  max_tip_length_to_length_ratio=0.06)
    h.play(GrowArrow(arrow), at=T.nw_posted - 0.1, dur=0.6)
    NH = 2.8
    centre = np.array([3.45, 0.55])
    spread = [(-1.35, 0.06, 6.0), (-0.45, 0.0, 2.0), (0.45, 0.0, -2.0), (1.35, 0.06, -6.0)]   # dx, dy, degrees
    fan = keys((T.nw_posted + 0.2, 0.0), (T.nw_posted + 1.2, 1.0, EASE), lead=0)
    lift = keys((T.nw_believes - 0.2, 0.0), (T.nw_believes + 0.5, 1.0, EASE), (T.nw_claude - 0.6, 1.0),
                (T.nw_claude + 0.1, 0.0, EASE), lead=0)
    hl = tuple(float(v) for v in ManimColor(C.claimed).to_rgb())
    for i, (dx, dy, ang) in reversed(list(enumerate(spread))):          # page 1 on top
        rgba, k = note_page(i + 1, ang)
        def p_pos(t, dx=dx, dy=dy, i=i):
            f = float(fan(t))
            p = centre + f * np.array([dx, dy])
            if i == 0:
                p = p + float(lift(t)) * np.array([0.55, 0.05])
            return tuple(p)
        sc_ = (lambda t: 1.0 + 0.3 * float(lift(t))) if i == 0 else 1.0
        start = T.nw_posted + 0.05 * i
        s.add(ArrayLayer(rgba, height=NH * k, pos=p_pos, scale=sc_, z=5.4 - 0.1 * i, parallax=0.0,
                         opacity=show(start)))
        if i == 0:                                                       # the same page, highlighted, cross-fades in
            rgbh, _ = note_page(1, ang, hl)
            hop = keys((T.nw_believes + 0.1, 0.0), (T.nw_believes + 0.6, 1.0), (out[0], 1.0), (out[1], 0.0), lead=0)
            s.add(ArrayLayer(rgbh, height=NH * k, pos=p_pos, scale=sc_, z=5.45, parallax=0.0, opacity=hop))

    # ── the claim, in an amber outline that is never filled ──
    cl = VGroup(lab("claimed:", 28, C.claimed), lab("a proof of the Riemann hypothesis", 30, C.text))
    cl.arrange(RIGHT, buff=0.22)
    cbox = RoundedRectangle(width=cl.width + 0.5, height=cl.height + 0.45, corner_radius=0.1, stroke_color=C.claimed,
                            stroke_width=2.4).move_to(cl)
    claim = VGroup(cbox, cl).move_to([centre[0] - 0.05, -2.45, 0])
    h.play(FadeIn(cl), at=T.nw_proof, dur=0.6)
    h.play(Create(cbox), at=T.nw_proof + 0.3, dur=0.8)

    # ── working with Claude: the symbol sits on the path from him to the note ──
    mid = np.array([(pxy[0] + 1.3 + 0.35) / 2, pxy[1], 0])
    hole = Circle(radius=0.42, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to(mid)
    sym = svg_logo("claude_symbol.svg", 0.62, C.ai).move_to(mid)
    ctag = caps(r"Claude", 24, C.ai).next_to(hole, DOWN, buff=0.08)
    h.play(FadeIn(hole), at=T.nw_claude, dur=0.3)
    h.play(FadeIn(sym, scale=0.6), at=T.nw_claude + 0.05, dur=0.5)
    # (no spin: keeps the mark as drawn)
    h.play(FadeIn(ctag, shift=0.05 * UP), at=T.nw_claude + 0.3, dur=0.5)

    # ── instead of a paper: Lean files. The card becomes one tile; pull back to all 175,187 ──
    melt = (T.nw_instead + 0.2, T.nw_instead + 1.0)
    first = Square(side_length=0.55, stroke_width=0, fill_color=C.lean, fill_opacity=1.0).move_to([*Q, 0])
    h.play(FadeOut(VGroup(cal, who, mark, arrow, hole, sym, ctag)), at=melt[0], dur=0.6, lead=0)
    h.play(ReplacementTransform(claim, first), at=melt[0] + 0.2, dur=0.6, lead=0)
    pull = (melt[1] + 0.3, melt[1] + 4.3)
    pu = keys((pull[0], 0.0), (pull[1], 1.0, EASE), lead=0)
    off = wall_tile_xy(K, WH)
    collapse = (T.nw_starts - 0.6, T.nw_starts + 0.6)
    cu = keys((collapse[0], 0.0), (collapse[1], 1.0, "in_cubic"), lead=0)

    def sc(t):
        if t < collapse[0]:
            return float(np.exp(np.log(SC0) * (1.0 - float(pu(t)))))
        return max(1e-3, 1.0 - 0.995 * float(cu(t)))

    def pos(t):
        if t < collapse[0]:
            a = float(pu(t))
            tp = (1 - a) * Q + a * (P1 + off)
            return tuple(tp - sc(t) * off)
        return tuple(P1)

    def band(t, hi, lo):
        v = sc(t)
        return float(np.clip((hi - v) / (hi - lo), 0.0, 1.0))

    dim_k = keys((T.nw_open - 0.3, 1.0), (T.nw_open + 0.5, 0.2), (collapse[0] - 0.9, 0.2), (collapse[0] - 0.2, 1.0),
                 lead=0)
    full_op0 = lambda t: band(t, 12.0, 9.0) * (1.0 - band(t, 4.5, 3.0)) if pull[0] <= t < collapse[0] else 0.0   # noqa: E731
    soft_op0 = lambda t: (band(t, 4.5, 3.0) if t < collapse[0] else 1.0 - float(cu(t)) ** 0.5) if t >= pull[0] else 0.0  # noqa: E731
    full_op = lambda t: full_op0(t) * float(dim_k(t))      # noqa: E731
    soft_op = lambda t: soft_op0(t) * float(dim_k(t))      # noqa: E731
    s.add(ArrayLayer(wall_rgba(), height=WH, pos=pos, scale=sc, z=3, parallax=0.0, opacity=full_op))
    s.add(ArrayLayer(wall_rgba(px=1200), height=WH, pos=pos, scale=sc, z=3, parallax=0.0, opacity=soft_op))

    def near(t):
        """Every tile on screen, drawn sharp (one VMobject of square subpaths) while the tiles are big."""
        v, p = sc(t), np.asarray(pos(t))
        a = 1.0 - band(t, 12.0, 9.0)
        if a <= 0:
            return VGroup()
        r0, c0 = divmod(K, PER_ROW)
        pitch = v * TW * (TILE + GAP) / TILE
        nr, nc = int(4.8 / pitch) + 2, int(11.0 / pitch) + 2         # the first tile sits left of centre
        rr, cc_ = np.meshgrid(np.arange(-nr, nr + 1), np.arange(-nc, nc + 1), indexing="ij")
        rr, cc_ = (rr + r0).ravel(), (cc_ + c0).ravel()
        k = rr * PER_ROW + cc_
        ok = (rr >= 0) & (cc_ >= 0) & (cc_ < PER_ROW) & (k < N_FILES)
        cen = p + v * np.array([wall_tile_xy(int(j), WH) for j in k[ok]])
        hs = v * TW / 2
        corners = np.array([[-hs, -hs], [hs, -hs], [hs, hs], [-hs, hs], [-hs, -hs]])
        pts = []
        for c in cen:
            q = c + corners
            for i in range(4):
                A, B = q[i], q[i + 1]
                pts += [A, A + (B - A) / 3, A + 2 * (B - A) / 3, B]
        pts = np.column_stack([np.array(pts), np.zeros(len(pts))])
        m = VMobject(stroke_width=0, fill_color=C.lean, fill_opacity=a)
        m.set_points(pts)
        return m

    tiles.remove(first, at=pull[0])
    h.remove(first, at=pull[0])
    live(tiles, near, (pull[0], pull[1]))

    # ── 175,187 files; a computer checks every step; checks still under way ──
    rx = 3.3
    num = VGroup(tex(r"175{,}187", size=48, color=C.lean), lab("Lean files", 30, C.lean)).arrange(DOWN, buff=0.12)
    num.move_to([rx, 2.4, 0])
    h.play(FadeIn(num, shift=0.06 * UP), at=pull[1] - 0.6, dur=0.6, lead=0)
    every = lab("a computer checks every step", 24, C.muted).move_to([rx, 1.35, 0])
    h.play(FadeIn(every), at=T.nw_checks, dur=0.5)
    rings = VGroup(*[ring(i not in (3, 8, 11), r=0.1) for i in range(14)]).arrange(RIGHT, buff=0.18)
    rings.move_to([P1[0], P1[1] - WH / 2 - 0.38, 0])
    rl = lab("checks: still under way", 24, C.muted).move_to([rx, 0.55, 0])
    h.play(LaggedStart(*[FadeIn(r_, scale=0.6) for r_ in rings], lag_ratio=0.08), at=T.nw_record, dur=1.0)
    h.play(FadeIn(rl), at=T.nw_underway - 0.2, dur=0.5)

    # ── open since 1859: Riemann's paper and portrait. A million-dollar prize: the Clay Institute ──
    h.play(FadeOut(VGroup(num, every, rl, rings)), at=T.nw_open - 0.4, dur=0.5, lead=0)
    show = lambda a, b: keys((a, 0.0), (a + 0.6, 1.0), (b - 0.5, 1.0), (b, 0.0), lead=0)   # noqa: E731
    end_ = collapse[0] - 0.1
    pg = paper_1859(1)
    PGH = 4.3
    pgxy = (2.75, 0.45)
    s.add(ArrayLayer(pg, height=PGH, pos=pgxy, z=5, parallax=0.0, opacity=show(T.nw_open - 0.1, end_)))
    rp = riemann()
    RH_ = 2.0
    rxy = (5.35, 1.75)
    s.add(ArrayLayer(rp, height=RH_, pos=rxy, z=5, parallax=0.0, opacity=show(T.nw_open + 0.4, end_)))
    rcap = caps(r"B. Riemann $\cdot$ 1859", 26, C.ink).move_to([rxy[0], rxy[1] - RH_ / 2 - 0.25, 0])
    h.play(FadeIn(rcap, shift=0.04 * UP), at=T.nw_open + 0.6, dur=0.5)
    c59 = chip("open since 1859", C.ink, size=24)
    c59.move_to([pgxy[0], pgxy[1] - PGH / 2 - 0.35, 0])
    h.play(FadeIn(c59, shift=0.06 * UP), at=T.nw_open + 0.3, dur=0.5)
    clay = svg_logo("clay_logo.svg", 0.6, C.ink).move_to([rxy[0], -0.4, 0])
    h.play(FadeIn(clay, shift=0.06 * UP), at=T.nw_prize - 0.2, dur=0.6)
    cmil = chip(r"\$1,000,000", C.ink, size=26).move_to([rxy[0], -1.3, 0])
    h.play(FadeIn(cmil, shift=0.06 * UP), at=T.nw_prize, dur=0.5)
    cl2 = chip("claimed", C.claimed, size=26).move_to([rxy[0], -2.15, 0])
    h.play(FadeIn(cl2), at=T.nw_judge, dur=0.5)

    # ── that starts with the primes: the wall collapses into one gold dot on the number line ──
    h.play(FadeOut(VGroup(rcap, c59, clay, cmil, cl2)), at=collapse[0] - 0.5, dur=0.5, lead=0)
    nl = number_line(0.0)
    w.play(Create(nl), at=T.nw_starts, dur=1.0, lead=0)
    seed0 = Dot([*P1, 0], radius=0.07, color=C.prime)
    seed = Dot([float(X(2)), 0.0, 0], radius=0.07, color=C.prime)
    w.play(FadeIn(seed0, scale=0.2), at=collapse[1] - 0.3, dur=0.3, lead=0)
    w.play(ReplacementTransform(seed0, seed), at=collapse[1], dur=0.7, ease=EASE, lead=0)
