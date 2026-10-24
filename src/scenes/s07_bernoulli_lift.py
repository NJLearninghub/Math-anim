import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import (BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE,
                               FAST_COLOR, SLOW_COLOR, LIFT_COLOR)
from src.utils.flow_field import JoukowskiFlow


class BernoulliLiftScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        flow = JoukowskiFlow(alpha_deg=8)

        title = Text("Bernoulli's Principle → Lift", font_size=34, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # ── Airfoil ────────────────────────────────────────────────────
        pts3d = flow.airfoil_manim_pts(n=200)
        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.9)
        airfoil.set_stroke(AIRFOIL_STROKE, width=2.0)
        self.play(Create(airfoil, run_time=1.2))

        # ── Bernoulli equation ─────────────────────────────────────────
        bernoulli = MathTex(
            r"p + \tfrac{1}{2}\rho v^2 = \mathrm{const}",
            font_size=40,
        )
        bernoulli.to_corner(UL, buff=0.8)
        bern_label = Text("(from N-S, steady, inviscid)",
                          font_size=18, color=GRAY_B)
        bern_label.next_to(bernoulli, DOWN, buff=0.1)
        self.play(Write(bernoulli), FadeIn(bern_label))
        self.wait(0.8)

        # Speed annotation arrows above/below
        fast_arr = Arrow(LEFT * 0.5 + UP * 1.35, RIGHT * 0.8 + UP * 1.35,
                         color=FAST_COLOR, buff=0, stroke_width=4)
        slow_arr = Arrow(LEFT * 0.5 + DOWN * 0.85, RIGHT * 0.8 + DOWN * 0.85,
                         color=SLOW_COLOR, buff=0, stroke_width=4)
        fast_txt = Text("v↑  (faster above)", font_size=20, color=FAST_COLOR)
        slow_txt = Text("v↓  (slower below)", font_size=20, color=SLOW_COLOR)
        fast_txt.next_to(fast_arr, RIGHT, buff=0.15)
        slow_txt.next_to(slow_arr, RIGHT, buff=0.15)

        self.play(GrowArrow(fast_arr), FadeIn(fast_txt))
        self.play(GrowArrow(slow_arr), FadeIn(slow_txt))
        self.wait(0.8)

        # Pressure arrows
        p_low  = Text("p  low",  font_size=19, color=FAST_COLOR)
        p_high = Text("p  high", font_size=19, color=SLOW_COLOR)
        p_low.move_to(UP * 1.0 + LEFT * 1.8)
        p_high.move_to(DOWN * 0.6 + LEFT * 1.8)
        self.play(FadeIn(p_low), FadeIn(p_high))
        self.wait(0.8)

        # ── Cp distribution ────────────────────────────────────────────
        xu, cpu, xl, cpl = flow.pressure_coeff(n=60)

        def make_cp_curve(xs, cps, scale=0.6, flip=False):
            sign = -1 if not flip else 1
            pts = [[x, sign * cp * scale, 0] for x, cp in zip(xs, cps)]
            c = VMobject()
            c.set_points_smoothly(np.array(pts))
            return c

        cp_upper = make_cp_curve(xu, cpu, scale=0.55, flip=False)
        cp_lower = make_cp_curve(xl, cpl, scale=0.55, flip=True)
        cp_upper.set_stroke(FAST_COLOR, width=2.5)
        cp_lower.set_stroke(SLOW_COLOR, width=2.5)

        cp_axes = Axes(
            x_range=[-2.8, 2.8, 1.0],
            y_range=[-1.8, 1.8, 0.5],
            x_length=5.6,
            y_length=3.6,
            axis_config={"color": GRAY_C, "stroke_width": 1.0},
            tips=False,
        ).to_corner(DR, buff=0.5)

        cp_title = Text("Cₚ distribution", font_size=20, color=GRAY_B)
        cp_title.next_to(cp_axes, UP, buff=0.1)

        self.play(FadeOut(VGroup(fast_arr, slow_arr, fast_txt, slow_txt,
                                  p_low, p_high)))
        self.play(Create(cp_axes), FadeIn(cp_title))
        self.play(Create(cp_upper, run_time=1.2), Create(cp_lower, run_time=1.2))
        self.wait(1.0)

        # ── Lift arrow ─────────────────────────────────────────────────
        lift_arrow = Arrow(airfoil.get_center() + DOWN * 0.1,
                           airfoil.get_center() + UP * 1.8,
                           color=LIFT_COLOR, buff=0, stroke_width=5)
        lift_label = Text("L  (Lift)", font_size=28, color=LIFT_COLOR)
        lift_label.next_to(lift_arrow, RIGHT, buff=0.15)

        self.play(GrowArrow(lift_arrow), FadeIn(lift_label))

        kj_eq = MathTex(r"L' = \rho_\infty V_\infty \Gamma",
                        font_size=36, color=LIFT_COLOR)
        kj_label = Text("Kutta–Joukowski theorem", font_size=18, color=GRAY_B)
        kj_eq.to_corner(UR, buff=0.7)
        kj_label.next_to(kj_eq, DOWN, buff=0.12)

        self.play(Write(kj_eq), FadeIn(kj_label))
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            title, airfoil, bernoulli, bern_label,
            cp_axes, cp_title, cp_upper, cp_lower,
            lift_arrow, lift_label, kj_eq, kj_label,
        )))
