# Neural network: 30 s hobby scene (exploration), v2: handwritten-digit countdown

A real handwritten-digit recognizer assembles itself out of the dark, then counts down 9 → 0.
Each handwritten digit is written onto the input grid as glowing ink, the signal races through the network,
and the matching output neuron flares and releases the clean digit. Black background, look C
(ice-blue hologram), small glowing neurons. No text other than the recognised digits.

**Everything is real.** The network is an MNIST classifier trained in numpy (96.8 % test accuracy); the
digits are real MNIST *test* images; every glow is a real activation or a real w·a contribution; the
digit that appears at the output is the network's actual answer.

| On screen | Comes from |
|---|---|
| Input neuron glow | pixel value of the 14×14 (pooled) handwritten digit |
| Ink particles | sampled from the original 28×28 image intensity |
| Edge brightness / thickness | \|w\| (98th-percentile normalised per layer) |
| Edge hue | sign of w: bright ice = positive, deep blue = negative |
| Pulse along an edge | \|w·a\| flowing through it during the forward pass |
| Hidden neuron flare | ReLU activation |
| Output flare + glyph | softmax p and argmax |

Network: **196 → 32 → 28 → 24 → 16 → 10** (4 hidden layers). The input fan is display-pruned to each
hidden-1 neuron's 28 strongest weights.

---

## 1. Engine choice

| Need | Tool | Why |
|---|---|---|
| MNIST training, forward passes, digit selection | **numpy** | Exact, deterministic, about 70 s to train on 2 cores |
| Neurons, 3008 curved edges, 24k signal particles, ink particles, glyphs, rings | **moderngl** (Radeon R4) | Additive HDR glow and many instanced sprites per frame |
| Glyph atlas | **Pillow** + Inter Light | Crisp mask plus a gaussian glow channel, sampled on GPU billboards |
| Bloom, tonemap, scanlines, 2× SSAA | **moderngl** post passes | Reused from the black-hole lab |
| Encode | **ffmpeg** + **tqdm** ETA bar | Resumable segments |

---

## 2. Storyboard (30.0 s @ 60 fps)

| # | Time | What the viewer sees | Camera |
|---|---|---|---|
| 1 | 0.0–2.0 | Black. A seed of light ignites and ripples outward into the 14×14 input grid | Frontal, close |
| 2 | 2.0–5.8 | Filaments grow layer by layer; each hidden disc of neurons forms as its filaments land. The output column of 10 forms last | Pull back and orbit to reveal depth |
| 3 | 5.1–8.6 | **9** is written onto the grid as ink, top to bottom. The signal fires through the layers and the top output flares; rings expand and a clean "9" emerges | Hero shot on the input, then follow the signal to the output |
| 4 | 8.4–20.5 | **8 → 1**, accelerating. Digits are in flight in different layers at once. Each answer rolls in like an odometer, moving down the output column | Wide orbits: side, low angle, high angle |
| 5 | 21.1–24.4 | **0** is written, seen close; the slower final pass whips along the network; the bottom output flares with big rings and a large "0" | Close on the input, whip along, push in on the output |
| 6 | 24.4–30.0 | The "0" holds; the network breathes, then a wide pull-back and fade to black | Wide dolly back |

## 3. Files
`network.py` (MNIST + training) · `layout.py` (3D layout) · `timeline.py` (all per-frame state) ·
`render.py` (moderngl pipeline, CLI) · `shaders/` · `NOTES.md`
