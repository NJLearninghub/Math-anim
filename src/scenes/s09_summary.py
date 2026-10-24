import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE, FLOW_COLOR
from src.utils.flow_field import JoukowskiFlow


class SummaryScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        flow = JoukowskiFlow(alpha_deg=8)

        # ── Background airfoil + faint flow ───────────────────────────
        pts3d = flow.airfoil_manim_pts(n=200)
        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.4)
        airfoil.set_stroke(AIRFOIL_STROKE, width=1.5, opacity=0.5)
        airfoil.scale(0.7).to_edge(DOWN, buff=0.9)
        self.add(airfoil)

        # ── Title ──────────────────────────────────────────────────────
        title = Text("Key Equations", font_size=38, weight=BOLD, color=YELLOW_C)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title))

        # ── 2×2 equation grid ──────────────────────────────────────────
        eq1 = VGroup(
            Text("Continuity", font_size=20, color=BLUE_C),
            MathTex(r"\nabla\cdot\vec{u}=0", font_size=40),
        ).arrange(DOWN, buff=0.15)

        eq2 = VGroup(
            Text("Momentum (N-S)", font_size=20, color=ORANGE),
            MathTex(
                r"\rho\!\left(\frac{\partial\vec{u}}{\partial t}"
                r"+\vec{u}\!\cdot\!\nabla\vec{u}\right)"
                r"=-\nabla p+\mu\nabla^2\vec{u}+\vec{f}",
                font_size=28,
            ),
        ).arrange(DOWN, buff=0.15)

        eq3 = VGroup(
            Text("Reynolds Number", font_size=20, color=GREEN),
            MathTex(r"\mathrm{Re}=\frac{\rho UL}{\mu}", font_size=40),
        ).arrange(DOWN, buff=0.15)

        eq4 = VGroup(
            Text("Kutta–Joukowski Lift", font_size=20, color=YELLOW_C),
            MathTex(r"L'=\rho_\infty V_\infty\Gamma", font_size=40),
        ).arrange(DOWN, buff=0.15)

        grid = VGroup(
            VGroup(eq1, eq2).arrange(RIGHT, buff=0.9),
            VGroup(eq3, eq4).arrange(RIGHT, buff=0.9),
        ).arrange(DOWN, buff=0.65)
        grid.move_to(UP * 0.35)

        for eq in [eq1, eq2, eq3, eq4]:
            box = SurroundingRectangle(eq, color=GRAY_C, buff=0.2,
                                       corner_radius=0.1, stroke_width=1)
            self.play(Write(eq, run_time=1.0), Create(box, run_time=0.5))

        self.wait(1.0)

        # ── Closing tagline ────────────────────────────────────────────
        tagline = Text(
            "The equations that govern flight.",
            font_size=26, color=YELLOW_C, weight=BOLD,
        )
        tagline.to_edge(DOWN, buff=0.35)
        self.play(Write(tagline))
        self.wait(3.0)

        self.play(FadeOut(Group(*self.mobjects)))
