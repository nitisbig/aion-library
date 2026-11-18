"""Sound design for 010: a calm, synthesized SFX bed mixed under the narration (aion has no audio-mix step).

Everything is generated here (seeded numpy/scipy, no downloaded samples), placed on named beats from beats.py, and
mixed into assets/audio.wav from the untouched narration master assets/audio.narration.wav. beats.py reads its timing
and silences from that narration file, so the SFX can never move a cut.

Palette (all quiet, ~15–25 dB under the voice; soft attacks, no clicks):
  whoosh  airy band-passed noise swell      chapter headers
  chime   two soft sine partials (a fifth)  the chapter badge lighting, and a few landings (claim, thesis)
  tick    short, high, round                reveals: answers, checks, key equations, badge arrivals
  thud    low, short                        strike-throughs and crosses (lim, ≈, det, D⁻¹, "by parts")
  swish   short noise sweep                 turns and slides (quarter turns, the eighth turn, the shift by h)
  pluck   the s13 string note (12 modes of the 200-point matrix, as in the picture)

Idempotent. Run from the repo root:  uv run python videos/010-calculus-is-linear-algebra/make_sfx.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import T  # noqa: E402

A = HERE / "assets"
NARR, MASTER = A / "audio.narration.wav", A / "audio.wav"
SR = 44100
RNG = np.random.default_rng(10)


def db(x):
    return 10 ** (x / 20)


def _t(d):
    return np.arange(int(d * SR)) / SR


def tick(f=1700.0, level=-27):
    t = _t(0.16)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.022) + 0.35 * np.sin(2 * np.pi * 2.01 * f * t) * np.exp(-t / 0.012)
    y *= np.minimum(t / 0.002, 1)
    return db(level) * y / np.abs(y).max()


def thud(level=-25):
    t = _t(0.4)
    y = np.sin(2 * np.pi * (95 - 30 * t) * t) * np.exp(-t / 0.09)
    n = sosfilt(butter(2, 900, "low", fs=SR, output="sos"), RNG.standard_normal(len(t))) * np.exp(-t / 0.03)
    y = y + 0.25 * n / np.abs(n).max()
    y *= np.minimum(t / 0.004, 1)
    return db(level) * y / np.abs(y).max()


def noise_sweep(d, f0, f1, level):
    """Band-passed noise whose band glides f0 → f1, under a smooth sin² envelope."""
    t = _t(d)
    n = RNG.standard_normal(len(t))
    out = np.zeros_like(n)
    seg = 2048
    for i in range(0, len(n), seg // 2):              # overlapping windowed segments, each its own band
        u = min(i / max(len(n) - 1, 1), 1.0)
        fc = f0 * (f1 / f0) ** u
        sos = butter(2, [fc / 1.6, fc * 1.6], "band", fs=SR, output="sos")
        chunk = sosfilt(sos, n[max(0, i - seg): i + seg])[-min(seg, len(n) - i):]
        w = np.hanning(len(chunk))
        out[i:i + len(chunk)] += chunk * w
    env = np.sin(np.pi * t / d) ** 2
    y = out * env
    return db(level) * y / np.abs(y).max()


def whoosh(level=-29):
    return noise_sweep(0.95, 500, 2600, level)


def swish(level=-31):
    return noise_sweep(0.5, 1800, 700, level)


def chime(f=659.25, level=-27):
    t = _t(2.2)
    y = (np.sin(2 * np.pi * f * t) + 0.55 * np.sin(2 * np.pi * 1.5 * f * t) + 0.18 * np.sin(2 * np.pi * 3 * f * t))
    y *= np.exp(-t / 0.75) * np.minimum(t / 0.006, 1)
    return db(level) * y / np.abs(y).max()


def pluck(level_peak=0.15):
    """The s13 string: the 200-point second-difference matrix's first 12 modes, plucked at x = 0.2."""
    N = 200
    H = 1 / (N + 1)
    XS = np.arange(1, N + 1) / (N + 1)
    L2 = (np.diag(-2 * np.ones(N)) + np.diag(np.ones(N - 1), 1) + np.diag(np.ones(N - 1), -1)) / H ** 2
    lam, vec = np.linalg.eigh(L2)
    o = np.argsort(-lam)
    lam, vec = lam[o][:12], vec[:, o][:, :12]
    ck = vec.T @ np.where(XS < 0.2, XS / 0.2, (1 - XS) / 0.8)
    fk = 110.0 * np.sqrt(lam / lam[0])
    assert abs(fk[1] / fk[0] - 2) < 1e-3 and abs(fk[2] / fk[0] - 3) < 1e-3
    dur = (T.cut_ch7 - 0.35) - (T.pluck + 1.2)
    t = _t(dur)
    y = sum(abs(ck[k]) * np.sqrt(k + 1) * np.sin(2 * np.pi * fk[k] * t) * np.exp(-t * (1 + 0.35 * k) / 2.6)
            for k in range(12))
    y *= np.minimum(t / 0.004, 1) * np.clip((dur - t) / 0.8, 0, 1)
    return level_peak * y / np.abs(y).max()


# ── the cue sheet: (time, sound). Animations start `lead` = 0.15 s before their beat; sounds sit on the landing. ──
L = -0.08
CUES = []
for k, t in enumerate([T.cut_ch1, T.cut_ch2, T.cut_ch3 + 0.45, T.cut_ch4, T.cut_ch5, T.cut_ch6, T.cut_ch7,
                       T.cut_outro]):
    CUES += [(t + 0.05, whoosh()), (t + 1.0, chime(659.25 if k % 2 == 0 else 587.33))]
