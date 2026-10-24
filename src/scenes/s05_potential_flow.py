import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import (BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE,
                               FAST_COLOR, SLOW_COLOR, ANNOTATION)
from src.utils.flow_field import JoukowskiFlow


class PotentialFlowScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        flow = JoukowskiFlow(alpha_deg=8)

        # ── Title ──────────────────────────────────────────────────────
        title = Text("Potential Flow Around an Airfoil", font_size=34, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # ── Joukowski transform intro ──────────────────────────────────
        transform_eq = MathTex(
            r"z = \zeta + \frac{a^2}{\zeta}",
            font_size=38, color=ANNOTATION,
        )
        transform_eq.to_edge(LEFT, buff=1.0).shift(DOWN * 0.5)
        transform_label = Text("Joukowski transform", font_size=20, color=GRAY_B)
        transform_label.next_to(transform_eq, DOWN, buff=0.2)

        self.play(Write(transform_eq), FadeIn(transform_label))
        self.wait(1.0)

        # ── Build airfoil VMobject ─────────────────────────────────────
        pts3d = flow.airfoil_manim_pts(n=200)
        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.9)
        airfoil.set_stroke(AIRFOIL_STROKE, width=2.5)

        self.play(Create(airfoil, run_time=1.8))
        self.play(FadeOut(transform_eq), FadeOut(transform_label))
        self.wait(0.3)

        # ── Velocity field function (clipped) ──────────────────────────
        def vel_field(pos):
            uv = flow.velocity(pos[0], pos[1])
            if uv is None:
                return np.array([0.0, 0.0, 0.0])
            u, v = uv
            mag = np.hypot(u, v)
            if mag > 3.5:
                u, v = u / mag * 3.5, v / mag * 3.5
            return np.array([u, v, 0.0])

        # ── StreamLines ────────────────────────────────────────────────
        stream = StreamLines(
            vel_field,
            x_range=[-7, 7, 0.4],
            y_range=[-3.5, 3.5, 0.35],
            dt=0.06,
            max_anchors_per_line=60,
            stroke_width=1.5,
            stroke_color=BLUE_C,
            opacity=0.75,
        )

        self.add(stream)
        stream.start_animation(warm_up=True, flow_speed=1.8, time_width=0.25)

        # Labels while flow animates
        fast_lbl = Text("Faster flow →", font_size=20, color=FAST_COLOR)
        fast_lbl.move_to(UP * 1.3 + RIGHT * 1.5)
        slow_lbl = Text("Slower flow →", font_size=20, color=SLOW_COLOR)
        slow_lbl.move_to(DOWN * 1.2 + RIGHT * 1.5)

        self.play(FadeIn(fast_lbl), FadeIn(slow_lbl))
        self.wait(3.0)

        # Stagnation point dots
        le_pt = airfoil.get_left()
        te_pt = airfoil.get_right()
        stag_le = Dot(le_pt, color=RED, radius=0.09)
        stag_te = Dot(te_pt, color=RED, radius=0.09)
        stag_lbl = Text("Stagnation\npoints", font_size=18, color=RED)
        stag_lbl.next_to(stag_le, LEFT, buff=0.25)

        self.play(FadeIn(stag_le), FadeIn(stag_te), FadeIn(stag_lbl))
        self.wait(3.0)

        stream.end_animation()

        # ── Static arrow vector field ──────────────────────────────────
        avf = ArrowVectorField(
            vel_field,
            x_range=[-6.5, 6.5, 1.1],
            y_range=[-3.2, 3.2, 1.1],
            length_func=lambda n: 0.5 * n,
            color=BLUE_C,
        )
        self.play(Create(avf, run_time=1.5))
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            title, airfoil, avf, fast_lbl, slow_lbl,
            stag_le, stag_te, stag_lbl,
        )))
