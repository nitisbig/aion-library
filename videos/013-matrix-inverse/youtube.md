# YouTube package: What Matrix Inverses Actually Mean

Final file: `videos/013-matrix-inverse/out/final_4k30.mp4` (3840×2160, 30 fps, 10:07).

---

## Title

**Recommended:** `What Matrix Inverses Actually Mean`

It matches the series pattern (009 What Matrices Are, 011 What the Matrix Exponential Actually Is) and says plainly what the video is.

Alternatives, if you want more search pull or more curiosity:

| Style | Title |
|---|---|
| Search-first | The Inverse Matrix, Visually Explained |
| Search-first | How to Undo Any Linear Transformation |
| Curiosity | Why Some Matrices Can't Be Undone (and How a CT Scanner Cheats) |
| Curiosity | 16 Different Keys Cast the Same Shadow. Here's Why. |
| Question | Can You Put the Plane Back? The Inverse Matrix |

Thumbnail idea: the brass key on the left, its flat streak shadow on the right, with a bold `A⁻¹ ?` between them. Black background, no glow, to match the video.

---

## Description (paste this)

```
What Matrix Inverses Actually Mean

One matrix can be undone. Its near-twin can't. Why? Start with a brass key on a grid, bend the whole plane, and watch the inverse bring every point home. Then crush the plane into a shadow, find that sixteen different keys cast the same one, and see exactly what "no inverse" means. The same idea decides how a game camera draws its world, how a drone reads a map, how an equation gets solved, why deblurring a photo can fail, and how a CT scanner rebuilds an object from its shadows.

Chapters
0:00 A key, a grid, and a way back
0:29 The matrix that can't be undone
0:59 Why it matters, and the promise
1:20 Easy ways back
1:42 Why "flip every number" is wrong
2:08 Threads: every move, reversed
2:26 The identity, and both orders
2:59 Rewind: undoing a chain of moves
3:32 Finding the inverse: rewind and record
5:08 The determinant, and what can't come back
6:31 Solving equations: Ax = b
7:41 A drone, a game camera, a blurred photo
8:57 Rebuilding the key from its shadows
9:43 What the move forgot

An inverse is every thread of a move, walked backward. A way back exists exactly when the move forgot nothing.

Made with Manim, GPU shaders and Skia. Narration by ElevenLabs.

#inversematrix #linearalgebra #math
```

Notes:
- Chapter starts are the real scene cuts from `beats.py`. Each chapter is over 10 s, so YouTube will accept them.
- If you do not want the credit line, delete the "Made with…" line.
- Add a pinned comment with the series links (009 What Matrices Are, 006 determinant).

### Tags

inverse matrix, matrix inverse, inverse of a matrix, linear algebra, linear transformation, determinant, singular matrix, why matrices have no inverse, solving linear equations, Ax=b, row reduction, Gauss-Jordan, deblurring, CT scan reconstruction, tomography, math visualization, math animation, Manim, 3Blue1Brown style

---

## Shorts

YouTube Shorts are vertical (1080×1920), at most 60 s, and must hook inside the first 2 seconds. The video is landscape, so each short needs a vertical re-frame: crop to the 3D stage, or re-run the scene with a portrait camera as the lab's portrait `det-zero short` did. Write narration fresh for each short; do not cut mid-sentence from the long video.

Every short ends with a pointer to the full video, and the last line loops into the first so it replays cleanly.

### Short 1: Sixteen keys, one shadow (≈ 40 s)

Source: 0:29–0:59, `s02_the_crush`. Strongest hook, and it is the video's open loop.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | Key on grid, then the plane falls flat to a streak | "Here's a key. Watch what one matrix does to it." |
| 0:05 | Key collapses to a line. Text: `PUT IT BACK` | "It's a flat streak now. Put it back." |
| 0:11 | Sixteen keys, each with a different tooth pattern, all above the same streak | "You can't. This streak came from this key. Or this one, with a tooth flipped. Four teeth, up or down: sixteen keys." |
| 0:24 | Streak glows once; counter `16 keys → 1 shadow` | "All sixteen leave exactly the same shadow." |
| 0:31 | Text: `One shadow can't tell you which key cast it.` | "One shadow can't tell you which key cast it." |
| 0:36 | Cut back to the intact key | "So how does a CT scanner do it? Full video on the channel." |

On-screen caption: **Why some matrices can't be undone**

### Short 2: Don't flip the numbers (≈ 35 s)