CUES += [(T.cut_recap + 0.1, whoosh(-31))]
CUES += [(T.hundredth + L, tick(1500)), (T.one_line + 0.3 + L, chime(783.99, -28)), (T.flipped + 0.2, swish()),
         (T.claim + 0.4 + L, chime(523.25, -29)), (T.limit + L, tick(1400)), (T.eight_dims + 0.6 + L, tick()),
         (T.took + 0.4 + L, tick(1500)),
         (T.no_limits + 0.45, thud()), (T.no_limits + 1.45, thud()),
         (T.all_zeros + L, tick(1300)), (T.null_space + 0.3 + L, tick(1500)), (T.det_zero + L, tick(1300)),
         (T.no_way + 0.4, thud()), (T.two_x + L, swish()),
         (T.plus_c + L, tick(1600)),
         *[(t + L, tick(1250 + 120 * j, -29)) for j, t in
           enumerate([T.slides + 0.3, T.slides + 2.0, T.four_times, T.four_times + 1.5])],
         (T.four_times + 2.7 + L, tick(1800)),
         (T.cos_swings + 0.2, swish()), (T.sin_swings + 0.2, swish()), (T.quarter + 0.2, swish(-30)),
         (T.rotation + L, tick()), (T.twice + 0.2, swish()), (T.full_turn + 0.2, swish()),
         (T.full_turn + 1.4, swish()), (T.i_squared + 0.4 + L, tick(1500)),
         (T.eighth + 0.3, swish()), (T.det_two + L, tick()), (T.inverse - 0.25, thud(-27)),
         (T.turn_back + 0.1, swish()), (T.out_comes + 0.2, tick(1500)), (T.check + 1.7 + L, tick(1900)),
         (T.plus_c2 + 0.2 + L, chime(659.25, -30)),
         (T.not_sine + 1.4 + L, thud(-28)), (T.not_x2 + 1.3 + L, thud(-28)), (T.itself + 0.2 + L, chime(783.99, -28)),
         (T.lambda_x + 0.4 + L, tick(1600)), (T.one_family + 0.2 + L, tick()),
         (T.operator + 0.4, swish(-32)), (T.plane2 + L, tick(1200)),
         (T.conditions - 0.3 + L, tick(1400)), (T.conditions + 0.6 + L, tick(1600)),
         *[(T.multiplied - 0.2 + 0.4 * j + L, tick(1300 + 200 * j, -29)) for j in range(3)],
         (T.algebra + L, tick()),
         (T.pinned + 0.6 + L, tick(1300)), (T.one_m2_one + L, tick(1500)), (T.pin_ends + 0.2 + L, tick(1300)),
         *[(t + L, tick(f, -28)) for t, f in ((T.arch1, 1100), (T.arch2, 1400), (T.arch3, 1700))],
         (T.eigvals + 0.3 + L, tick()),
         *[(t + L, tick(f, -29)) for t, f in ((T.how_fast + 1.2, 1100), (T.octave, 1400), (T.three_fast + 0.3, 1700))],
         (T.pluck + 1.2, pluck()),
         (T.x_plus_h + L, tick(1500)), (T.shift + 0.3, swish()), (T.slides_h + 0.9, swish()),
         (T.asterisk + 0.2 + L, tick(1800)), (T.zero_series - 0.2, tick(1300)), (T.zero_series + 1.0 + L, thud(-28)),
         (T.no_det + 0.3, thud()), (T.every_eigenvalue, swish(-31)), (T.takes_limit + L, tick(1500)),
         (T.quantum + 0.3 + L, tick(1600)),
         *[(t + L, tick(1300 + 150 * j, -29)) for j, t in
           enumerate([T.r_plus_c - 0.2, T.r_rotation - 0.1, T.r_eigen, T.r_string])],
         (T.r_thesis + L, chime(523.25, -28)), (T.r_limit - 0.6 + L, chime(783.99, -27))]


def main():
    if not NARR.exists():
        shutil.copy2(MASTER, NARR)
    sr, raw = wavfile.read(NARR)
    assert sr == SR and raw.ndim == 1 and raw.dtype == np.int16
    voice = raw.astype(np.float64) / 32768
    bed = np.zeros_like(voice)
    for t, snd in CUES:
        i = int(round(t * SR))
        n = min(len(snd), len(bed) - i)
        bed[i:i + n] += snd[:n]
    touched = uniform_filter1d((np.abs(bed) > 1e-6).astype(np.float32), int(0.05 * SR)) > 0
    mix = voice + bed
    thr = db(-1.7)                                        # keep the master's headroom where the bed adds
    need = np.where(touched, np.minimum(1.0, thr / np.maximum(np.abs(mix), 1e-9)), 1.0)
    w = int(0.02 * SR)
    gain = uniform_filter1d(minimum_filter1d(need, 2 * w + 1), w)       # hold the dip ±20 ms, then smooth it
    mix = np.where(touched, mix * np.minimum(gain, 1.0), voice)
    assert np.abs(mix[touched]).max() < thr * 1.001
    out = raw.copy()
    out[touched] = np.clip(np.round(mix[touched] * 32768), -32768, 32767).astype(np.int16)
    wavfile.write(MASTER, SR, out)
    wavfile.write(A / "sfx.wav", SR, np.clip(np.round(bed * 32768), -32768, 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(MASTER), "-codec:a", "libmp3lame", "-b:a", "192k",
                    str(A / "audio.mp3")], check=True)
    print(f"{len(CUES)} cues mixed into {MASTER.name}; {touched.mean() * 100:.1f}% of samples touched; "
          f"bed peak {20 * np.log10(np.abs(bed).max()):.1f} dBFS")


if __name__ == "__main__":
    main()
