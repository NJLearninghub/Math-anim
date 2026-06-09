"""
Bernoulli's Equation — Full Educational Animation
Covers: equation derivation, Venturi tube, airplane lift,
        Magnus effect, artery stenosis, rooftop wind lift.
~4 minutes total.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import (BG_COLOR, FLOW_COLOR, FAST_COLOR, SLOW_COLOR,
                               AIRFOIL_FILL, AIRFOIL_STROKE, LIFT_COLOR, ANNOTATION)
from src.utils.flow_field import JoukowskiFlow


# ─── helpers ──────────────────────────────────────────────────────────────────

def section_title(text, color=YELLOW_C):
    t = Text(text, font_size=38, weight=BOLD, color=color)
    t.to_edge(UP, buff=0.35)
    line = Line(t.get_left(), t.get_right(), color=color, stroke_width=1.5)
    line.next_to(t, DOWN, buff=0.08)
    return VGroup(t, line)


def pressure_gauge(label, value, color, size=0.55):
    """Small vertical pressure bar widget."""
    backing = Rectangle(width=size, height=1.5, color=GRAY_D,
                        fill_color=GRAY_D, fill_opacity=0.4, stroke_width=1)
    fill_h = max(0.05, 1.5 * value)
    fill = Rectangle(width=size, height=fill_h, color=color,
                     fill_color=color, fill_opacity=0.85, stroke_width=0)
    fill.align_to(backing, DOWN)
    lbl = Text(label, font_size=16, color=GRAY_B)
    lbl.next_to(backing, DOWN, buff=0.1)
    return VGroup(backing, fill, lbl)


# ─── Scene ────────────────────────────────────────────────────────────────────

class BernoulliExplainedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self._s1_title()
        self._s2_equation()
        self._s3_venturi()
        self._s4_airfoil()
        self._s5_magnus()
        self._s6_stenosis()
        self._s7_rooftop()
        self._s8_summary()

    # ══════════════════════════════════════════════════════════════════════════
    # S1 — Title
    # ══════════════════════════════════════════════════════════════════════════
    def _s1_title(self):
        title = Text("Bernoulli's Equation", font_size=54, weight=BOLD)
        subtitle = Text("The Physics of Flowing Fluids", font_size=30,
                        color=BLUE_C)
        subtitle.next_to(title, DOWN, buff=0.4)
        tagline = Text("…and how it shapes the world around us",
                       font_size=22, color=GRAY_B, slant=ITALIC)
        tagline.next_to(subtitle, DOWN, buff=0.5)

        # Animated background dots simulating flow
        dots = VGroup(*[
            Dot([-7 + i * 0.65, y, 0], radius=0.035, color=FLOW_COLOR)
            .set_opacity(0.35)
            for i in range(24) for y in [-3, -1.8, -0.6, 0.6, 1.8, 3.0]
        ])

        self.play(FadeIn(dots, lag_ratio=0.01, run_time=1.0))
        self.play(Write(title, run_time=1.5))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.play(FadeIn(tagline))
        self.play(dots.animate.shift(RIGHT * 1.8), run_time=2.5,
                  rate_func=linear)
        self.wait(0.8)
        self.play(FadeOut(VGroup(dots, title, subtitle, tagline)))

    # ══════════════════════════════════════════════════════════════════════════
    # S2 — The Equation
    # ══════════════════════════════════════════════════════════════════════════
    def _s2_equation(self):
        hdr = section_title("Bernoulli's Equation")
        self.play(Write(hdr))

        # Full equation
        eq = MathTex(
            r"p", r"+", r"\tfrac{1}{2}\rho v^2", r"+", r"\rho g h",
            r"=", r"\mathrm{constant}",
            font_size=52,
        )
        eq.move_to(UP * 0.8)
        self.play(Write(eq, run_time=2.0))
        self.wait(0.4)

        # Labels per term
        term_info = [
            (0, BLUE_C,   "p",          "Static pressure\n(force per unit area)"),
            (2, ORANGE,   r"\tfrac{1}{2}\rho v^2", "Dynamic pressure\n(kinetic energy density)"),
            (4, GREEN,    r"\rho g h",  "Hydrostatic pressure\n(gravitational potential energy)"),
            (6, YELLOW_C, r"\mathrm{const}", "Total mechanical\nenergy is conserved"),
        ]
        for idx, col, _, desc in term_info:
            box = SurroundingRectangle(eq[idx], color=col, buff=0.1,
                                       stroke_width=2)
            txt = Text(desc, font_size=20, color=col)
            txt.next_to(eq, DOWN, buff=0.6)
            self.play(Create(box, run_time=0.4))
            self.play(FadeIn(txt))
            self.wait(1.8)
            self.play(FadeOut(box), FadeOut(txt), run_time=0.3)

        # Streamline picture: two cross-sections A and B
        self.wait(0.3)
        pipe_pts_top = np.array([
            [-5, 1.0, 0], [-2, 1.0, 0], [-0.8, 0.4, 0], [0.8, 0.4, 0],
            [2, 1.0, 0], [5, 1.0, 0],
        ])
        pipe_pts_bot = np.array([
            [-5, -1.0, 0], [-2, -1.0, 0], [-0.8, -0.4, 0], [0.8, -0.4, 0],
            [2, -1.0, 0], [5, -1.0, 0],
        ])
        pipe_pts_top[:, 1] -= 2.2
        pipe_pts_bot[:, 1] -= 2.2

        top_curve = VMobject().set_points_smoothly(pipe_pts_top)
        top_curve.set_stroke(BLUE_B, 2.5)
        bot_curve = VMobject().set_points_smoothly(pipe_pts_bot)
        bot_curve.set_stroke(BLUE_B, 2.5)

        lbl_a = Text("①", font_size=22, color=GRAY_B).move_to([-4, -1.1, 0])
        lbl_b = Text("②", font_size=22, color=GRAY_B).move_to([0, -1.9, 0])

        eq_pts = MathTex(
            r"p_1 + \tfrac{1}{2}\rho v_1^2 = p_2 + \tfrac{1}{2}\rho v_2^2",
            font_size=30, color=ANNOTATION,
        )
        eq_pts.move_to(DOWN * 1.2)

        self.play(Create(top_curve), Create(bot_curve),
                  FadeIn(lbl_a), FadeIn(lbl_b))
        self.play(Write(eq_pts))
        self.wait(2.5)
        self.play(FadeOut(VGroup(hdr, eq, top_curve, bot_curve,
                                  lbl_a, lbl_b, eq_pts)))

    # ══════════════════════════════════════════════════════════════════════════
    # S3 — Venturi Effect
    # ══════════════════════════════════════════════════════════════════════════
    def _s3_venturi(self):
        hdr = section_title("Application 1 — Venturi Effect")
        self.play(Write(hdr))

        # Draw Venturi tube cross-section
        def venturi_y(x, top=True):
            half_w = 1.0 - 0.62 * np.exp(-2.5 * x**2)
            return half_w if top else -half_w

        xs = np.linspace(-5.5, 5.5, 120)
        top_pts = np.column_stack([xs, [venturi_y(x, True)  for x in xs],
                                   np.zeros(len(xs))])
        bot_pts = np.column_stack([xs, [venturi_y(x, False) for x in xs],
                                   np.zeros(len(xs))])
        top_pts[:, 1] -= 0.2
        bot_pts[:, 1] -= 0.2

        top_wall = VMobject().set_points_smoothly(top_pts)
        top_wall.set_stroke(BLUE_B, 3)
        bot_wall = VMobject().set_points_smoothly(bot_pts)
        bot_wall.set_stroke(BLUE_B, 3)

        # Flow particles (streamlines)
        def venturi_speed(x):
            area = 2 * (1.0 - 0.62 * np.exp(-2.5 * x**2))
            return 1.0 / max(area, 0.05)

        # Draw 5 horizontal streamlines with varying speed via dot spacing
        stream_group = VGroup()
        for y_frac in [-0.7, -0.35, 0, 0.35, 0.7]:
            pts = []
            x = -5.4
            t = 0.0
            step_t = 0.15
            while x < 5.4:
                half = venturi_y(x, True)
                y = y_frac * half - 0.2
                pts.append([x, y, 0])
                dx = venturi_speed(x) * step_t
                x += max(dx, 0.02)
                t += step_t
            line = VMobject().set_points_smoothly(np.array(pts))
            line.set_stroke(FLOW_COLOR, 1.5, opacity=0.6)
            stream_group.add(line)

        self.play(Create(top_wall), Create(bot_wall))
        self.play(Create(stream_group, lag_ratio=0.1, run_time=1.5))

        # Pressure gauges
        gauge_hi  = pressure_gauge("p₁\n(high)", 0.85, BLUE_C)
        gauge_lo  = pressure_gauge("p₂\n(low)",  0.25, FAST_COLOR)
        gauge_hi2 = pressure_gauge("p₃\n(high)", 0.85, BLUE_C)
        gauge_hi.move_to([-4.0, 1.5, 0])
        gauge_lo.move_to([0.0,  1.5, 0])
        gauge_hi2.move_to([4.0, 1.5, 0])

        # Dashed drop lines
        drop_lines = VGroup(
            DashedLine([-4, 0.7, 0], [-4, -0.1, 0],
                       color=GRAY_C, stroke_width=1),
            DashedLine([0, 0.2, 0], [0, -0.85, 0],
                       color=GRAY_C, stroke_width=1),
            DashedLine([4, 0.7, 0], [4, -0.1, 0],
                       color=GRAY_C, stroke_width=1),
        )

        self.play(FadeIn(gauge_hi), FadeIn(gauge_lo), FadeIn(gauge_hi2),
                  Create(drop_lines))

        speed_label = VGroup(
            Text("Narrow section:", font_size=22, color=FAST_COLOR),
            MathTex(r"v\uparrow \;\Rightarrow\; p\downarrow",
                    font_size=30, color=FAST_COLOR),
        ).arrange(RIGHT, buff=0.3)
        speed_label.move_to(DOWN * 2.8)

        self.play(FadeIn(speed_label))
        self.wait(1.5)

        # Real-world callouts
        uses = Text(
            "Used in: carburetors · flow meters · perfume atomizers · aircraft pitot tubes",
            font_size=20, color=GRAY_B,
        )
        uses.to_edge(DOWN, buff=0.25)
        self.play(Write(uses))
        self.wait(2.0)

        self.play(FadeOut(VGroup(hdr, top_wall, bot_wall, stream_group,
                                  gauge_hi, gauge_lo, gauge_hi2,
                                  drop_lines, speed_label, uses)))

    # ══════════════════════════════════════════════════════════════════════════
    # S4 — Airplane Wing
    # ══════════════════════════════════════════════════════════════════════════
    def _s4_airfoil(self):
        hdr = section_title("Application 2 — Airplane Wing")
        self.play(Write(hdr))

        flow = JoukowskiFlow(alpha_deg=8)
        sc = 0.8  # scale chord to 4 units
        pts3d = flow.airfoil_manim_pts(n=200).copy()
        pts3d[:, :2] *= sc

        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.9)
        airfoil.set_stroke(AIRFOIL_STROKE, width=2.5)
        airfoil.shift(DOWN * 0.3)

        self.play(Create(airfoil, run_time=1.2))

        def vel_field(pos):
            uv = flow.velocity(pos[0] / sc, (pos[1] + 0.3) / sc)
            if uv is None:
                return np.array([0., 0., 0.])
            u, v = uv
            mag = np.hypot(u, v)
            if mag > 3.5:
                u, v = u / mag * 3.5, v / mag * 3.5
            return np.array([u, v, 0.])

        stream = StreamLines(
            vel_field,
            x_range=[-7, 7, 0.38],
            y_range=[-3.5, 3.5, 0.38],
            dt=0.06,
            max_anchors_per_line=55,
            stroke_width=1.6,
            stroke_color=FLOW_COLOR,
            opacity=0.7,
        )
        self.add(stream)
        self.add(airfoil)
        stream.start_animation(warm_up=True, flow_speed=1.6, time_width=0.25)

        # Labels
        fast_lbl = Text("v↑  low pressure", font_size=22, color=FAST_COLOR)
        slow_lbl = Text("v↓  high pressure", font_size=22, color=SLOW_COLOR)
        fast_lbl.move_to(UP * 1.7 + RIGHT * 1.5)
        slow_lbl.move_to(DOWN * 1.5 + RIGHT * 1.5)
        self.play(FadeIn(fast_lbl), FadeIn(slow_lbl))
        self.wait(2.5)

        # Pressure surface colours
        raw = flow.airfoil_manim_pts(n=160).copy()
        raw[:, :2] *= sc
        raw[:, 1] += -0.3
        le_idx = int(np.argmin(raw[:, 0]))
        upper_pts = raw[:le_idx + 1]
        lower_pts = np.vstack([raw[le_idx:], raw[:1]])
        upper_surf = VMobject().set_points_smoothly(upper_pts)
        upper_surf.set_stroke(FAST_COLOR, 6, opacity=0.85).set_fill(opacity=0)
        lower_surf = VMobject().set_points_smoothly(lower_pts)
        lower_surf.set_stroke(SLOW_COLOR, 6, opacity=0.85).set_fill(opacity=0)
        self.play(Create(upper_surf, run_time=0.8),
                  Create(lower_surf, run_time=0.8))

        # Lift arrow
        lift_arr = Arrow(
            airfoil.get_center() + DOWN * 0.1,
            airfoil.get_center() + UP * 2.0,
            color=LIFT_COLOR, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.12,
        )
        lift_lbl = Text("LIFT", font_size=30, color=LIFT_COLOR, weight=BOLD)
        lift_lbl.next_to(lift_arr, RIGHT, buff=0.15)
        self.play(GrowArrow(lift_arr), FadeIn(lift_lbl))
        self.wait(3.0)

        stream.end_animation()
        self.remove(stream)
        self.play(FadeOut(VGroup(hdr, airfoil, upper_surf, lower_surf,
                                  lift_arr, lift_lbl, fast_lbl, slow_lbl)))

    # ══════════════════════════════════════════════════════════════════════════
    # S5 — Magnus Effect (spinning ball)
    # ══════════════════════════════════════════════════════════════════════════
    def _s5_magnus(self):
        hdr = section_title("Application 3 — Magnus Effect")
        self.play(Write(hdr))

        subtitle = Text("Why curveballs curve", font_size=26, color=GRAY_B,
                        slant=ITALIC)
        subtitle.next_to(hdr, DOWN, buff=0.55)
        self.play(FadeIn(subtitle))

        # Ball
        R = 1.0
        ball = Circle(radius=R, color=WHITE, stroke_width=2.5)
        ball.set_fill(GRAY_E, opacity=0.7)
        ball.move_to(DOWN * 0.4)

        # Spin arrow (clockwise)
        spin_arc = Arc(radius=0.55, start_angle=PI/4, angle=-3*PI/2,
                       color=YELLOW_C, stroke_width=2.5)
        spin_tip = Arrow(
            spin_arc.get_end(), spin_arc.get_end() + DOWN * 0.3 + LEFT * 0.1,
            buff=0, color=YELLOW_C, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.6,
        )
        spin_arc.move_to(ball.get_center())
        spin_tip.move_to(ball.get_center() + DOWN * 0.5 + LEFT * 0.15)
        spin_lbl = Text("spin", font_size=18, color=YELLOW_C)
        spin_lbl.move_to(ball.get_center())

        self.play(Create(ball), Create(spin_arc), FadeIn(spin_lbl))
        self.wait(0.3)

        # Streamlines: above slower (top curve), below faster (bottom)
        # Above: wider spacing (low speed) → HIGH pressure
        # Below: compressed (high speed) → LOW pressure
        # (Clockwise spin: top drags air backward → slower, bottom drags forward → faster)
        center = ball.get_center()
        cx, cy = center[0], center[1]

        above_lines = VGroup()
        for y_off in [1.25, 1.60, 2.00, 2.50]:
            pts = []
            for t in np.linspace(-6, 6, 120):
                r = np.sqrt(t**2 + (y_off)**2) + 0.01
                # Simple deflection: streamlines bow upward over ball
                y_defl = y_off + R**2 / r * 0.5  # bow upward (slower side)
                pts.append([t + cx, y_defl + cy, 0])
            line = VMobject().set_points_smoothly(np.array(pts))
            line.set_stroke(SLOW_COLOR, 2, opacity=0.75)
            above_lines.add(line)

        below_lines = VGroup()
        for y_off in [-1.25, -1.55, -1.90, -2.35]:
            pts = []
            for t in np.linspace(-6, 6, 120):
                r = np.sqrt(t**2 + y_off**2) + 0.01
                y_defl = y_off - R**2 / r * 0.8  # bow downward (faster side)
                pts.append([t + cx, y_defl + cy, 0])
            line = VMobject().set_points_smoothly(np.array(pts))
            line.set_stroke(FAST_COLOR, 2, opacity=0.75)
            below_lines.add(line)

        # Incoming flow arrow
        flow_arr = Arrow([-6.5, cy, 0], [-R - 0.15 + cx, cy, 0],
                         color=GRAY_B, buff=0, stroke_width=3)
        flow_lbl = Text("v∞", font_size=20, color=GRAY_B)
        flow_lbl.next_to(flow_arr, UP, buff=0.1)

        self.play(Create(above_lines, run_time=1.2),
                  Create(below_lines, run_time=1.2),
                  GrowArrow(flow_arr), FadeIn(flow_lbl))
        self.wait(0.5)

        # Pressure labels
        hi_p = Text("high p", font_size=20, color=SLOW_COLOR)
        lo_p = Text("low p",  font_size=20, color=FAST_COLOR)
        hi_p.move_to([cx, cy + 1.0, 0])
        lo_p.move_to([cx, cy - 1.0, 0])
        self.play(FadeIn(hi_p), FadeIn(lo_p))

        # Net force (downward deflection)
        force_arr = Arrow(
            [cx, cy, 0], [cx, cy - 1.8, 0],
            color=LIFT_COLOR, buff=0, stroke_width=5,
        )
        force_lbl = Text("Net force\n(curve down)", font_size=20,
                         color=LIFT_COLOR)
        force_lbl.next_to(force_arr, RIGHT, buff=0.15)
        self.play(GrowArrow(force_arr), FadeIn(force_lbl))
        self.wait(1.5)

        examples = Text(
            "Used in: soccer free-kicks · cricket swing · tennis topspin · golf",
            font_size=20, color=GRAY_B,
        )
        examples.to_edge(DOWN, buff=0.3)
        self.play(Write(examples))
        self.wait(2.0)

        self.play(FadeOut(VGroup(hdr, subtitle, ball, spin_arc, spin_lbl,
                                  above_lines, below_lines, flow_arr, flow_lbl,
                                  hi_p, lo_p, force_arr, force_lbl, examples)))

    # ══════════════════════════════════════════════════════════════════════════
    # S6 — Arterial Stenosis
    # ══════════════════════════════════════════════════════════════════════════
    def _s6_stenosis(self):
        hdr = section_title("Application 4 — Blood Flow & Stenosis",
                            color=RED_C)
        self.play(Write(hdr))

        # Draw artery with narrowing
        def artery_r(x):
            return 0.85 - 0.62 * np.exp(-3.0 * (x - 0.5)**2)

        xs = np.linspace(-5.5, 5.5, 140)
        top_pts = np.column_stack([xs, [artery_r(x)  for x in xs], np.zeros_like(xs)])
        bot_pts = np.column_stack([xs, [-artery_r(x) for x in xs], np.zeros_like(xs)])
        top_pts[:, 1] -= 0.3
        bot_pts[:, 1] -= 0.3

        top_wall = VMobject().set_points_smoothly(top_pts)
        top_wall.set_stroke(RED_C, 3)
        bot_wall = VMobject().set_points_smoothly(bot_pts)
        bot_wall.set_stroke(RED_C, 3)

        # Red fill between walls
        fill_pts = list(top_pts) + list(reversed(list(bot_pts)))
        fill_shape = Polygon(*[p for p in fill_pts],
                             color=RED_C, fill_color=RED_C,
                             fill_opacity=0.12, stroke_width=0)

        self.play(Create(top_wall), Create(bot_wall), FadeIn(fill_shape))

        # Plaque buildup at stenosis
        plaque = Ellipse(width=1.2, height=0.5, color=ORANGE,
                         fill_color=ORANGE, fill_opacity=0.8, stroke_width=0)
        plaque.move_to([0.5, -0.3 + artery_r(0.5) - 0.25, 0])
        plaque2 = Ellipse(width=0.9, height=0.35, color=ORANGE,
                          fill_color=ORANGE, fill_opacity=0.8, stroke_width=0)
        plaque2.move_to([0.5, -0.3 - artery_r(0.5) + 0.18, 0])
        plaque_lbl = Text("plaque", font_size=18, color=ORANGE)
        plaque_lbl.next_to(plaque, RIGHT, buff=0.15)

        self.play(FadeIn(plaque), FadeIn(plaque2), FadeIn(plaque_lbl))

        # Flow lines
        def blood_speed(x):
            r = artery_r(x)
            return 0.72 / max(r**2, 0.03)

        stream_lines = VGroup()
        for y_frac in [-0.55, -0.25, 0, 0.25, 0.55]:
            pts = []
            x = -5.3
            while x < 5.3:
                r = artery_r(x)
                y = y_frac * r - 0.3
                pts.append([x, y, 0])
                dx = blood_speed(x) * 0.12
                x += max(dx, 0.02)
            line = VMobject().set_points_smoothly(np.array(pts))
            line.set_stroke(RED_B, 1.8, opacity=0.65)
            stream_lines.add(line)

        self.play(Create(stream_lines, lag_ratio=0.15, run_time=1.5))

        # Labels
        fast_here = Text("v↑  p↓", font_size=22, color=FAST_COLOR)
        fast_here.move_to([0.5, 1.15, 0])
        collapse_lbl = Text("Risk: vessel may\ncollapse inward!",
                            font_size=20, color=RED_C)
        collapse_lbl.move_to([3.5, 0.9, 0])
        self.play(FadeIn(fast_here), FadeIn(collapse_lbl))

        # Bernoulli equation linking the two zones
        eq_blood = MathTex(
            r"p_{\text{normal}} + \tfrac{1}{2}\rho v_1^2 = "
            r"p_{\text{stenosis}} + \tfrac{1}{2}\rho v_2^2",
            font_size=28, color=ANNOTATION,
        )
        eq_blood.move_to(DOWN * 2.6)
        self.play(Write(eq_blood))
        self.wait(2.5)

        uses = Text(
            "Doctors use Doppler ultrasound to measure v → calculate p drop",
            font_size=19, color=GRAY_B,
        )
        uses.to_edge(DOWN, buff=0.2)
        self.play(Write(uses))
        self.wait(2.0)

        self.play(FadeOut(VGroup(hdr, top_wall, bot_wall, fill_shape,
                                  plaque, plaque2, plaque_lbl, stream_lines,
                                  fast_here, collapse_lbl, eq_blood, uses)))

    # ══════════════════════════════════════════════════════════════════════════
    # S7 — Rooftop Wind Lift
    # ══════════════════════════════════════════════════════════════════════════
    def _s7_rooftop(self):
        hdr = section_title("Application 5 — Rooftop in a Storm")
        self.play(Write(hdr))

        # Simple house cross-section
        ground = Line([-6.5, -2.0, 0], [6.5, -2.0, 0],
                      color=GRAY_C, stroke_width=2)
        walls = Polygon(
            [-2.0, -2.0, 0], [-2.0, -0.2, 0],
            [2.0, -0.2, 0],  [2.0, -2.0, 0],
            color=GRAY_C, fill_color=GRAY_E, fill_opacity=0.4, stroke_width=2,
        )
        roof = Polygon(
            [-2.2, -0.2, 0], [0, 1.3, 0], [2.2, -0.2, 0],
            color=ORANGE, fill_color=ORANGE, fill_opacity=0.55, stroke_width=2.5,
        )
        house = VGroup(ground, walls, roof)
        self.play(Create(house, run_time=1.2))

        # Wind streamlines over roof (converge over peak → faster)
        wind_lines = VGroup()
        for y_off in [1.7, 2.2, 2.7, 3.2]:
            pts = []
            for x in np.linspace(-6.5, 6.5, 120):
                if -2.5 < x < 2.5:
                    # Roof profile influence
                    roof_h = max(0, 1.3 - (abs(x) / 2.2) * 1.3 - 0.2)
                    compress = roof_h * 0.45 / (y_off - 0.5)
                    y = y_off + compress
                else:
                    y = y_off
                pts.append([x, y - 1.0, 0])
            line = VMobject().set_points_smoothly(np.array(pts))
            line.set_stroke(FLOW_COLOR, 2, opacity=0.7)
            wind_lines.add(line)

        wind_arr = Arrow([-6.5, 0.5, 0], [-3.0, 0.5, 0],
                         color=GRAY_B, buff=0, stroke_width=3)
        wind_lbl = Text("Wind →", font_size=20, color=GRAY_B)
        wind_lbl.next_to(wind_arr, UP, buff=0.1)

        self.play(GrowArrow(wind_arr), FadeIn(wind_lbl))
        self.play(Create(wind_lines, lag_ratio=0.15, run_time=1.5))

        # Labels
        fast_over  = Text("v↑ over roof → p↓", font_size=22, color=FAST_COLOR)
        inside_p   = Text("p inside = atmospheric", font_size=20, color=SLOW_COLOR)
        fast_over.move_to([3.0, 2.0, 0])
        inside_p.move_to([3.5, -0.8, 0])
        self.play(FadeIn(fast_over), FadeIn(inside_p))

        # Lift arrow on roof
        lift_roof = Arrow(
            [0, 1.3, 0], [0, 2.8, 0],
            color=RED_C, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.15,
        )
        lift_roof_lbl = Text("Net upward force!", font_size=22, color=RED_C)
        lift_roof_lbl.next_to(lift_roof, RIGHT, buff=0.1)
        self.play(GrowArrow(lift_roof), FadeIn(lift_roof_lbl))
        self.wait(2.0)

        uses = Text(
            "Hurricane roofs fail from below-pressure suction, not just wind pushing",
            font_size=19, color=GRAY_B,
        )
        uses.to_edge(DOWN, buff=0.25)
        self.play(Write(uses))
        self.wait(2.5)

        self.play(FadeOut(VGroup(hdr, house, wind_lines, wind_arr, wind_lbl,
                                  fast_over, inside_p, lift_roof,
                                  lift_roof_lbl, uses)))

    # ══════════════════════════════════════════════════════════════════════════
    # S8 — Summary
    # ══════════════════════════════════════════════════════════════════════════
    def _s8_summary(self):
        hdr = section_title("Bernoulli's Equation — Everywhere")
        self.play(Write(hdr))

        eq = MathTex(
            r"p + \tfrac{1}{2}\rho v^2 + \rho g h = \mathrm{const}",
            font_size=40,
        )
        eq.move_to(UP * 2.2)
        self.play(Write(eq, run_time=1.5))

        apps = [
            ("✈  Airplane wings",    "Lift from pressure difference",  BLUE_C),
            ("⚽  Spinning balls",    "Magnus effect curves the path",   ORANGE),
            ("🔧  Venturi / meters",  "Speed → pressure in pipes",       GREEN),
            ("🩺  Blood flow",        "Stenosis raises fluid velocity",  RED_C),
            ("🏠  Rooftops",          "Wind suction lifts the roof",     YELLOW_C),
        ]

        card_group = VGroup()
        for i, (title, desc, col) in enumerate(apps):
            box = RoundedRectangle(width=5.0, height=0.85, corner_radius=0.12,
                                   color=col, fill_color=col,
                                   fill_opacity=0.12, stroke_width=1.5)
            t1 = Text(title, font_size=22, color=col, weight=BOLD)
            t2 = Text(desc,  font_size=18, color=GRAY_B)
            t1.move_to(box.get_left() + RIGHT * 1.6)
            t2.move_to(box.get_right() + LEFT * 1.5)
            card_group.add(VGroup(box, t1, t2))

        card_group.arrange(DOWN, buff=0.22)
        card_group.move_to(DOWN * 0.15)

        for card in card_group:
            self.play(FadeIn(card, shift=RIGHT * 0.3, run_time=0.45))

        self.wait(1.5)

        tagline = Text(
            "Faster flow → lower pressure. Simple, elegant, universal.",
            font_size=24, color=YELLOW_C, weight=BOLD,
        )
        tagline.to_edge(DOWN, buff=0.35)
        self.play(Write(tagline))
        self.wait(3.0)
        self.play(FadeOut(VGroup(hdr, eq, card_group, tagline)))
