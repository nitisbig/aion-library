import sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from aion.drawings import portrait_line
from aion import fourier as F
z = portrait_line("videos/003-fourier-series/assets/images/fourier_portrait.jpg")
print(len(z), "pts")
zr = F.resample(np.append(z, z[0]), 8192)
fig, axs = plt.subplots(1, 3, figsize=(15, 6.5), facecolor="k")
for ax, N in zip(axs, (150, 300, 450)):
    c = F.coefficients(zr, N)
    t = np.linspace(0, 1, 12000, endpoint=False)
    w = sum(cn * np.exp(2j * np.pi * n * t) for n, cn in c.items())
    ax.plot(w.real, w.imag, color="#FFD43B", lw=0.5); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{2*N+1} circles", color="w")
fig.savefig("lab/2026-11-09-portrait-preview/recon.png", dpi=100, facecolor="k")
