# Voyage to the black hole — supplementary cold open for video 004

Audio: `assets/audio.wav`, 21.4 s. One spoken line (9.0–13.7 s), silence around it for music.
One unbroken shot (0–14.6 s), then the quote card on black. `uv run aion sheet 005 s00` shows a frame per beat.

Everything in the flight is computed: the hole, its disk and every background object are drawn by aion's
Schwarzschild ray tracer (`BlackHoleLayer`, light paths from u'' + u = 3u²). The sky objects are looked up
along the *bent* ray, so the lensing is the real thing. The planet is close to the camera and uses straight rays.

## s00_voyage · 0 → 21.4 s

Narration: "Look deep into nature, and then you will understand everything better." (attributed to Albert Einstein, 1951)

| beat | s | what the viewer sees | why it is there |
|---|---|---|---|
| `remnant` | 0–2.5 | Fade up mid-flight: a ringed ice giant sweeps out of frame, an emission nebula and a supernova remnant behind it. | Scale and depth: the planet is a real position, so the camera's own motion moves it. |
| `pulsar` | 1.5–4 | A neutron star, lighthouse beams turning. The hole enters as a small warm speck at the right. | Other ways a star ends, before the one this video is about. |
| `centred` | 5.0 | The pan stops with the hole in the middle, stars round it pulled into arcs. | First clear sight of the subject. |
| `einstein` | 5.5–7.5 | A spiral galaxy slides behind the hole and is smeared into a ring. | Gravitational lensing on something with a recognisable shape. |
| `nova` | 7.5–10.5 | A star explodes beside the hole; its light splits in two, then wraps into an Einstein ring. | Lensing of a point source: one star seen twice. |
| `look` | 9.0 | "Look deep into nature…" The camera banks and dives; the far side of the disk rises over the shadow. | The line lands as the camera looks into the hole. |
| `skim` | 12.5 | 30 M from the centre, 2 M above the gas. Wide lens, slight buffeting. | The closest the viewer gets: the disk is a landscape. |
| `said` → `black` | 13.7–14.6 | "…everything better." A long-lens push into the shadow; the picture fades to black. | The black is the hole itself, and what the card sits on. |
| `card` | 14.9–20.5 | Out of the black, a slice of a 7-dimensional lattice opens from the centre: thin violet and cyan contour lines, zooming inward and folding. Einstein's 1921 portrait, square and framed, at the left; the quote line by line at the right, then his name. | The far side of the hole. The words are read after they are heard. |
| end | 20.5–21.4 | Card fades to black. | Video 004 opens by fading up from black: cut straight into it. |

`d ≈ … light-years` runs in the top-right corner for the length of the flight: the estimated distance still to go,
1,500 at the first frame, falling with the camera's real distance from the hole (story scale: the path itself is in M).

Camera (`flight.py`): distance 1500 → 21 M in log space (the tracer's tables stop at 20 M), a 150° orbit,
inclination 52° → 85° → 79°, an opening look-away that pans onto the hole, an 11° bank in the dive,
field of view 36° → 52° (dive) → 20° (plunge).

Portrait: Ferdinand Schmutzer, 1921, public domain (Wikimedia Commons). `make_portrait.py` builds the square crop.
