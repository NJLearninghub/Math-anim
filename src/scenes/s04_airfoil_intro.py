import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import BG_COLOR, AIRFOIL_FILL, AIRFOIL_STROKE, ANNOTATION
from src.utils.airfoil import naca4412_polygon, naca0012_polygon, to_manim, camber_line


class AirfoilIntroScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("NACA 4412 Airfoil Geometry", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title))

        # ── Draw airfoil ──────────────────────────────────────────────
        poly = naca4412_polygon(100)
        pts3d = to_manim(poly, chord=5.5)
        airfoil = VMobject()
        airfoil.set_points_smoothly(pts3d)
        airfoil.close_path()
        airfoil.set_fill(AIRFOIL_FILL, opacity=0.85)
        airfoil.set_stroke(AIRFOIL_STROKE, width=2.5)
        airfoil.move_to(DOWN * 0.3)

        self.play(Create(airfoil, run_time=2.0))
        self.wait(0.4)

        # ── Chord line ────────────────────────────────────────────────
        le = airfoil.get_left()
        te = airfoil.get_right()
        chord_line = DashedLine(le, te, color=GRAY_B, dash_length=0.15, stroke_width=1.5)
        chord_label = MathTex(r"c", font_size=32, color=GRAY_B)
        chord_label.next_to(chord_line, DOWN, buff=0.25)
        self.play(Create(chord_line), FadeIn(chord_label))

        # ── Camber line ───────────────────────────────────────────────
        cx, cy = camber_line(0.04, 0.4, n=60)
        camber_pts = to_manim(np.column_stack([cx, cy]), chord=5.5)
        camber_pts[:, 1] += airfoil.get_center()[1]
        camber_pts[:, 0] += airfoil.get_center()[0]
        camber_curve = VMobject()
        camber_curve.set_points_smoothly(camber_pts)
        camber_curve.set_stroke(YELLOW_C, width=1.8, opacity=0.9)
        camber_label = Text("camber line", font_size=18, color=YELLOW_C)
        camber_label.next_to(camber_curve.get_top(), UP, buff=0.15)
        self.play(Create(camber_curve), FadeIn(camber_label))

        # ── NACA digit breakdown ──────────────────────────────────────
        self.wait(0.5)
        naca_row = VGroup(
            Text("NACA ",     font_size=34, color=WHITE),
            Text("4",         font_size=34, color=GREEN),
            Text("4",         font_size=34, color=YELLOW),
            Text("12",        font_size=34, color=ORANGE),
        ).arrange(RIGHT, buff=0.05)
        naca_row.to_corner(UR, buff=0.5)

        def make_brace_label(obj, txt, direction, color):
            b = Brace(obj, direction, color=color)
            lbl = Text(txt, font_size=16, color=color)
            lbl.next_to(b, direction, buff=0.1)
            return VGroup(b, lbl)

        braces = VGroup(
            make_brace_label(naca_row[1], "4% max camber", UP,   GREEN),
            make_brace_label(naca_row[2], "at 40% chord",  UP,   YELLOW),
            make_brace_label(naca_row[3], "12% thickness", DOWN, ORANGE),
        )

        self.play(FadeIn(naca_row))
        for b in braces:
            self.play(FadeIn(b), run_time=0.6)
        self.wait(1.2)

        # ── Angle of attack arrow ─────────────────────────────────────
        aoa_arrow = Arrow(le + LEFT * 1.6 + DOWN * 0.22,
                          le + LEFT * 0.15,
                          color=RED_C, buff=0)
        aoa_label = Text("U∞, α=8°", font_size=22, color=RED_C)
        aoa_label.next_to(aoa_arrow, LEFT, buff=0.1)

        self.play(GrowArrow(aoa_arrow), FadeIn(aoa_label))
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            title, airfoil, chord_line, chord_label,
            camber_curve, camber_label, naca_row, braces,
            aoa_arrow, aoa_label,
        )))
