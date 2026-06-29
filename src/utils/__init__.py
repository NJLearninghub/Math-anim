from .airfoil import naca4_points, naca0012_polygon, naca4412_polygon, to_manim, camber_line
from .flow_field import JoukowskiFlow
from .colors import *
from .layout import (
    TITLE_Y, RULE_Y, EQ_Y, AXES_TOP, AXES_BOT, NOTE_Y,
    check_overlap, safe_label_position, clamp_to_zone, warn_zone_violation,
)
from .tts import OfflineTTSService
