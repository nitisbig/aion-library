"""aion: math animation library for the channel.

Importing this package puts TinyTeX's LaTeX binaries (installed via pytinytex)
on PATH, so Manim's MathTex/Tex work without any shell configuration.
"""

import os
import shutil


def _ensure_latex_on_path() -> None:
    if shutil.which("latex") and shutil.which("dvisvgm"):
        return
    try:
        import pytinytex

        bin_dir = pytinytex.get_tinytex_path()
    except Exception:
        bin_dir = os.path.expanduser("~/.pytinytex/.TinyTeX/bin/x86_64-linux")
    if os.path.isdir(bin_dir):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


_ensure_latex_on_path()
