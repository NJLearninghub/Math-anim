"""
Projectile Motion — Feynman Technique (First Principles)
Pattern per section:
  1. OBSERVE    → show the phenomenon, no equations yet
  2. SIMPLIFY   → strip to the essential idea in plain language
  3. MODEL      → identify which physical law applies
  4. QUANTIFY   → let the equation emerge from reasoning
  5. CHECK      → does it make sense at extreme cases?

Layout zones (strict — nothing may cross zone boundaries simultaneously):
  TITLE   y ≈ +3.35   (to_edge UP)
  RULE    y ≈ +2.95   (thin line under title)
  EQ      y ≈ +2.20   (equation or key statement)
  AXES    y ∈ [-2.0, +1.8]   (all animations live here)
  NOTE    y ≈ -3.10   (one-liner principle)

Narration is provided by an offline TTS service (src/utils/tts.py) since
gTTS is blocked from cloud IPs. Overlap safeguards live in
src/utils/layout.py and are reused here for the S8 angle labels.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from src.utils.tts import OfflineTTSService
from src.utils.layout import warn_zone_violation

# ── palette ────────────────────────────────────────────────────────────────
BG      = "#0d1117"
H_COL   = BLUE_C        # horizontal / x-direction
V_COL   = GREEN_C       # vertical / y-direction
T_COL   = YELLOW_C      # full trajectory
G_COL   = RED_C         # gravity
BALL_C  = WHITE

# ── simulation constants (chosen so trajectory looks good on screen) ───────
G_SIM   = 2.0           # "scene gravity"  [scene-units / s²]
V0      = 5.0           # initial speed    [scene-units / s]
DEG45   = np.pi / 4

def T_flight(theta=DEG45, v0=V0, g=G_SIM):
    return 2 * v0 * np.sin(theta) / g

def traj_xy(t, theta=DEG45, v0=V0, g=G_SIM):
    x = v0 * np.cos(theta) * t
    y = v0 * np.sin(theta) * t - 0.5 * g * t**2
    return x, y

def traj_range(theta=DEG45, v0=V0, g=G_SIM):
    return v0**2 * np.sin(2 * theta) / g

def traj_height(theta=DEG45, v0=V0, g=G_SIM):
    return v0**2 * np.sin(theta)**2 / (2 * g)

# ── shared axes factory ─────────────────────────────────────────────────────
def make_traj_axes(x_max=13, y_max=4.0):
    ax = Axes(
        x_range=[0, x_max, 2],
        y_range=[0, y_max, 1],
        x_length=11.0,
        y_length=3.8,
        axis_config={
            "color": GRAY_C, "stroke_width": 1.5,
            "include_tip": False,
        },
        tips=False,
    )
    ax.move_to([0, -0.10, 0])
    return ax

# ── section header (title + rule, always at top) ───────────────────────────
def make_header(txt, color=YELLOW_C, font_size=34):
    t = Text(txt, font_size=font_size, weight=BOLD, color=color)
    t.to_edge(UP, buff=0.32)
    rule = Line(
        t.get_left() + LEFT * 0.1,
        t.get_right() + RIGHT * 0.1,
        color=color, stroke_width=1.5,
    ).next_to(t, DOWN, buff=0.08)
    return VGroup(t, rule)

# ── bottom note (always at bottom edge) ───────────────────────────────────
def make_note(txt, color=GRAY_B, font_size=21):
    t = Text(txt, font_size=font_size, color=color, slant=ITALIC)
    t.to_edge(DOWN, buff=0.28)
    return t

# ── equation box (always in EQ zone, just below header rule) ───────────────
def make_eq_box(tex_str, font_size=38, color=WHITE):
    eq = MathTex(tex_str, font_size=font_size, color=color)
    eq.move_to([0, 2.20, 0])
    return eq


# ══════════════════════════════════════════════════════════════════════════════
class ProjectileMotionScene(VoiceoverScene):

    def construct(self):
        self.camera.background_color = BG
        self.set_speech_service(OfflineTTSService())
        self._s1_hook()
        self._s2_feynman_start()
        self._s3_horizontal()
        self._s4_vertical()
        self._s5_independence()
        self._s6_combine()
        self._s7_equations()
        self._s8_angles()
        self._s9_real_world()
        self._s10_summary()

    # ══════ S1: Hook ══════════════════════════════════════════════════════════
    def _s1_hook(self):
        # Dramatic opening: ball following parabola, no equations yet
        ax = make_traj_axes()

        curve = ax.plot_parametric_curve(
            lambda t: [traj_xy(t)[0], traj_xy(t)[1]],
            t_range=[0, T_flight()],
            color=T_COL, stroke_width=3,
        )
        ball = Dot(color=BALL_C, radius=0.14).move_to(ax.c2p(0, 0))
        shadow_trail = TracedPath(ball.get_center,
                                  stroke_color=T_COL,
                                  stroke_width=2,
                                  stroke_opacity=0.55)

        title = Text("Projectile Motion", font_size=48, weight=BOLD, color=T_COL)
        title.to_edge(UP, buff=0.32)

        question = Text("Why does it follow THIS curve?",
                        font_size=26, color=GRAY_B, slant=ITALIC)
        question.to_edge(DOWN, buff=0.32)

        with self.voiceover(
            text="Watch this ball rise, curve, and fall back down in a "
                 "perfect arc. Why does it follow exactly this shape?"
        ) as tracker:
            self.play(Write(title, run_time=1.2))
            self.add(shadow_trail)
            self.play(Create(ax, run_time=0.8))
            self.play(
                MoveAlongPath(ball, curve,
                              run_time=max(tracker.duration - 2.0, 1.5),
                              rate_func=linear),
            )
            self.play(FadeIn(question))

        self.wait(1.0)
        self.play(FadeOut(VGroup(title, ax, ball, shadow_trail, question,
                                  curve)))

    # ══════ S2: Feynman Start ═════════════════════════════════════════════════
    def _s2_feynman_start(self):
        hdr = make_header("The Feynman Way: Teach It From Scratch")
        self.play(Write(hdr))

        lines = VGroup(
            Text("Step 1 — Observe the phenomenon", font_size=26, color=BLUE_C),
            Text("Step 2 — Strip it to the simplest possible idea", font_size=26, color=GREEN_C),
            Text("Step 3 — Find which physical law explains it", font_size=26, color=ORANGE),
            Text("Step 4 — Write only the math that follows", font_size=26, color=YELLOW_C),
            Text("Step 5 — Check extremes, then apply everywhere", font_size=26, color=RED_C),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        lines.move_to([0, -0.2, 0])

        with self.voiceover(
            text="Let's use Feynman's technique: to truly understand "
                 "something, build it up from scratch in five steps — "
                 "observe, simplify, find the law, derive the math, "
                 "then check the extremes."
        ) as tracker:
            for line in lines:
                self.play(FadeIn(line, shift=RIGHT * 0.25,
                                  run_time=tracker.duration / len(lines)))

        note = make_note(
            '"If you cannot explain it simply, you do not understand it." — Feynman'
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, lines, note)))

    # ══════ S3: Horizontal Motion ════════════════════════════════════════════
    def _s3_horizontal(self):
        hdr = make_header("Part I — Horizontal: No Force, No Change", color=H_COL)
        self.play(Write(hdr))

        # OBSERVE: plain-language idea (EQ zone)
        idea = Text("Nothing pushes the ball sideways  →  it keeps the same speed",
                    font_size=24, color=H_COL)
        idea.move_to([0, 2.20, 0])

        # MODEL: axes showing x vs t (straight line)
        ax = Axes(
            x_range=[0, 4.0, 1],
            y_range=[0, 12, 3],
            x_length=5.5,
            y_length=3.6,
            axis_config={"color": GRAY_C, "stroke_width": 1.5, "include_tip": False},
            tips=False,
        ).move_to([-2.8, -0.2, 0])

        x_label = ax.get_x_axis_label(MathTex("t\\,(s)", font_size=24),
                                       edge=RIGHT, direction=RIGHT, buff=0.15)
        y_label = ax.get_y_axis_label(MathTex("x\\,(m)", font_size=24),
                                       edge=UP, direction=UP, buff=0.15)

        # Animate straight line x = v0_x * t
        v0x = V0 * np.cos(DEG45)
        line_x = ax.plot(lambda t: v0x * t, x_range=[0, 3.8],
                         color=H_COL, stroke_width=2.5)

        # Dot moving at constant speed (right panel animation)
        anim_line = NumberLine(x_range=[0, 12, 3], length=4.5,
                               color=GRAY_C, stroke_width=1.5)
        anim_line.move_to([3.0, -0.2, 0])
        anim_dot = Dot(color=H_COL, radius=0.14).move_to(anim_line.n2p(0))

        # Time dots at equal intervals
        time_dots = VGroup(*[
            Dot(anim_line.n2p(v0x * t), color=H_COL, radius=0.08).set_opacity(0.5)
            for t in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        ])
        lbl_equal = Text("equal spacing\n= constant speed",
                         font_size=18, color=H_COL)
        lbl_equal.next_to(anim_line, DOWN, buff=0.5)

        # QUANTIFY: equation emerges
        eq_x = make_eq_box(r"x(t) \;=\; v_0 \cos\theta \cdot t", color=H_COL)

        with self.voiceover(
            text="Nothing pushes the ball sideways. By Newton's first "
                 "law, that means its horizontal speed never changes — "
                 "equal time gives equal distance. This gives us "
                 "x equals v-zero cosine theta, times t."
        ) as tracker:
            self.play(FadeIn(idea))
            self.play(Create(ax), FadeIn(x_label), FadeIn(y_label))
            self.play(Create(line_x, run_time=1.8))
            self.play(Create(anim_line))
            self.play(anim_dot.animate.move_to(anim_line.n2p(v0x * 3.0)),
                      run_time=2.0, rate_func=linear)
            self.play(FadeIn(time_dots), FadeIn(lbl_equal))
            self.play(FadeOut(idea))
            self.play(Write(eq_x, run_time=1.2))

        note = make_note(
            "Newton's 1st Law: no sideways force → sideways velocity is constant"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, ax, x_label, y_label, line_x,
                                  anim_line, anim_dot, time_dots, lbl_equal,
                                  eq_x, note)))

    # ══════ S4: Vertical / Gravity ════════════════════════════════════════════
    def _s4_vertical(self):
        hdr = make_header("Part II — Vertical: Gravity Pulls Constantly",
                          color=V_COL)
        self.play(Write(hdr))

        idea = Text("Gravity adds 9.8 m/s of downward speed  every  second",
                    font_size=24, color=V_COL)
        idea.move_to([0, 2.20, 0])

        # Left: ball positions at equal time steps — gaps grow!
        column_x = -4.5
        t_steps = [0, 0.4, 0.8, 1.2, 1.6, 2.0]
        gap_dots = VGroup()
        gap_arrows = VGroup()
        v0y = V0 * np.sin(DEG45)
        base_y = 1.5
        prev_y = None
        for t in t_steps:
            y_phys = v0y * t - 0.5 * G_SIM * t**2
            y_scene = base_y - y_phys * 0.7          # scale & invert for drop
            dot = Dot([column_x, y_scene, 0], color=V_COL, radius=0.10)
            gap_dots.add(dot)
            if prev_y is not None:
                arr = Arrow(
                    [column_x + 0.25, prev_y, 0],
                    [column_x + 0.25, y_scene, 0],
                    color=G_COL, buff=0,
                    stroke_width=2.0,
                    max_tip_length_to_length_ratio=0.35,
                )
                gap_arrows.add(arr)
            prev_y = y_scene

        gaps_lbl = Text("gaps increase\n= accelerating downward",
                        font_size=17, color=G_COL)
        gaps_lbl.move_to([column_x + 1.55, 0.0, 0])

        # Right: velocity arrow growing downward
        ax_v = Axes(
            x_range=[0, 2.2, 0.5],
            y_range=[-5, 0, 1],
            x_length=4.2,
            y_length=3.6,
            axis_config={"color": GRAY_C, "stroke_width": 1.5, "include_tip": False},
            tips=False,
        ).move_to([2.8, -0.3, 0])
        x_lbl_v = ax_v.get_x_axis_label(MathTex("t", font_size=22),
                                         edge=RIGHT, direction=RIGHT, buff=0.12)
        y_lbl_v = ax_v.get_y_axis_label(MathTex("v_y", font_size=22),
                                         edge=UP, direction=UP, buff=0.12)
        line_vy = ax_v.plot(lambda t: -G_SIM * t, x_range=[0, 2.0],
                            color=V_COL, stroke_width=2.5)

        slope_lbl = Text("slope = −g", font_size=18, color=G_COL)
        slope_lbl.move_to(ax_v.c2p(0.8, -3.5) + RIGHT * 0.8)

        # Equation emerges
        eq_y = make_eq_box(
            r"y(t) \;=\; v_0\sin\theta\cdot t \;-\; \tfrac{1}{2}g t^2",
            color=V_COL,
        )

        with self.voiceover(
            text="Now the vertical motion. Gravity pulls down constantly, "
                 "adding the same extra speed every second — that's "
                 "Newton's second law: force equals mass times "
                 "acceleration, and the only force here is gravity. "
                 "This gives us y equals v-zero sine theta times t, "
                 "minus one half g t squared."
        ) as tracker:
            self.play(FadeIn(idea))
            self.play(FadeIn(gap_dots, lag_ratio=0.3, run_time=1.5))
            self.play(Create(gap_arrows, lag_ratio=0.4, run_time=1.2))
            self.play(FadeIn(gaps_lbl))
            self.play(Create(ax_v), FadeIn(x_lbl_v), FadeIn(y_lbl_v))
            self.play(Create(line_vy, run_time=1.5))
            self.play(FadeIn(slope_lbl))
            self.play(FadeOut(idea))
            self.play(Write(eq_y, run_time=1.5))

        note = make_note(
            "Newton's 2nd Law: F = ma, only force is gravity → a = −g downward"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, idea, gap_dots, gap_arrows, gaps_lbl,
                                  ax_v, x_lbl_v, y_lbl_v, line_vy, slope_lbl,
                                  eq_y, note)))

    # ══════ S5: Independence ══════════════════════════════════════════════════
    def _s5_independence(self):
        hdr = make_header("The Key Insight: Two Motions, Completely Independent",
                          color=ORANGE)
        self.play(Write(hdr))

        insight = Text(
            "The horizontal speed has ZERO effect on how fast you fall.",
            font_size=25, color=ORANGE,
        )
        insight.move_to([0, 2.20, 0])

        # Show two balls: one thrown horizontally, one dropped
        # Both reach the ground at the same time
        ground = Line([-5.5, -1.8, 0], [5.5, -1.8, 0],
                      color=GRAY_C, stroke_width=2)

        # Ball A: thrown horizontally (constant horizontal + falling)
        ball_A = Dot([-4.5, 1.5, 0], color=H_COL, radius=0.15)
        lbl_A = Text("Thrown\nhorizontally", font_size=18, color=H_COL)
        lbl_A.next_to(ball_A, UP, buff=0.12)

        # Ball B: dropped straight down (pure vertical)
        ball_B = Dot([2.5, 1.5, 0], color=G_COL, radius=0.15)
        lbl_B = Text("Dropped\nstraight down", font_size=18, color=G_COL)
        lbl_B.next_to(ball_B, UP, buff=0.12)

        # Animate both falling — same vertical motion, via always_redraw
        target_y = -1.8
        start_y  =  1.5
        total_t  = np.sqrt(2 * (start_y - target_y) / G_SIM)  # free-fall time
        vx_A = 1.2     # horizontal velocity of A

        fall_tracker = ValueTracker(0)

        def ball_A_pos():
            t = fall_tracker.get_value()
            y = start_y - 0.5 * G_SIM * t**2
            x = -4.5 + vx_A * t
            return [min(x, 4.5), max(y, target_y), 0]

        def ball_B_pos():
            t = fall_tracker.get_value()
            y = start_y - 0.5 * G_SIM * t**2
            return [2.5, max(y, target_y), 0]

        with self.voiceover(
            text="Here's the key insight. Horizontal motion and vertical "
                 "motion are completely independent. A ball thrown "
                 "sideways and a ball dropped straight down hit the "
                 "ground at exactly the same moment — Galileo proved "
                 "it by experiment."
        ) as tracker:
            self.play(FadeIn(insight))
            self.play(Create(ground))
            self.play(FadeIn(ball_A), FadeIn(lbl_A),
                      FadeIn(ball_B), FadeIn(lbl_B))

            ball_A.add_updater(lambda d: d.move_to(ball_A_pos()))
            ball_B.add_updater(lambda d: d.move_to(ball_B_pos()))

            # Horizontal velocity arrow for A
            h_arr = always_redraw(lambda: Arrow(
                ball_A.get_center(),
                ball_A.get_center() + RIGHT * 0.9,
                buff=0, color=H_COL, stroke_width=2.5,
                max_tip_length_to_length_ratio=0.35,
            ))
            self.add(h_arr)

            self.play(fall_tracker.animate.set_value(total_t),
                      run_time=2.8, rate_func=linear)

            ball_A.clear_updaters()
            ball_B.clear_updaters()
            self.remove(h_arr)

            # Flash when they land together
            self.play(Flash(ball_A.get_center(), color=H_COL, line_length=0.35),
                      Flash(ball_B.get_center(), color=G_COL, line_length=0.35))

            simultaneous = Text("They land at the SAME time!",
                                font_size=26, color=YELLOW_C, weight=BOLD)
            simultaneous.move_to([0, 0.6, 0])
            self.play(FadeIn(simultaneous))

        self.play(FadeOut(lbl_A), FadeOut(lbl_B))

        math_indep = MathTex(
            r"\ddot{x} = 0 \qquad \ddot{y} = -g",
            font_size=40, color=ORANGE,
        )
        math_indep.move_to([0, 2.20, 0])
        self.play(FadeOut(insight), Write(math_indep))

        note = make_note(
            "Galileo proved this by experiment — horizontal motion never affects free fall"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, ground, ball_A, ball_B,
                                  simultaneous, math_indep, note)))

    # ══════ S6: Combine → Parabola ════════════════════════════════════════════
    def _s6_combine(self):
        hdr = make_header("Combine Both → The Trajectory Appears", color=T_COL)
        self.play(Write(hdr))

        ax = make_traj_axes()
        x_lbl = ax.get_x_axis_label(
            MathTex(r"x\;(\mathrm{m})", font_size=22),
            edge=RIGHT, direction=RIGHT, buff=0.12,
        )
        y_lbl = ax.get_y_axis_label(
            MathTex(r"y\;(\mathrm{m})", font_size=22),
            edge=UP, direction=UP, buff=0.12,
        )

        # Animate dots appearing at equal time steps
        Tf  = T_flight()
        n_steps = 14
        step_dots = VGroup()
        for i in range(n_steps + 1):
            t  = i * Tf / n_steps
            xp, yp = traj_xy(t)
            dot = Dot(ax.c2p(xp, yp), radius=0.09, color=T_COL).set_opacity(0.7)
            step_dots.add(dot)

        # Draw the full curve through them
        curve = ax.plot_parametric_curve(
            lambda t: [traj_xy(t)[0], traj_xy(t)[1]],
            t_range=[0, Tf],
            color=T_COL, stroke_width=3,
        )

        # Ball tracing it
        ball = Dot(color=BALL_C, radius=0.14).move_to(ax.c2p(0, 0))
        shadow = TracedPath(ball.get_center,
                            stroke_color=T_COL, stroke_width=1.5,
                            stroke_opacity=0.4)

        # Key labels: peak, range — placed so they never overlap curve or axes
        xH, yH = traj_xy(Tf / 2)
        peak_dot  = Dot(ax.c2p(xH, yH), color=V_COL, radius=0.11)
        peak_lbl  = Text("H = max height", font_size=18, color=V_COL)
        peak_lbl.next_to(peak_dot, UP, buff=0.18)

        xR = traj_range()
        range_dot = Dot(ax.c2p(xR, 0), color=H_COL, radius=0.11)
        range_lbl = Text("R = range", font_size=18, color=H_COL)
        range_lbl.next_to(range_dot, UR, buff=0.15)

        # Derive the parabola equation (eliminate t)
        eq_para = make_eq_box(
            r"y = x\tan\theta \;-\; \frac{g\,x^2}{2v_0^2\cos^2\!\theta}",
            font_size=34, color=T_COL,
        )

        with self.voiceover(
            text="Now put both motions together, and a parabola appears. "
                 "If we eliminate time from the two equations, y becomes "
                 "a quadratic function of x — that's the trajectory."
        ) as tracker:
            self.play(Create(ax), FadeIn(x_lbl), FadeIn(y_lbl))
            self.play(FadeIn(step_dots, lag_ratio=0.12, run_time=1.8))
            self.play(Create(curve, run_time=2.0))
            self.add(shadow, ball)
            self.play(MoveAlongPath(ball, curve, run_time=2.2, rate_func=linear))
            self.remove(shadow)
            self.play(FadeIn(peak_dot), FadeIn(peak_lbl))
            self.play(FadeIn(range_dot), FadeIn(range_lbl))
            self.play(Write(eq_para, run_time=1.5))

        note = make_note(
            "Eliminate t from x(t) and y(t) → a quadratic in x → parabola"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, ax, x_lbl, y_lbl, curve, step_dots,
                                  ball, peak_dot, peak_lbl, range_dot,
                                  range_lbl, eq_para, note)))

    # ══════ S7: Key Equations ═════════════════════════════════════════════════
    def _s7_equations(self):
        hdr = make_header("What We Can Now Calculate", color=YELLOW_C)
        self.play(Write(hdr))

        eq_data = [
            (r"T \;=\; \frac{2\,v_0\sin\theta}{g}",
             "Time of flight", GREEN_C,
             "Double the vertical launch speed, double the air time"),
            (r"R \;=\; \frac{v_0^2\,\sin 2\theta}{g}",
             "Horizontal range", BLUE_C,
             "Maximum when sin(2θ)=1  →  θ = 45°"),
            (r"H \;=\; \frac{v_0^2\,\sin^2\!\theta}{2g}",
             "Maximum height", ORANGE,
             "Grows as the square of launch speed"),
        ]

        cards = VGroup()
        for tex, label, col, explain in eq_data:
            backing = RoundedRectangle(width=9.5, height=1.05,
                                       corner_radius=0.12,
                                       color=col, fill_color=col,
                                       fill_opacity=0.10, stroke_width=1.5)
            eq  = MathTex(tex, font_size=36, color=col)
            lbl = Text(label, font_size=20, color=col, weight=BOLD)
            exp = Text(explain, font_size=17, color=GRAY_B)
            eq.move_to(backing.get_left() + RIGHT * 2.2)
            lbl.move_to(backing.get_right() + LEFT * 3.2 + UP * 0.18)
            exp.move_to(backing.get_right() + LEFT * 3.2 + DOWN * 0.22)
            cards.add(VGroup(backing, eq, lbl, exp))

        cards.arrange(DOWN, buff=0.30)
        cards.move_to([0, -0.10, 0])

        with self.voiceover(
            text="From these two simple equations, we can now calculate "
                 "everything: the time of flight, the horizontal range, "
                 "and the maximum height the ball reaches."
        ) as tracker:
            for card in cards:
                self.play(FadeIn(card, shift=LEFT * 0.2,
                                  run_time=tracker.duration / len(cards)))

        note = make_note(
            "All three follow directly from x(t) = v₀cosθ·t and y(t) = v₀sinθ·t − ½gt²"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, cards, note)))

    # ══════ S8: Angle Effect ══════════════════════════════════════════════════
    def _s8_angles(self):
        hdr = make_header("Which Angle Throws Farthest? Let the Math Decide",
                          color=YELLOW_C)
        self.play(Write(hdr))

        # y_max raised from 4.0 → 6.5 so the 75° trajectory peak (which would
        # otherwise reach into the EQ zone) stays inside the AXES zone.
        ax = make_traj_axes(x_max=14, y_max=6.5)
        x_lbl = ax.get_x_axis_label(
            MathTex(r"x", font_size=22),
            edge=RIGHT, direction=RIGHT, buff=0.12,
        )
        self.play(Create(ax), FadeIn(x_lbl))

        angles_deg = [15, 30, 45, 60, 75]
        colors      = [PURPLE_C, BLUE_C, YELLOW_C, GREEN, RED_C]

        curves = VGroup()
        legend_items = VGroup()
        for deg, col in zip(angles_deg, colors):
            theta = np.radians(deg)
            Tf    = T_flight(theta)
            curve = ax.plot_parametric_curve(
                lambda t, th=theta: [traj_xy(t, th)[0], traj_xy(t, th)[1]],
                t_range=[0, Tf],
                color=col, stroke_width=2.5,
            )
            curves.add(curve)
            legend_items.add(Text(f"{deg}°", font_size=17, color=col))

        # Legend in top-right corner of axes area (clear of other text)
        legend_items.arrange(DOWN, buff=0.20)
        legend_items.move_to([4.8, 0.8, 0])

        # Highlight 45°
        theta45 = np.radians(45)
        Tf45    = T_flight(theta45)
        highlight = ax.plot_parametric_curve(
            lambda t: [traj_xy(t, theta45)[0], traj_xy(t, theta45)[1]],
            t_range=[0, Tf45],
            color=YELLOW_C, stroke_width=5.5,
        )

        best_lbl = Text("45° → maximum range", font_size=22,
                        color=YELLOW_C, weight=BOLD)
        best_lbl.move_to([0, 2.20, 0])
        warn_zone_violation(best_lbl, "best_lbl", "EQ")

        # Derivative argument — placed below the EQ zone (not next_to best_lbl)
        # so it never gets crossed by the descending 60°/75° trajectory arcs.
        deriv = MathTex(
            r"\frac{dR}{d\theta}=0 \;\Rightarrow\; \cos 2\theta = 0"
            r"\;\Rightarrow\; \theta = 45°",
            font_size=26, color=GRAY_B,
        )
        deriv.move_to([0, 1.20, 0])

        with self.voiceover(
            text="Which launch angle gives the longest range? Taking the "
                 "derivative of the range with respect to theta and "
                 "setting it to zero gives cosine of two theta equals "
                 "zero — so theta equals 45 degrees. Notice that 30 and "
                 "60 degrees give the same range — complementary angles "
                 "always do."
        ) as tracker:
            for curve in curves:
                self.play(Create(curve, run_time=0.6))
            self.play(FadeIn(legend_items))
            self.play(Create(highlight, run_time=0.8))
            self.play(FadeIn(best_lbl))
            self.play(Write(deriv, run_time=1.2))

        note = make_note(
            "Symmetry: 30° and 60° give the same range — complementary angles always do"
        )
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hdr, ax, x_lbl, legend_items, curves,
                                  highlight, best_lbl, deriv, note)))

    # ══════ S9: Real World ════════════════════════════════════════════════════
    def _s9_real_world(self):
        hdr = make_header("Real World Applications", color=BLUE_C)
        self.play(Write(hdr))

        # ── 1. Basketball ─────────────────────────────────────────────────────
        sub = Text("① Basketball — the arc to the hoop",
                   font_size=24, color=ORANGE)
        sub.move_to([0, 2.20, 0])

        ax1 = Axes(
            x_range=[0, 11, 2], y_range=[0, 4.5, 1],
            x_length=8.5, y_length=3.5,
            axis_config={"color": GRAY_C, "stroke_width": 1.2, "include_tip": False},
            tips=False,
        ).move_to([-0.5, -0.2, 0])

        # Hoop: circle at far end
        hoop_x, hoop_y = 9.5, 2.3
        hoop_scene = ax1.c2p(hoop_x, hoop_y)
        hoop = Circle(radius=0.22, color=ORANGE, stroke_width=3)
        hoop.move_to(hoop_scene)
        hoop_board = Rectangle(width=0.12, height=1.0,
                               color=GRAY_B, fill_color=GRAY_B,
                               fill_opacity=0.7, stroke_width=0)
        hoop_board.next_to(hoop, RIGHT, buff=0.05)

        # Find angle that passes through hoop
        # x = v0*cos(th)*t, y = v0*sin(th)*t - 0.5*g*t²  set (x,y)=(9.5,2.3)
        theta_bball = np.radians(52)
        v0_bball    = 4.8
        Tf_bb = T_flight(theta_bball, v0_bball)
        curve_bb = ax1.plot_parametric_curve(
            lambda t: [
                traj_xy(t, theta_bball, v0_bball)[0],
                traj_xy(t, theta_bball, v0_bball)[1],
            ],
            t_range=[0, Tf_bb * 0.82],
            color=ORANGE, stroke_width=3,
        )
        ball_bb = Dot(color=ORANGE, radius=0.14).move_to(ax1.c2p(0, 0))

        angle_lbl = Text("~52° optimal for this distance", font_size=18,
                         color=ORANGE)
        angle_lbl.to_edge(DOWN, buff=0.28)

        with self.voiceover(
            text="In basketball, players intuitively find the launch "
                 "angle — often around 52 degrees — that arcs the ball "
                 "into the hoop."
        ) as tracker:
            self.play(FadeIn(sub))
            self.play(Create(ax1), FadeIn(hoop), FadeIn(hoop_board))
            self.add(ball_bb)
            self.play(MoveAlongPath(ball_bb, curve_bb, run_time=2.0,
                                    rate_func=linear))
            self.play(FadeIn(angle_lbl))

        self.wait(0.5)
        self.play(FadeOut(VGroup(sub, ax1, hoop, hoop_board, ball_bb,
                                  curve_bb, angle_lbl)))

        # ── 2. Water Fountain ─────────────────────────────────────────────────
        sub2 = Text("② Water Fountain — jets at different angles",
                    font_size=24, color=BLUE_C)
        sub2.move_to([0, 2.20, 0])

        nozzle = Dot([0, -1.8, 0], color=GRAY_B, radius=0.15)
        nozzle_base = Rectangle(width=0.5, height=0.3,
                                color=GRAY_C, fill_color=GRAY_C,
                                fill_opacity=0.8, stroke_width=0)
        nozzle_base.next_to(nozzle, DOWN, buff=0.0)

        fountain_curves = VGroup()
        fan_angles = [50, 65, 80, 90, 100, 115, 130]
        v0_fount   = 3.5
        for deg in fan_angles:
            theta_f = np.radians(deg)
            Tf_f    = T_flight(theta_f, v0_fount)
            pts = []
            for t in np.linspace(0, Tf_f, 60):
                x = v0_fount * np.cos(theta_f) * t
                y = v0_fount * np.sin(theta_f) * t - 0.5 * G_SIM * t**2
                pts.append([x * 0.75, y * 0.75 - 1.8, 0])
            curve_f = VMobject()
            curve_f.set_points_smoothly(np.array(pts))
            col = interpolate_color(BLUE_C, TEAL_C, (deg - 50) / 80)
            curve_f.set_stroke(col, width=2.0, opacity=0.8)
            fountain_curves.add(curve_f)

        fount_lbl = Text("Same v₀, different angles → different arcs",
                         font_size=19, color=BLUE_C)
        fount_lbl.to_edge(DOWN, buff=0.28)

        with self.voiceover(
            text="Water fountains shoot jets at the same speed but "
                 "different angles, tracing out a whole family of these "
                 "parabolic arcs."
        ) as tracker:
            self.play(FadeIn(sub2))
            self.play(FadeIn(nozzle), FadeIn(nozzle_base))
            self.play(Create(fountain_curves, lag_ratio=0.1, run_time=2.0))
            self.play(FadeIn(fount_lbl))

        self.wait(0.5)
        self.play(FadeOut(VGroup(sub2, nozzle, nozzle_base,
                                  fountain_curves, fount_lbl)))

        # ── 3. Javelin / Long Jump ────────────────────────────────────────────
        sub3 = Text("③ Athletics — javelin & long jump",
                    font_size=24, color=GREEN_C)
        sub3.move_to([0, 2.20, 0])

        ax3 = Axes(
            x_range=[0, 14, 2], y_range=[0, 4, 1],
            x_length=10.5, y_length=3.5,
            axis_config={"color": GRAY_C, "stroke_width": 1.2, "include_tip": False},
            tips=False,
        ).move_to([0, -0.2, 0])

        jav_data = [
            (35, 4.5, RED_C),
            (45, 4.5, GREEN_C),
        ]
        jav_curves = VGroup()
        for deg, v0j, col in jav_data:
            theta_j = np.radians(deg)
            Tf_j    = T_flight(theta_j, v0j)
            c = ax3.plot_parametric_curve(
                lambda t, th=theta_j, v=v0j: [
                    traj_xy(t, th, v)[0], traj_xy(t, th, v)[1]
                ],
                t_range=[0, Tf_j],
                color=col, stroke_width=2.5,
            )
            jav_curves.add(c)

        # Corner-anchored legend (was: labels floating at trajectory-dependent
        # positions, which drifted into the curves/axes area).
        jav_legend = VGroup(
            Text("35° — real-world optimal (air drag)", font_size=15, color=RED_C),
            Text("45° — no-drag ideal", font_size=15, color=GREEN_C),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        # Shift below the header (which spans most of the top edge) to
        # avoid overlapping "Real World Applications".
        jav_legend.to_corner(UR, buff=0.4).shift(DOWN * 0.9)

        jav_note = Text(
            "Air resistance shifts optimal angle below 45° in real throws",
            font_size=19, color=GRAY_B,
        )
        jav_note.to_edge(DOWN, buff=0.28)

        with self.voiceover(
            text="In javelin throwing, air resistance shifts the optimal "
                 "angle from the ideal 45 degrees down to around 35 "
                 "degrees in real throws."
        ) as tracker:
            self.play(FadeIn(sub3))
            self.play(Create(ax3))
            self.play(Create(jav_curves, lag_ratio=0.5, run_time=1.5))
            self.play(FadeIn(jav_legend))
            self.play(FadeIn(jav_note))

        self.wait(0.5)
        self.play(FadeOut(VGroup(sub3, ax3, jav_curves, jav_legend, jav_note)))

        # ── 4. Orbital Mechanics (extreme case) ───────────────────────────────
        sub4 = Text("④ The extreme case: Throw fast enough → Orbit!",
                    font_size=24, color=PURPLE_C)
        sub4.move_to([0, 2.20, 0])

        # Earth circle in center, then an arc becoming nearly circular
        earth = Circle(radius=1.2, color=BLUE_E,
                       fill_color=BLUE_E, fill_opacity=0.6, stroke_width=2)
        earth.move_to([0, -0.5, 0])
        atmo  = Circle(radius=1.5, color=TEAL_C,
                       stroke_width=1.0, stroke_opacity=0.4, fill_opacity=0)
        atmo.move_to(earth.get_center())

        # Multiple arcs from surface, getting more "orbital"
        orbit_colors = [ORANGE, YELLOW_C, GREEN, PURPLE_C]
        orbit_arcs   = VGroup()
        for i, col in enumerate(orbit_colors):
            frac = (i + 1) / len(orbit_colors)
            # Increasingly curved path: partial ellipse
            arc = Arc(
                radius=1.2 + i * 0.55,
                start_angle=PI,
                angle=-(PI / 2 + frac * PI),
                color=col, stroke_width=2.0,
            )
            arc.move_to(earth.get_center())
            orbit_arcs.add(arc)

        # Labels for the orbit arcs — staggered on the right side
        orbit_labels = VGroup()
        for i, (col, lbl_txt) in enumerate(zip(
            orbit_colors,
            ["slow throw", "faster", "faster still", "orbital speed (8 km/s)!"],
        )):
            lbl = Text(lbl_txt, font_size=15, color=col)
            lbl.move_to([4.2, 1.4 - i * 0.55, 0])
            orbit_labels.add(lbl)

        orbit_note = Text(
            "Newton realised: the Moon is just a very fast projectile!",
            font_size=20, color=PURPLE_C,
        )
        orbit_note.to_edge(DOWN, buff=0.28)

        with self.voiceover(
            text="And here's the extreme case. Throw the ball fast "
                 "enough, and it falls around the curve of the Earth "
                 "forever — that's an orbit. Newton realized the Moon "
                 "is just a very fast projectile."
        ) as tracker:
            self.play(FadeIn(sub4))
            self.play(Create(earth), Create(atmo))
            self.play(Create(orbit_arcs, lag_ratio=0.4, run_time=2.0))
            for lbl in orbit_labels:
                self.play(FadeIn(lbl), run_time=0.35)
            self.play(FadeIn(orbit_note))

        self.wait(0.5)
        self.play(FadeOut(VGroup(hdr, sub4, earth, atmo, orbit_arcs,
                                  orbit_labels, orbit_note)))
        # Clear any residual mobjects
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)))

    # ══════ S10: Summary ══════════════════════════════════════════════════════
    def _s10_summary(self):
        self.camera.background_color = BG
        hdr = make_header("The Beauty of First Principles", color=T_COL)
        self.play(Write(hdr))

        # Central equation
        eq_main = MathTex(
            r"\begin{cases}"
            r"x(t) = v_0\cos\theta \cdot t \\[4pt]"
            r"y(t) = v_0\sin\theta \cdot t - \tfrac{1}{2}g t^2"
            r"\end{cases}",
            font_size=38,
        )
        eq_main.move_to(UP * 1.5)

        arrow_down = Arrow(UP * 0.4, DOWN * 0.4, color=GRAY_B,
                           stroke_width=2.5, buff=0).move_to(UP * 0.3)

        result = MathTex(
            r"y = x\tan\theta - \frac{g\,x^2}{2v_0^2\cos^2\!\theta}",
            font_size=40, color=T_COL,
        )
        result.move_to(DOWN * 0.5)

        # Key principles grid — placed below result with enough gap
        principles = VGroup(
            Text("Horizontal: constant velocity  (Newton I)",
                 font_size=20, color=H_COL),
            Text("Vertical: constant acceleration  g = 9.8 m/s²  (Newton II)",
                 font_size=20, color=V_COL),
            Text("Two motions are independent  (Galileo's insight)",
                 font_size=20, color=ORANGE),
            Text("Together: any parabolic trajectory on Earth",
                 font_size=20, color=T_COL),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        principles.move_to(DOWN * 2.4)

        tagline = Text(
            "Two laws + one insight = every projectile that ever flew.",
            font_size=22, color=YELLOW_C, weight=BOLD,
        )
        tagline.to_edge(DOWN, buff=0.28)

        with self.voiceover(
            text="Two laws of motion, plus Galileo's insight that they're "
                 "independent, explain every projectile that has ever "
                 "flown — from a thrown ball to an orbiting moon."
        ) as tracker:
            self.play(Write(eq_main, run_time=1.8))
            self.play(GrowArrow(arrow_down))
            self.play(Write(result, run_time=1.5))
            self.play(FadeIn(principles, lag_ratio=0.2, run_time=1.2))
            self.play(Write(tagline))

        self.wait(1.0)
        self.play(FadeOut(Group(*self.mobjects)))
