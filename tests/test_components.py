"""Linear-algebra drawing blocks promoted from videos 006–010."""

import numpy as np
import pytest

from aion.components.linalg import fmt, grid_lines, panel


def test_fmt_numbers():
    assert [fmt(2.0), fmt(-0.0001), fmt(2.718281), fmt(-3.5), fmt(23.1407)] == ["2", "0", "2.72", "-3.5", "23.14"]


def test_grid_lines_identity_and_collapse():
    box = (-7.3, -4.2, 7.3, 4.2)
    minor, major, axes = grid_lines(np.eye(2), (0, 0), 1.0, box)
    assert len(axes) == 2 and len(major) == 14 + 8   # x = -7..7 minus 0, y = -4..4 minus 0
    for line in [*major, *axes]:                                   # everything clipped to the box
        for p in (line.get_start(), line.get_end()):
            assert box[0] - 1e-6 <= p[0] <= box[2] + 1e-6 and box[1] - 1e-6 <= p[1] <= box[3] + 1e-6
    # a singular matrix (element-wise exp of pi*J has det 0): every line lands on the one image line
    E = np.exp(np.pi * np.array([[0.0, -1.0], [1.0, 0.0]]))
    assert abs(np.linalg.det(E)) < 1e-9
    d = E[:, 0] / np.linalg.norm(E[:, 0])
    for line in [*grid_lines(E, (0, 0), 1.0, box)[1]]:
        for p in (line.get_start(), line.get_end()):
            assert abs(p[0] * d[1] - p[1] * d[0]) < 1e-6           # on the line through 0 along column 1


def test_panel_bounds():
    r = panel(-6.0, -3.0, -1.0, 3.0)
    assert np.allclose([r.width, r.height], [5.0, 6.0]) and np.allclose(r.get_center()[:2], [-3.5, 0.0])


@pytest.mark.tex
def test_mat_cells_and_columns():
    from aion import Mat

    M = Mat([["0", r"-\pi"], [r"\pi", 0.0]])
    assert len(M.cols) == 2 and len(M.cols[0]) == 2 and M.cell(1, 1).get_tex_string() == "0"
    assert M.br.width > M.cols[0].width + M.cols[1].width
