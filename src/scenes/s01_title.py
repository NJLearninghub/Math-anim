import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from manim import *
from src.utils.colors import BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE, FLOW_COLOR
from src.utils.airfoil import naca0012_polygon, to_manim


class TitleScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # Faint airfoil silhouette
        poly = naca0012_polygon(80)
        pts3d = to_manim(poly, chord=7.0)
        airfoil_bg = VMobject()
        airfoil_bg.set_points_smoothly(pts3d)
        airfoil_bg.close_path()
        airfoil_bg.set_fill(AIRFOIL_FILL, opacity=0.25)
        airfoil_bg.set_stroke(AIRFOIL_STROKE, width=1, opacity=0.3)
        airfoil_bg.shift(DOWN * 0.3)

        # Flowing particle dots (background decoration)
        dots = VGroup(*[
            Dot(point=[-7 + i * 0.7, y, 0], radius=0.03, color=FLOW_COLOR)
            .set_opacity(0.4)
            for i in range(22) for y in [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
        ])

        title = Text("Navier–Stokes Equations", font_size=52, weight=BOLD)
        subtitle = Text("& Airfoil Aerodynamics", font_size=36, color=BLUE_C)
        subtitle.next_to(title, DOWN, buff=0.45)
        group = VGroup(title, subtitle).move_to(ORIGIN)

        tagline = Text("How mathematics governs flight", font_size=22,
                       color=GRAY_B, slant=ITALIC)
        tagline.next_to(group, DOWN, buff=0.9)

        self.add(airfoil_bg)
        self.play(FadeIn(dots, lag_ratio=0.02, run_time=1.2))
        self.play(Write(title, run_time=1.8))
        self.play(FadeIn(subtitle, shift=UP * 0.3, run_time=1.0))
        self.play(FadeIn(tagline, run_time=0.8))

        # Animate dots moving right
        self.play(dots.animate.shift(RIGHT * 1.5), run_time=2.5,
                  rate_func=linear)
        self.wait(1.5)
        self.play(FadeOut(VGroup(dots, airfoil_bg, title, subtitle, tagline),
                          run_time=1.0))
