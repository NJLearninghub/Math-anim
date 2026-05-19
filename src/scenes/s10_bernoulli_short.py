"""
Bernoulli's Equation — 60-second YouTube Short (9:16 vertical).

Frame: 4.5 units wide × 8 units tall  (pixel_width=1080, pixel_height=1920)
Airfoil chord: 2.8 Manim units (fits the narrow frame).

Structure:
  A  0–3s   Airfoil drawn; StreamLines start
  B  3–12s  Flow animation plays
  C  12–18s Bernoulli equation writes over animation
  D  18–28s Term p  — pressure colour overlay
  E  28–40s Term ½ρv² — speed difference arrows
  F  40–50s = const  — trade-off balance bars
  G  50–58s Net pressure → LIFT arrow
  H  58–60s Tagline fade-out
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import (BG_COLOR, FLOW_COLOR, FAST_COLOR, SLOW_COLOR,
                               AIRFOIL_FILL, AIRFOIL_STROKE, LIFT_COLOR, ANNOTATION)
from src.utils.flow_field import JoukowskiFlow


# ── Shared constants ───────────────────────────────────────────────────────────
CHORD_MANIM = 2.8          # airfoil chord in scene units
EQ_Y        =  3.15        # y-position for equation (top area)
LABEL_Y     = -3.25        # y-position for term labels (bottom area)
AIRFOIL_Y   =  0.15        # slight upward shift so equation has breathing room


class BernoulliShortScene(Scene):
    # ── Setup ──────────────────────────────────────────────────────────────────
    def setup(self):
        self.camera.background_color = BG_COLOR
        self.flow = JoukowskiFlow(alpha_deg=8)
        self._scale = CHORD_MANIM / self.flow.chord_manim  # ≈ 0.56

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _vel_field(self, pos):
        s = self._scale
        uv = self.flow.velocity(pos[0] / s, pos[1] / s)
        if uv is None:
            return np.array([0., 0., 0.])
        u, v = uv
        mag = np.hypot(u, v)
        if mag > 3.2:
            u, v = u / mag * 3.2, v / mag * 3.2
        return np.array([u, v, 0.])

    def _make_airfoil(self):
        pts = self.flow.airfoil_manim_pts(n=180).copy()
        pts[:, :2] *= self._scale
        pts[:, 1] += AIRFOIL_Y
        mob = VMobject()
        mob.set_points_smoothly(pts)
        mob.close_path()
        mob.set_fill(AIRFOIL_FILL, opacity=0.92)
        mob.set_stroke(AIRFOIL_STROKE, width=2.5)
        return mob

    def _surface_halves(self, airfoil):
        """Return (upper, lower) VMobjects tracing the airfoil surface."""
        raw = self.flow.airfoil_manim_pts(n=180).copy()
        raw[:, :2] *= self._scale
        raw[:, 1] += AIRFOIL_Y
        # Points go from TE→ upper → LE → lower → TE (parametric circle order)
        # Find index of leftmost point (leading edge)
        le_idx = int(np.argmin(raw[:, 0]))
        upper_pts = raw[:le_idx + 1]
        lower_pts = np.vstack([raw[le_idx:], raw[:1]])  # LE → TE via lower

        upper = VMobject()
        upper.set_points_smoothly(upper_pts)
        upper.set_stroke(FAST_COLOR, width=6, opacity=0.9)
        upper.set_fill(opacity=0)

        lower = VMobject()
        lower.set_points_smoothly(lower_pts)
        lower.set_stroke(SLOW_COLOR, width=6, opacity=0.9)
        lower.set_fill(opacity=0)
        return upper, lower

    def _make_stream(self):
        return StreamLines(
            self._vel_field,
            x_range=[-2.35, 2.35, 0.30],
            y_range=[-3.70, 3.70, 0.30],
            dt=0.05,
            max_anchors_per_line=55,
            stroke_width=1.8,
            stroke_color=FLOW_COLOR,
            opacity=0.72,
        )

    def _label(self, text, color=WHITE, size=30):
        t = Text(text, font_size=size, color=color)
        t.move_to(DOWN * abs(LABEL_Y))
        return t

    # ── Main construct ─────────────────────────────────────────────────────────
    def construct(self):
        # ── A: Airfoil + StreamLines (0–3s) ───────────────────────────────────
        airfoil = self._make_airfoil()
        self.play(Create(airfoil, run_time=1.5))

        stream = self._make_stream()
        self.add(stream)
        # Move airfoil in front of stream lines
        self.add(airfoil)
        stream.start_animation(warm_up=True, flow_speed=1.6, time_width=0.28)
        self.wait(1.5)   # finish segment A

        # ── B: Flow warms up — speed indicators (3–12s) ───────────────────────
        fast_arr = Arrow(LEFT * 1.5 + UP * (AIRFOIL_Y + 0.9),
                         RIGHT * 1.5 + UP * (AIRFOIL_Y + 0.9),
                         color=FAST_COLOR, buff=0, stroke_width=4,
                         max_tip_length_to_length_ratio=0.08)
        slow_arr = Arrow(LEFT * 1.2 + DOWN * (0.55 - AIRFOIL_Y),
                         RIGHT * 1.2 + DOWN * (0.55 - AIRFOIL_Y),
                         color=SLOW_COLOR, buff=0, stroke_width=4,
                         max_tip_length_to_length_ratio=0.08)
        fast_lbl = Text("faster", font_size=24, color=FAST_COLOR)
        slow_lbl = Text("slower", font_size=24, color=SLOW_COLOR)
        fast_lbl.next_to(fast_arr, RIGHT, buff=0.1)
        slow_lbl.next_to(slow_arr, RIGHT, buff=0.1)

        self.play(GrowArrow(fast_arr), GrowArrow(slow_arr), run_time=0.8)
        self.play(FadeIn(fast_lbl), FadeIn(slow_lbl), run_time=0.5)
        self.wait(5.2)   # hold through B

        self.play(FadeOut(fast_arr, slow_arr, fast_lbl, slow_lbl), run_time=0.5)

        # ── C: Equation reveal (12–18s) ───────────────────────────────────────
        eq = MathTex(
            r"p",
            r"+ \tfrac{1}{2}\rho v^2",
            r"+ \rho g h",
            r"= \mathrm{const}",
            font_size=40,
        )
        eq.move_to(UP * EQ_Y)

        # Fade ρgh (height term) slightly — airfoil at constant altitude
        eq[2].set_opacity(0.38)

        self.play(Write(eq, run_time=2.2))
        self.wait(3.8)   # end of C at ~18s

        # ── D: Term p — static pressure (18–28s) ──────────────────────────────
        p_box = SurroundingRectangle(eq[0], color=BLUE_C, buff=0.1, stroke_width=2.5)
        upper_surf, lower_surf = self._surface_halves(airfoil)

        p_label = VGroup(
            Text("p  =  static pressure", font_size=26, color=BLUE_C),
            Text("Low p above  •  High p below", font_size=22, color=GRAY_B),
        ).arrange(DOWN, buff=0.18)
        p_label.move_to(DOWN * abs(LABEL_Y) + DOWN * 0.25)

        self.play(Create(p_box), run_time=0.5)
        self.play(Create(upper_surf, run_time=0.8),
                  Create(lower_surf, run_time=0.8))
        self.play(FadeIn(p_label), run_time=0.6)
        self.wait(6.3)   # hold to ~28s

        self.play(FadeOut(p_box, upper_surf, lower_surf, p_label), run_time=0.5)

        # ── E: Term ½ρv² — dynamic pressure (28–40s) ─────────────────────────
        half_box = SurroundingRectangle(eq[1], color=ORANGE, buff=0.1, stroke_width=2.5)

        # Three pre-computed streamlines above and below
        above_lines = VGroup()
        below_lines = VGroup()
        s = self._scale
        for y0 in [0.65, 0.90, 1.15]:
            pts = self.flow.streamline(-4.5 / s, y0 / s, n_steps=300, dt=0.025)
            if len(pts) < 10:
                continue
            arr = np.array([[x * s, y * s + AIRFOIL_Y, 0] for x, y in pts
                            if -2.4 <= x * s <= 2.4])
            if len(arr) < 4:
                continue
            line = VMobject()
            line.set_points_smoothly(arr)
            line.set_stroke(FAST_COLOR, width=2.2, opacity=0.85)
            above_lines.add(line)

        for y0 in [-0.65, -0.90, -1.15]:
            pts = self.flow.streamline(-4.5 / s, y0 / s, n_steps=300, dt=0.025)
            if len(pts) < 10:
                continue
            arr = np.array([[x * s, y * s + AIRFOIL_Y, 0] for x, y in pts
                            if -2.4 <= x * s <= 2.4])
            if len(arr) < 4:
                continue
            line = VMobject()
            line.set_points_smoothly(arr)
            line.set_stroke(SLOW_COLOR, width=2.2, opacity=0.85)
            below_lines.add(line)

        v_label = VGroup(
            Text("½ρv²  =  dynamic pressure", font_size=25, color=ORANGE),
            Text("v↑ above  →  ½ρv² larger", font_size=22, color=GRAY_B),
        ).arrange(DOWN, buff=0.18)
        v_label.move_to(DOWN * abs(LABEL_Y) + DOWN * 0.25)

        self.play(Create(half_box), run_time=0.5)
        self.play(Create(above_lines, run_time=1.2),
                  Create(below_lines, run_time=1.2))
        self.play(FadeIn(v_label), run_time=0.6)
        self.wait(7.7)   # hold to ~40s

        self.play(FadeOut(half_box, above_lines, below_lines, v_label),
                  run_time=0.5)

        # ── F: = const — trade-off balance (40–50s) ───────────────────────────
        const_box = SurroundingRectangle(eq[3], color=YELLOW_C, buff=0.1,
                                          stroke_width=2.5)

        bar_w = 0.55
        bar_gap = 1.0
        bar_x_l = -bar_gap / 2
        bar_x_r =  bar_gap / 2
        bar_y   = LABEL_Y + 1.0   # just above label zone

        # Left stack: low v → large p, small ½ρv²
        p_bar_l = Rectangle(width=bar_w, height=1.4, color=BLUE_C,
                             fill_color=BLUE_C, fill_opacity=0.7, stroke_width=0)
        v_bar_l = Rectangle(width=bar_w, height=0.55, color=ORANGE,
                             fill_color=ORANGE, fill_opacity=0.7, stroke_width=0)
        p_bar_l.move_to([bar_x_l, bar_y + 0.7,  0])
        v_bar_l.move_to([bar_x_l, bar_y + 0.55 + 1.4 - 0.275, 0])
        v_bar_l.next_to(p_bar_l, UP, buff=0)
        lbl_l = Text("low v", font_size=18, color=GRAY_B)
        lbl_l.next_to(p_bar_l, DOWN, buff=0.12)

        # Right stack: high v (above wing) → small p, large ½ρv²
        p_bar_r = Rectangle(width=bar_w, height=0.55, color=BLUE_C,
                             fill_color=BLUE_C, fill_opacity=0.7, stroke_width=0)
        v_bar_r = Rectangle(width=bar_w, height=1.4, color=ORANGE,
                             fill_color=ORANGE, fill_opacity=0.7, stroke_width=0)
        p_bar_r.move_to([bar_x_r, bar_y + 0.275, 0])
        v_bar_r.next_to(p_bar_r, UP, buff=0)
        lbl_r = Text("high v", font_size=18, color=GRAY_B)
        lbl_r.next_to(p_bar_r, DOWN, buff=0.12)

        # Legend dots
        p_dot = Dot(color=BLUE_C, radius=0.09)
        v_dot = Dot(color=ORANGE,  radius=0.09)
        p_leg = Text(" p",    font_size=18, color=BLUE_C)
        v_leg = Text(" ½ρv²", font_size=18, color=ORANGE)
        legend = VGroup(
            VGroup(p_dot, p_leg).arrange(RIGHT, buff=0.06),
            VGroup(v_dot, v_leg).arrange(RIGHT, buff=0.06),
        ).arrange(RIGHT, buff=0.5)
        legend.move_to([0, bar_y - 0.85, 0])

        const_lbl = Text("When v↑, p must ↓", font_size=26, color=YELLOW_C)
        const_lbl.move_to(DOWN * abs(LABEL_Y))

        bars = VGroup(p_bar_l, v_bar_l, p_bar_r, v_bar_r,
                      lbl_l, lbl_r, legend)

        self.play(Create(const_box), run_time=0.4)
        self.play(FadeIn(bars, lag_ratio=0.1, run_time=1.2))
        self.play(FadeIn(const_lbl), run_time=0.5)
        self.wait(6.9)   # hold to ~50s

        self.play(FadeOut(const_box, bars, const_lbl), run_time=0.5)

        # ── G: Net pressure → LIFT (50–58s) ───────────────────────────────────
        self.play(FadeOut(eq), run_time=0.4)

        # Re-draw pressure surfaces (briefly)
        upper_s2, lower_s2 = self._surface_halves(airfoil)
        self.play(Create(upper_s2, run_time=0.6),
                  Create(lower_s2, run_time=0.6))

        lift_arrow = Arrow(
            airfoil.get_center() + DOWN * 0.1,
            airfoil.get_center() + UP * 2.0,
            color=LIFT_COLOR, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.12,
        )
        lift_lbl = Text("LIFT", font_size=44, color=LIFT_COLOR, weight=BOLD)
        lift_lbl.next_to(lift_arrow, RIGHT, buff=0.2)

        dp_eq = MathTex(r"\Delta p \;\longrightarrow\; \text{Lift!}",
                        font_size=38, color=LIFT_COLOR)
        dp_eq.move_to(UP * EQ_Y)

        self.play(GrowArrow(lift_arrow), FadeIn(lift_lbl), run_time=1.0)
        self.play(Write(dp_eq), run_time=1.2)
        self.wait(4.8)   # hold to ~58s

        # ── H: Tagline (58–60s) ───────────────────────────────────────────────
        stream.end_animation()
        # Remove StreamLines before any FadeOut (it holds thread locks)
        self.remove(stream)

        tagline = Text("Bernoulli — in every wing.",
                       font_size=27, color=YELLOW_C, weight=BOLD)
        tagline.move_to(DOWN * abs(LABEL_Y))

        self.play(
            FadeOut(lift_arrow, lift_lbl, dp_eq, upper_s2, lower_s2,
                    airfoil),
            run_time=0.5,
        )
        self.play(FadeIn(tagline), run_time=0.6)
        self.wait(0.9)
        self.play(FadeOut(tagline), run_time=0.5)
