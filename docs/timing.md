# Timing: beats, tracks, lead

## The model
Every value on screen is a pure function of **absolute audio time `t`** (seconds from the start of
`audio.wav`). Scenes are windows `[start, end)` on that timeline. Nothing accumulates frame to frame, so
any frame can be rendered alone, in any order, by any worker. Holds cost nothing.

## Beats (`beats.py`)
```python
from aion import beats, cut, end, w
T = beats(
    intro="today we",               # str = start of the phrase
    grid=w("grid", offset=-0.2),    # w() = start, with options (offset, nth)
    done=end("for every vector"),   # end() = end of the phrase
    cut1=cut("every vector", "now consider"),   # boundary in the middle of the silence between
    lam="lambda",
)
```
- Specs resolve **in order**: each search begins after the previous beat. A repeated word just works:
  the second `"x"` finds the next occurrence. Use `nth=2` to skip matches.
- Unknown phrases fail with the closest matches (`KeyError: 'eigen vector' … did you mean 'eigenvector'`).
- `T.name` is a `Beat` (a float) with `.end` (end of the phrase) and `.text`. `T.start = 0`, `T.end` = audio
  length (decoded samples, exact). `T.cuts` lists the cut beats.
- `cut()` snaps to the frame grid at `fps` (60 by default). If no real silence is nearby it still works
  but is marked `.soft`, and `aion audit --timing` warns (audible jump at the cut).
- `aion beats <v>` prints the resolved table; `--md` prints markdown for the storyboard.

## Lead: `at=` lands on the beat
`m.play(anim, at=T.x)`, `key(T.x, a, b)`, `fade(T.x)` and camera moves all **end their ease-in on the
beat**: motion starts `lead` (theme `lead`, default 0.15 s) early, so the viewer sees it as the word is
heard. Pass `lead=0` to start exactly on the beat. `pulse(T.x)` peaks exactly on the beat. `m.add(at=)` is exact.

## Tracks
`Track` = a function of `t` that knows when it changes (so static frames are skipped).

| maker | meaning |
|---|---|
| `const(v)` / plain numbers | constant |
| `key(at, a, b, dur, ease)` | hold a → move → hold b |
| `keys((t, v[, ease]), …)` | multi-keyframe |
| `fade(at, to=1, out=None)` | opacity in (and out) |
| `pulse(at, amp, dur, base)` | bump that peaks on the beat |
| `ramp(t0, t1, a, b)` | linear segment |
| `wave(freq, amp, phase, base, during)` | oscillation |
| `Clock(rate, start)` | ∫ rate dt: slow-motion / speed ramps with continuous position |

Tracks compose with `+ - * /`, `.map(f)`, `.delay(s)`, `.clamp(lo, hi)`. Values may be numbers, tuples or
numpy arrays (matrices interpolate elementwise). Any layer parameter, effect parameter or `u_*` uniform accepts a Track.

## Easing
`ease=` accepts a name or a callable: `smooth` (default), `smoother`, `linear`, `in_cubic`, `out_cubic`,
`in_out_cubic`, `out_quint`, `out_expo`, `in_out_sine`, `out_back`, `out_elastic`, `there_and_back`,
`easy_ease` (After Effects' default), `easy_ease_in`, `easy_ease_out`, `snap`, `spring`, plus factories
`spring(k, damping)`, `steps(n)` and `cubic_bezier(x1, y1, x2, y2)`.
Guidance: `easy_ease` for camera, `smooth` for most motion, `out_back` for small pops, avoid `linear`
except for clocks and continuous rotation.

## Checks
- An event whose `at` lies outside its scene raises at build time (wrong beat).
- An animation that runs more than 0.5 s past its scene end raises (shorten `dur` or move the cut).
- `aion audit <v> --timing` covers contiguity, soft cuts and scenes under 2 s.
