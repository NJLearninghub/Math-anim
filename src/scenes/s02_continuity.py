import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from manim import *
from src.utils.colors import BG_COLOR, ANNOTATION, FLOW_COLOR


class ContinuityScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # ── Title ──────────────────────────────────────────────────────
        title = Text("Mass Conservation", font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        underline = Line(title.get_left(), title.get_right(),
                         color=BLUE_C, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.08)
        self.play(Write(title), Create(underline))
        self.wait(0.3)

        # ── Control volume ─────────────────────────────────────────────
        box = Square(side_length=2.5, color=BLUE_B, stroke_width=2)
        box.set_fill(BLUE_E, opacity=0.15)
        box.move_to(LEFT * 2.5)
        cv_label = Text("Fluid\nElement", font_size=22, color=BLUE_B)
        cv_label.move_to(box.get_center())

        # Flux arrows on each face
        arrow_in  = Arrow(box.get_left()  + LEFT  * 1.2, box.get_left(),
                          color=GREEN, buff=0)
        arrow_out = Arrow(box.get_right(), box.get_right() + RIGHT * 1.2,
                          color=GREEN, buff=0)
        arrow_top = Arrow(box.get_top()   + UP    * 0.8, box.get_top(),
                          color=YELLOW, buff=0)
        arrow_bot = Arrow(box.get_bottom(), box.get_bottom() + DOWN * 0.8,
                          color=YELLOW, buff=0)

        lbl_in  = Text("mass in",  font_size=18, color=GREEN).next_to(arrow_in,  UP, buff=0.1)
        lbl_out = Text("mass out", font_size=18, color=GREEN).next_to(arrow_out, UP, buff=0.1)

        self.play(Create(box), Write(cv_label))
        self.play(
            GrowArrow(arrow_in), GrowArrow(arrow_out),
            GrowArrow(arrow_top), GrowArrow(arrow_bot),
        )
        self.play(FadeIn(lbl_in), FadeIn(lbl_out))

        balance = Text("mass in = mass out", font_size=26, color=ANNOTATION)
        balance.next_to(box, DOWN, buff=0.5)
        self.play(Write(balance))
        self.wait(1.0)

        # ── The equation ───────────────────────────────────────────────
        eq_label = Text("Continuity equation  (incompressible):",
                        font_size=28, color=GRAY_A)
        eq_label.move_to(RIGHT * 2.5 + UP * 1.2)

        eq = MathTex(r"\nabla \cdot \vec{u} = 0",
                     font_size=64, color=WHITE)
        eq.move_to(RIGHT * 2.5)

        brace = Brace(eq, DOWN, color=BLUE_C)
        brace_txt = Text("No net flow created or destroyed",
                         font_size=22, color=BLUE_C)
        brace_txt.next_to(brace, DOWN, buff=0.15)

        self.play(Write(eq_label))
        self.play(Write(eq, run_time=1.5))
        self.play(Create(brace), FadeIn(brace_txt))
        self.wait(1.5)

        # ── Vector field preview ──────────────────────────────────────
        self.play(
            FadeOut(VGroup(box, cv_label, arrow_in, arrow_out,
                           arrow_top, arrow_bot, lbl_in, lbl_out, balance)),
        )

        def div_free_field(pos):
            x, y = pos[0], pos[1]
            # Simple divergence-free field: rotation
            r2 = x**2 + y**2 + 0.01
            return np.array([-y / r2, x / r2, 0]) * 0.8

        vf = ArrowVectorField(div_free_field,
                              x_range=[-6, -0.5, 0.7],
                              y_range=[-3.0, 3.0, 0.7],
                              length_func=lambda n: 0.45 * n,
                              color=FLOW_COLOR)
        vf_label = Text("∇·u = 0  everywhere in flow",
                        font_size=22, color=FLOW_COLOR)
        vf_label.to_edge(DOWN, buff=0.4)

        self.play(Create(vf, run_time=1.5), FadeIn(vf_label))
        self.wait(2.0)
        self.play(
            FadeOut(VGroup(title, underline, eq_label, eq, brace,
                           brace_txt, vf, vf_label)),
        )
