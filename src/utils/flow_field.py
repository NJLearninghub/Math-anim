"""Joukowski potential flow around a near-NACA airfoil.

The Joukowski transform  z = ζ + a²/ζ  maps a circle to an airfoil
shape. We compute the exact complex potential in the ζ-plane and
convert velocities back to the physical z-plane via the chain rule.
"""
import cmath
import math
import numpy as np


class JoukowskiFlow:
    """Exact potential flow (with lift) around a Joukowski airfoil.

    Parameters
    ----------
    alpha_deg : angle of attack in degrees
    a         : Joukowski parameter (half-chord scale)
    eps       : circle offset in x (controls thickness)
    delta     : circle offset in y (controls camber)
    U         : free-stream speed
    """

    def __init__(self, alpha_deg: float = 8.0, a: float = 1.0,
                 eps: float = 0.12, delta: float = 0.04, U: float = 1.0):
        self.alpha = math.radians(alpha_deg)
        self.a = a
        self.U = U
        # Circle centre in ζ-plane
        self.c = complex(-eps * a, delta * a)
        # Circle radius (passes through z=a on real axis)
        self.R = abs(a - self.c)
        # Kutta condition: circulation
        self.Gamma = 4 * math.pi * U * self.R * math.sin(self.alpha + math.atan2(delta, 1 + eps))
        # Chord scale factor (for converting to Manim coords)
        z_te = self._joukowski(a)
        z_le = self._joukowski(-a)
        self.chord_raw = abs(z_te - z_le)
        # Desired chord in Manim units
        self.chord_manim = 5.0
        self.scale = self.chord_manim / self.chord_raw
        # x-offset so LE is at x=−chord/2
        self.x_offset = z_le.real * self.scale + self.chord_manim / 2

    # ------------------------------------------------------------------
    def _joukowski(self, zeta: complex) -> complex:
        return zeta + self.a**2 / zeta

    def _inv_joukowski(self, z: complex) -> complex:
        """Outer branch of ζ = (z ± √(z²−4a²)) / 2."""
        disc = cmath.sqrt(z**2 - 4 * self.a**2)
        z1 = (z + disc) / 2
        z2 = (z - disc) / 2
        return z1 if abs(z1) >= abs(z2) else z2

    def _dzdz_eta(self, zeta: complex) -> complex:
        return 1 - self.a**2 / zeta**2

    # ------------------------------------------------------------------
    def velocity(self, x_screen: float, y_screen: float):
        """Return (u, v) at screen-space position, or None if inside airfoil."""
        # Convert screen → raw Joukowski z-plane
        x_raw = (x_screen + self.x_offset) / self.scale
        y_raw = y_screen / self.scale
        z = complex(x_raw, y_raw)

        zeta = self._inv_joukowski(z)
        zeta_c = zeta - self.c  # relative to circle centre

        if abs(zeta_c) <= self.R * 1.02:
            return None  # inside the airfoil body

        dzdz = self._dzdz_eta(zeta)
        if abs(dzdz) < 1e-9:
            return None  # trailing-edge singularity guard

        alpha = self.alpha
        R, U = self.R, self.U
        Gamma = self.Gamma

        dF_dzeta_c = (
            U * cmath.exp(-1j * alpha)
            - U * cmath.exp(1j * alpha) * R**2 / zeta_c**2
            + 1j * Gamma / (2 * math.pi * zeta_c)
        )
        dF_dz = dF_dzeta_c / dzdz

        u = dF_dz.real
        v = -dF_dz.imag
        return u, v

    # ------------------------------------------------------------------
    def airfoil_manim_pts(self, n: int = 200) -> np.ndarray:
        """Return closed airfoil outline as (N+1, 3) Manim-coord array."""
        angles = np.linspace(0, 2 * math.pi, n, endpoint=False)
        pts = []
        for theta in angles:
            zeta_c = self.R * complex(math.cos(theta), math.sin(theta))
            zeta = zeta_c + self.c
            z = self._joukowski(zeta)
            x_m = z.real * self.scale - self.x_offset
            y_m = z.imag * self.scale
            pts.append([x_m, y_m, 0.0])
        pts.append(pts[0])  # close
        return np.array(pts)

    # ------------------------------------------------------------------
    def streamline(self, x0: float, y0: float,
                   n_steps: int = 400, dt: float = 0.03):
        """Integrate a streamline starting at (x0, y0) using RK4.

        Returns list of (x, y) screen-space points.
        """
        pts = []
        x, y = x0, y0
        for _ in range(n_steps):
            uv = self.velocity(x, y)
            if uv is None:
                break
            u, v = uv
            mag = math.hypot(u, v)
            if mag < 1e-6:
                break
            # RK4
            k1u, k1v = u, v
            uv2 = self.velocity(x + 0.5*dt*k1u, y + 0.5*dt*k1v)
            if uv2 is None:
                break
            k2u, k2v = uv2
            uv3 = self.velocity(x + 0.5*dt*k2u, y + 0.5*dt*k2v)
            if uv3 is None:
                break
            k3u, k3v = uv3
            uv4 = self.velocity(x + dt*k3u, y + dt*k3v)
            if uv4 is None:
                break
            k4u, k4v = uv4
            x += dt * (k1u + 2*k2u + 2*k3u + k4u) / 6
            y += dt * (k1v + 2*k2v + 2*k3v + k4v) / 6
            pts.append((x, y))
            if x > 7.5 or x < -7.5 or abs(y) > 5.0:
                break
        return pts

    # ------------------------------------------------------------------
    def pressure_coeff(self, n: int = 80):
        """Return (x_upper, Cp_upper, x_lower, Cp_lower) along chord.

        x values are in Manim screen coords.
        """
        angles_upper = np.linspace(math.pi, 0, n)       # upper: LE → TE
        angles_lower = np.linspace(math.pi, 2*math.pi, n)  # lower: LE → TE

        def _cp_at_angle(theta):
            zeta_c = self.R * complex(math.cos(theta), math.sin(theta))
            zeta = zeta_c + self.c
            z = self._joukowski(zeta)
            x_m = z.real * self.scale - self.x_offset
            uv = self.velocity(x_m, 0.0)  # surface point
            # Surface velocity from exact formula
            dzdz = self._dzdz_eta(zeta)
            if abs(dzdz) < 1e-9:
                return x_m, 1.0
            dF = (self.U * cmath.exp(-1j*self.alpha)
                  - self.U * cmath.exp(1j*self.alpha) * self.R**2 / zeta_c**2
                  + 1j*self.Gamma / (2*math.pi*zeta_c))
            v_surf = abs(dF / dzdz)
            cp = 1 - (v_surf / self.U)**2
            return x_m, float(cp)

        xu = [_cp_at_angle(a)[0] for a in angles_upper]
        cpu = [_cp_at_angle(a)[1] for a in angles_upper]
        xl = [_cp_at_angle(a)[0] for a in angles_lower]
        cpl = [_cp_at_angle(a)[1] for a in angles_lower]
        return xu, cpu, xl, cpl