Source: 1:42–2:08, `s05_wrong_rule`.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | `[[2,0],[0,3]]` becomes `[[½,0],[0,⅓]]` | "To undo a stretch, flip the numbers. Two becomes a half. Three becomes a third." |
| 0:08 | Text: `So the inverse is every entry flipped?` | "So the inverse is just every number flipped. Right?" |
| 0:12 | Slide matrix `[[1,1],[0,1]]` with the zero circled in red | "Try it on this one. There's a zero. You can't flip zero." |
| 0:19 | The same matrix with one sign changed, grid returns home | "Yet we undid this move by changing one sign." |
| 0:26 | A near-flat matrix with no zeros, key crushed | "And this one has no zeros at all, and it can't be undone." |
| 0:31 | Text: `Watch what it does to space.` | "The numbers won't tell you. Watch what the whole matrix does to space." |

On-screen caption: **The "flip every number" rule is wrong**

### Short 3: An inverse is a thread, walked backward (≈ 40 s)

Source: 2:08–2:26, `s06_threads`, and the first sentence of `s07_identity`.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | One point and a thread from start to landing | "Take one point. Draw a thread from where it started to where it landed." |
| 0:07 | Threads for every point appear, forming a web | "Now do it for every point." |
| 0:13 | The web glows; text `This is the matrix` | "That whole web of threads is the move." |
| 0:19 | Arrows reverse on every thread | "The way back is the same web, walked the other way." |
| 0:26 | Text: `Inverse = every thread, reversed` | "That's all an inverse is. Every thread, reversed." |
| 0:32 | Out-and-back round trip, every point returns | "Go out and come back, and everything is where it began." |

On-screen caption: **What an inverse really is**

### Short 4: Your game never moves the camera (≈ 35 s)

Source: 8:00–8:17, `s21_camera`. Surprising fact, short, visual.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | Camera walking up a street of blocks (outside view) | "In a video game, you never walk forward." |
| 0:05 | Split: outside view left, what the camera sees right | "The camera sits in the world, placed by a matrix." |
| 0:12 | Text `C` on the camera, `C⁻¹` on the right view | "To draw what it sees, the game applies the inverse of that matrix to everything else." |
| 0:20 | Camera locks; the town slides backward past it | "So the world gets carried backward, past you." |
| 0:28 | Text: `Every frame. Every game.` | "Every frame, every game: one inverse matrix." |

On-screen caption: **How a game camera really works**

### Short 5: Why unblurring a photo explodes (≈ 45 s)

Source: 8:17–8:57, `s22_blur` and `s23_noise`. The ×2360 number is computed in the video from the actual blur.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | Blurred die | "This blur has an inverse. Apply it, and every edge comes back." |
| 0:08 | Bar chart: tall orange bars shrinking to near zero | "But blur squeezes the finest detail almost to nothing." |
| 0:15 | Teal bars stretching up, counter `×2360` | "So the inverse has to stretch that detail by two thousand times." |
| 0:23 | Faint noise added, picture turns to pink static | "Add noise too faint to see, and it gets stretched too." |
| 0:30 | Picture is buried; text `useless` | "The picture is buried." |
| 0:34 | A cutoff plane sweeps up; die returns sharp | "Real deblurring stops short, and only undoes the directions that survived." |
| 0:41 | Text: `An inverse can exist and still be useless.` | "An inverse can exist, and still be useless." |

On-screen caption: **Why deblurring blows up**

### Short 6: Rebuilding the key from its shadows (≈ 45 s)

Source: 8:57–9:43, `s24_second_shadow` and `s25_ct_reconstruct`. The payoff; best as the final short or the one that points straight to the long video.

| Time | On screen | Narration |
|---|---|---|
| 0:00 | The crushed streak and sixteen keys | "One shadow can't tell sixteen keys apart." |
| 0:06 | Light turns 40°, a second shadow appears, pink cells mark where flipped keys differ | "So turn the light. A tooth that could point either way now falls somewhere new." |
| 0:15 | Counter `16 keys fit → 1 key fits` | "Two shadows, and only one key fits both." |
| 0:21 | Ring of shadows; counter 4, 16, 32, 64, 128; reconstruction sharpens from blur to outline to key | "Four shadows. Sixteen. A blur at first, then an outline." |
| 0:33 | The finished key, teeth and all | "With enough angles, nothing is forgotten, and here's the key, rebuilt from shadows alone." |
| 0:39 | CT scanner ring around the key | "This is how a CT scanner sees inside you." |

On-screen caption: **Rebuilding an object from its shadows**

### Posting order and notes

1. Post Short 1 first (it opens the loop), then Short 6 two or three days later (it closes it).
2. Posting Shorts 2 to 5 between them keeps the channel active and each one links to the full video.
3. Put the full-video link in each short's description and pin a comment with it.
4. Shorts title pattern: question or surprising claim, under 60 characters, plus `#shorts`. Example: `16 keys, 1 shadow #shorts #math`.
5. Every short quotes narration that I wrote for this file, not the video's audio. Voice them with the same ElevenLabs voice, or record them separately. Generating new audio spends credits, so it needs your OK first.
