"""Prototype: Fourier's portrait as one continuous line (contours of blurred brightness, toured greedily)."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage

SRC = "videos/003-fourier-series/assets/images/fourier_portrait.jpg"
im = Image.open(SRC).convert("L").crop((70, 80, 900, 1110))
W = 420
im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
g = np.asarray(im, float) / 255
sig, levels, minlen = float(sys.argv[1]), [float(x) for x in sys.argv[2].split(",")], float(sys.argv[3])
b = ndimage.gaussian_filter(g, sig)
cs = plt.figure().add_subplot().contour(b, levels=levels)
segs = [p for lv in cs.allsegs for p in lv if len(p) > 2]
segs = [p for p in segs if np.sum(np.hypot(*np.diff(p, axis=0).T)) > minlen]
print(len(segs), "contours", sum(len(p) for p in segs), "pts")
fig, ax = plt.subplots(figsize=(6, 7.4), facecolor="k")
ax.set_facecolor("k")
for p in segs:
    ax.plot(p[:, 0], -p[:, 1], color="#FFD43B", lw=0.6)
ax.set_aspect("equal"); ax.axis("off")
fig.savefig(sys.argv[4], dpi=110, facecolor="k")
