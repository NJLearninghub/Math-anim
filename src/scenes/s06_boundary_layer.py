import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE, BL_COLOR, ANNOTATION
from src.utils.airfoil import naca0012_polygon, to_manim


class BoundaryLayerScene(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("Boundary Layer & Viscosity", font_size=34, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # ── Airfoil ────────────────────────────────────────────────────
        poly = naca0012_polygon(80)
        pts3d = to_manim(poly, chord=5.0)
        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.9)
        airfoil.set_stroke(AIRFOIL_STROKE, width=2.0)

        self.play(Create(airfoil, run_time=1.5))

        # Highlight leading-edge area
        le_box = SurroundingRectangle(
            VGroup(Dot(airfoil.get_left() + RIGHT * 1.0)),
            color=YELLOW, buff=0.6,
        )
        self.play(Create(le_box))
        self.wait(0.8)

        # ── Zoom in to LE region ───────────────────────────────────────
        self.play(
            self.camera.frame.animate
                .set_width(3.5)
                .move_to(airfoil.get_left() + RIGHT * 1.2 + UP * 0.15),
            FadeOut(le_box),
            run_time=1.8,
        )
        self.wait(0.5)

        # ── Velocity profile arrows ────────────────────────────────────
        profile_group = VGroup()
        n_stations = 8
        xs = np.linspace(-1.8, 1.0, n_stations)
        for x in xs:
            y_surface = 0.22 * np.sqrt(max(x + 2.5, 0.01)) - 0.02
            base = np.array([x, y_surface + airfoil.get_center()[1], 0])
            n_arrows = 6
            for j in range(1, n_arrows + 1):
                frac = j / n_arrows
                length = 0.38 * frac**0.6
                arr = Arrow(
                    base + UP * (j - 1) * 0.065,
                    base + UP * (j - 1) * 0.065 + RIGHT * length,
                    buff=0, max_tip_length_to_length_ratio=0.3,
                    stroke_width=1.5,
                    color=interpolate_color(PURPLE_C, BLUE_C, frac),
                )
                profile_group.add(arr)

        self.play(Create(profile_group, lag_ratio=0.05, run_time=2.0))

        # No-slip label
        no_slip = Text("no-slip: u=0 at wall", font_size=9, color=RED)
        no_slip.move_to(airfoil.get_left() + RIGHT * 0.0 + UP * 0.52)
        self.play(FadeIn(no_slip))

        # Boundary layer thickness curve
        x_bl = np.linspace(-2.0, 2.0, 80)
        delta = 0.14 * np.sqrt(np.clip(x_bl + 2.5, 0.01, None))
        y_center = airfoil.get_center()[1]
        bl_pts = np.column_stack([x_bl, delta + y_center + 0.05, np.zeros(80)])
        bl_curve = VMobject()
        bl_curve.set_points_smoothly(bl_pts)
        bl_curve.set_stroke(BL_COLOR, width=2.5, opacity=0.9)

        self.play(Create(bl_curve))
        bl_label = Text("δ(x) boundary layer", font_size=9, color=BL_COLOR)
        bl_label.next_to(bl_curve.get_end(), RIGHT, buff=0.05)
        self.play(FadeIn(bl_label))
        self.wait(1.5)

        # ── Zoom back out ──────────────────────────────────────────────
        self.play(
            self.camera.frame.animate.set_width(14.2).move_to(ORIGIN),
            run_time=1.5,
        )

        # ── Boundary layer thickness formula ──────────────────────────
        bl_eq = MathTex(
            r"\delta \approx \frac{5x}{\sqrt{Re_x}}",
            font_size=40, color=BL_COLOR,
        )
        bl_eq.to_corner(DR, buff=0.6)
        bl_eq_label = Text("Laminar BL thickness", font_size=20, color=GRAY_B)
        bl_eq_label.next_to(bl_eq, UP, buff=0.2)

        mu_eq = MathTex(
            r"\mu\,\nabla^2\vec{u}",
            font_size=38, color=GREEN,
        )
        mu_eq.to_corner(DL, buff=0.6)
        mu_label = Text("Viscous term (N-S)\ndominates near wall",
                        font_size=20, color=GREEN)
        mu_label.next_to(mu_eq, UP, buff=0.15)

        self.play(Write(bl_eq), FadeIn(bl_eq_label))
        self.play(Write(mu_eq), FadeIn(mu_label))
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            title, airfoil, profile_group, no_slip,
            bl_curve, bl_label, bl_eq, bl_eq_label,
            mu_eq, mu_label,
        )))
