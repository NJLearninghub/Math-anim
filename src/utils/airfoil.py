import math
import numpy as np


def naca4_points(m: float, p: float, t: float, n: int = 100):
    """Return upper and lower surface points for a NACA 4-digit airfoil.

    m: max camber fraction (e.g. 0.04 for NACA 4xxx)
    p: chordwise position of max camber (e.g. 0.4)
    t: thickness fraction (e.g. 0.12)
    Cosine spacing for better LE resolution.
    Returns (upper, lower) each as list of (x, y) tuples, x in [0,1].
    """
    upper, lower = [], []
    for i in range(n + 1):
        x = (1 - math.cos(i * math.pi / n)) / 2
        a0, a1, a2, a3, a4 = 0.2969, -0.1260, -0.3516, 0.2843, -0.1015
        yt = 5 * t * (a0 * math.sqrt(x) + a1 * x + a2 * x**2 + a3 * x**3 + a4 * x**4)
        if m == 0 or p == 0:
            yc, dyc = 0.0, 0.0
        elif x < p:
            yc  = m / p**2 * (2 * p * x - x**2)
            dyc = 2 * m / p**2 * (p - x)
        else:
            yc  = m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2)
            dyc = 2 * m / (1 - p)**2 * (p - x)
        theta = math.atan(dyc)
        upper.append((x - yt * math.sin(theta), yc + yt * math.cos(theta)))
        lower.append((x + yt * math.sin(theta), yc - yt * math.cos(theta)))
    return upper, lower


def naca0012_polygon(n: int = 80):
    """Closed polygon for NACA 0012 (symmetric), x in [0,1].
    Returns np.ndarray shape (2n+1, 2): upper LE→TE then lower TE→LE.
    """
    upper, lower = naca4_points(0, 0, 0.12, n)
    pts = upper + list(reversed(lower[1:-1]))
    return np.array(pts)


def naca4412_polygon(n: int = 80):
    """Closed polygon for NACA 4412 (cambered), x in [0,1]."""
    upper, lower = naca4_points(0.04, 0.4, 0.12, n)
    pts = upper + list(reversed(lower[1:-1]))
    return np.array(pts)


def to_manim(pts_2d: np.ndarray, chord: float = 4.0, center=None):
    """Scale unit-chord 2-D airfoil points to Manim 3-D coordinates.

    pts_2d: (N, 2) array with x in [0,1]
    Returns (N, 3) array suitable for VMobject point arrays.
    """
    if center is None:
        center = np.array([0.0, 0.0, 0.0])
    scaled = pts_2d * chord
    # centre airfoil at midchord (x=0.5*chord → 0)
    scaled[:, 0] -= chord / 2
    return np.column_stack([scaled, np.zeros(len(scaled))]) + center


def camber_line(m: float, p: float, n: int = 60):
    """Return (x, yc) camber line arrays for NACA 4-digit airfoil."""
    xs = np.linspace(0, 1, n)
    ycs = []
    for x in xs:
        if m == 0 or p == 0:
            ycs.append(0.0)
        elif x < p:
            ycs.append(m / p**2 * (2 * p * x - x**2))
        else:
            ycs.append(m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2))
    return xs, np.array(ycs)
