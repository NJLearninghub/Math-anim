import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from manim import *
from src.utils.colors import BG_COLOR


TERM_DATA = [
    # (slice_index, color, label, description)
    (1, YELLOW,    r"\rho\,\frac{\partial\vec{u}}{\partial t}",
     "Unsteady inertia:\nhow momentum changes in time"),
    (2, ORANGE,    r"\vec{u}\cdot\nabla\vec{u}",
     "Convective acceleration:\nfluid carrying its own momentum"),
    (3, BLUE_C,    r"-\nabla p",
     "Pressure gradient:\nfluid driven from high→low pressure"),
    (4, GREEN,     r"\mu\,\nabla^2\vec{u}",
     "Viscous diffusion:\nfriction between fluid layers"),
    (5, RED_C,     r"\vec{f}",
     "Body forces:\ngravity, electromagnetic, etc."),
]


class NavierStokesScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("Navier–Stokes Momentum Equation", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title))

        # Full equation (6 sub-expressions for per-term coloring)
        ns = MathTex(
            r"\rho",
            r"\left(\frac{\partial\vec{u}}{\partial t}",
            r"+ \vec{u}\cdot\nabla\vec{u}\right)",
            r"= -\nabla p",
            r"+ \mu\,\nabla^2\vec{u}",
            r"+ \vec{f}",
            font_size=44,
        )
        ns.move_to(UP * 1.2)

        self.play(Write(ns, run_time=2.5))
        self.wait(0.8)

        # ── Term-by-term highlight ─────────────────────────────────────
        descriptions = [
            (slice(0, 3), YELLOW, "Inertia terms  (left-hand side)",
             "Rate of change of momentum"),
            (slice(3, 4), BLUE_C, "Pressure gradient",
             "Pushes fluid from high → low pressure"),
            (slice(4, 5), GREEN,  "Viscous (diffusion) term",
             "Resistance from fluid friction (∝ viscosity μ)"),
            (slice(5, 6), RED_C,  "Body forces",
             "External forces: gravity, buoyancy…"),
        ]

        for sl, col, short, long_desc in descriptions:
            highlight = SurroundingRectangle(ns[sl], color=col, buff=0.12)
            label = Text(short, font_size=26, color=col)
            desc  = Text(long_desc, font_size=20, color=GRAY_B)
            label.next_to(ns, DOWN, buff=0.55)
            desc.next_to(label, DOWN, buff=0.22)

            self.play(Create(highlight), run_time=0.5)
            self.play(FadeIn(label), FadeIn(desc))
            self.wait(2.0)
            self.play(FadeOut(highlight), FadeOut(label), FadeOut(desc),
                      run_time=0.4)

        # ── Physical interpretation box ────────────────────────────────
        self.wait(0.5)
        interp = VGroup(
            Text("F = ma  for a fluid parcel", font_size=28, color=ANNOTATION),
            Text("(per unit volume)", font_size=20, color=GRAY_B),
        ).arrange(DOWN, buff=0.18)
        interp.move_to(DOWN * 2.0)

        box = SurroundingRectangle(interp, color=ANNOTATION, buff=0.25,
                                   corner_radius=0.15)
        self.play(Create(box), Write(interp))
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, ns, interp, box)))


# Reuse color name from manim
ANNOTATION = YELLOW_C
