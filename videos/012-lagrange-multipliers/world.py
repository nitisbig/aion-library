"""The mountain and the trail: the one landscape shared by verify.py and every scene (pure numpy, no side effects)."""
import numpy as np

TRAIL_A, TRAIL_B = 2.5, 2.0


def hill(px, py):
    """Height f(x, y): a main peak plus a smaller shoulder."""
    return 3.0 * np.exp(-((px - 0.8) ** 2 + (py - 0.6) ** 2) / 3.0) + 1.4 * np.exp(-((px + 1.8) ** 2 + (py + 1.2) ** 2) / 2.0)


def hill_grad(px, py):
    """The gradient of f, exactly."""
    a = 3.0 * np.exp(-((px - 0.8) ** 2 + (py - 0.6) ** 2) / 3.0)
    b = 1.4 * np.exp(-((px + 1.8) ** 2 + (py + 1.2) ** 2) / 2.0)
    return np.array([a * -2 * (px - 0.8) / 3.0 + b * -(px + 1.8), a * -2 * (py - 0.6) / 3.0 + b * -(py + 1.2)])


def trail(s):
    """The point of the trail at parameter s."""
    return TRAIL_A * np.cos(s), TRAIL_B * np.sin(s)


def trail_tangent(s):
    """d/ds of the trail."""
    return np.array([-TRAIL_A * np.sin(s), TRAIL_B * np.cos(s)])


def trail_grad(px, py):
    """The gradient of g(x, y) = x^2 / a^2 + y^2 / b^2."""
    return np.array([2 * px / TRAIL_A**2, 2 * py / TRAIL_B**2])
