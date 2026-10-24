"""
Navier-Stokes & Airfoil Aerodynamics — full animation.

Render single scene (fast preview):
    manim -pql src/main.py TitleScene

Render all scenes as one video:
    manim -pql src/main.py NavierStokesAirfoilFull

High quality:
    manim -qh src/main.py NavierStokesAirfoilFull
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from manim import *

from src.scenes.s01_title         import TitleScene
from src.scenes.s02_continuity    import ContinuityScene
from src.scenes.s03_navier_stokes import NavierStokesScene
from src.scenes.s04_airfoil_intro import AirfoilIntroScene
from src.scenes.s05_potential_flow import PotentialFlowScene
from src.scenes.s06_boundary_layer import BoundaryLayerScene
from src.scenes.s07_bernoulli_lift import BernoulliLiftScene
from src.scenes.s08_reynolds       import ReynoldsScene
from src.scenes.s09_summary        import SummaryScene


SCENE_CLASSES = [
    TitleScene,
    ContinuityScene,
    NavierStokesScene,
    AirfoilIntroScene,
    PotentialFlowScene,
    BoundaryLayerScene,
    BernoulliLiftScene,
    ReynoldsScene,
    SummaryScene,
]


class NavierStokesAirfoilFull(Scene):
    """Single-pass render: all 9 scenes in sequence."""

    def construct(self):
        for SceneClass in SCENE_CLASSES:
            instance = SceneClass()
            instance.renderer = self.renderer
            instance.camera = self.camera
            instance.construct()
            self.clear()
            self.wait(0.3)
