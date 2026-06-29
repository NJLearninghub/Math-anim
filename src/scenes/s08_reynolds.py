import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from manim import *
from src.utils.colors import BG_COLOR, ANNOTATION


class ReynoldsScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("Reynolds Number", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title))

        # ── Re definition ──────────────────────────────────────────────
        re_eq = MathTex(
            r"\mathrm{Re} = \frac{\rho\, U\, L}{\mu}",
            font_size=60,
        )
        re_eq.move_to(UP * 0.8)
        self.play(Write(re_eq, run_time=1.5))

        # Label each symbol
        symbols = [
            (r"\rho", "density",         LEFT * 1.6 + DOWN * 0.3,  YELLOW_C),
            (r"U",    "velocity",         LEFT * 0.5 + DOWN * 0.3,  ORANGE),
            (r"L",    "length scale (c)", RIGHT * 0.5 + DOWN * 0.3, GREEN),
            (r"\mu",  "dynamic viscosity",RIGHT * 1.8 + DOWN * 0.3, BLUE_C),
        ]
        sym_labels = VGroup()
        for sym, desc, offset, col in symbols:
            lbl = MathTex(sym, font_size=30, color=col)
            lbl.move_to(re_eq.get_center() + offset + DOWN * 1.5)
            desc_txt = Text(desc, font_size=18, color=col)
            desc_txt.next_to(lbl, DOWN, buff=0.1)
            sym_labels.add(lbl, desc_txt)

        self.play(FadeIn(sym_labels, lag_ratio=0.15))
        self.wait(1.0)

        # ── Re number line ─────────────────────────────────────────────
        self.play(FadeOut(sym_labels))

        ax = NumberLine(
            x_range=[0, 8, 1],
            length=9,
            include_numbers=False,
            color=GRAY_C,
        )
        ax.move_to(DOWN * 0.5)

        # Custom tick labels (log scale)
        log_labels = VGroup()
        ticks = [1, 2, 3, 4, 5, 6, 7]
        labels_str = ["10¹", "10²", "10³", "10⁴", "10⁵", "10⁶", "10⁷"]
        for t, lstr in zip(ticks, labels_str):
            lbl = Text(lstr, font_size=16, color=GRAY_B)
            lbl.next_to(ax.n2p(t), DOWN, buff=0.2)
            log_labels.add(lbl)

        self.play(Create(ax), FadeIn(log_labels))

        laminar_region = Rectangle(
            width=ax.n2p(4.7)[0] - ax.n2p(0)[0],
            height=0.35,
            color=BLUE_C, fill_color=BLUE_C, fill_opacity=0.25, stroke_width=0,
        ).align_to(ax, LEFT).shift(DOWN * 0.5)

        turb_region = Rectangle(
            width=ax.n2p(8)[0] - ax.n2p(4.7)[0],
            height=0.35,
            color=RED_C, fill_color=RED_C, fill_opacity=0.25, stroke_width=0,
        ).next_to(laminar_region, RIGHT, buff=0)

        lam_lbl  = Text("Laminar",   font_size=22, color=BLUE_C)
        turb_lbl = Text("Turbulent", font_size=22, color=RED_C)
        lam_lbl.move_to(laminar_region.get_center() + UP * 0.7)
        turb_lbl.move_to(turb_region.get_center()   + UP * 0.7)

        transition = DashedLine(ax.n2p(4.7) + UP * 0.5, ax.n2p(4.7) + DOWN * 0.5,
                                color=YELLOW_C, stroke_width=2)
        tr_lbl = Text("Re ≈ 5×10⁵\nTransition", font_size=16, color=YELLOW_C)
        tr_lbl.next_to(transition, UP, buff=0.12)

        self.play(
            Create(laminar_region), Create(turb_region),
            FadeIn(lam_lbl), FadeIn(turb_lbl),
        )
        self.play(Create(transition), FadeIn(tr_lbl))

        # Example dots
        dragonfly = Dot(ax.n2p(3), color=GREEN, radius=0.1)
        boeing    = Dot(ax.n2p(7), color=ORANGE, radius=0.1)
        drag_lbl  = Text("Dragonfly\nRe≈10³",    font_size=14, color=GREEN)
        boei_lbl  = Text("Boeing 737\nRe≈10⁷",  font_size=14, color=ORANGE)
        drag_lbl.next_to(dragonfly, UP, buff=0.15)
        boei_lbl.next_to(boeing, UP, buff=0.15)

        self.play(FadeIn(dragonfly), FadeIn(boeing))
        self.play(FadeIn(drag_lbl), FadeIn(boei_lbl))
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            title, re_eq, ax, log_labels,
            laminar_region, turb_region, lam_lbl, turb_lbl,
            transition, tr_lbl, dragonfly, boeing, drag_lbl, boei_lbl,
        )))
