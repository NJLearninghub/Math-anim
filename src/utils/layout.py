"""Layout zone constants and overlap-safeguard helpers for scene mobjects.

Scenes that follow the strict-zone convention (see s12_projectile_motion.py)
divide the 14.2x8 frame into horizontal bands. These helpers detect and
prevent text/labels from drifting into neighbouring zones or colliding with
other mobjects.
"""
import warnings

from manim import DOWN, UP

# ── Zone y-coordinates (scene units) ────────────────────────────────────────
TITLE_Y  =  3.35   # centre of title text
RULE_Y   =  2.95   # dividing line below title
EQ_Y     =  2.20   # equation / key statement zone
AXES_TOP =  1.80   # top of animation/axes zone
AXES_BOT = -2.00   # bottom of animation/axes zone
NOTE_Y   = -3.10   # bottom note centre

# ── Named zone bounds (bottom, top) used by clamp/warn helpers ──────────────
_ZONE_BOUNDS = {
    "TITLE": (TITLE_Y - 0.3, TITLE_Y + 0.3),
    "EQ":    (EQ_Y - 0.3, EQ_Y + 0.3),
    "AXES":  (AXES_BOT, AXES_TOP),
    "NOTE":  (NOTE_Y - 0.2, NOTE_Y + 0.2),
}


def check_overlap(mob_a, mob_b, padding: float = 0.0) -> bool:
    """Return True if the bounding boxes of mob_a and mob_b overlap.

    `padding` symmetrically grows mob_a's box before testing, which is
    useful for enforcing a minimum gap between mobjects.
    """
    a_l = mob_a.get_left()[0] - padding
    a_r = mob_a.get_right()[0] + padding
    a_b = mob_a.get_bottom()[1] - padding
    a_t = mob_a.get_top()[1] + padding

    b_l = mob_b.get_left()[0]
    b_r = mob_b.get_right()[0]
    b_b = mob_b.get_bottom()[1]
    b_t = mob_b.get_top()[1]

    return (a_l < b_r) and (a_r > b_l) and (a_b < b_t) and (a_t > b_b)


def clamp_to_zone(mob, zone_name: str) -> None:
    """Shift `mob` vertically so its bounding box stays within `zone_name`."""
    if zone_name not in _ZONE_BOUNDS:
        raise ValueError(f"Unknown zone: {zone_name!r}. Use one of {list(_ZONE_BOUNDS)}")
    bot, top = _ZONE_BOUNDS[zone_name]

    mob_top = mob.get_top()[1]
    if mob_top > top:
        mob.shift(DOWN * (mob_top - top))

    mob_bot = mob.get_bottom()[1]
    if mob_bot < bot:
        mob.shift(UP * (bot - mob_bot))


def safe_label_position(label, preferred_y: float, avoid_mobs: list,
                         step: float = 0.25, max_steps: int = 8) -> None:
    """Place `label` at `preferred_y` (top edge), nudging it downward in
    `step` increments until it no longer overlaps any mobject in
    `avoid_mobs`. Final position is clamped to the AXES zone.

    Call this BEFORE adding/animating `label` into the scene.
    """
    label.set_y(preferred_y - label.get_height() / 2)

    for _ in range(max_steps):
        if not any(check_overlap(label, m, padding=0.05) for m in avoid_mobs):
            break
        label.shift(DOWN * step)

    clamp_to_zone(label, "AXES")


def warn_zone_violation(mob, mob_name: str, allowed_zone: str) -> bool:
    """Print a non-fatal warning if `mob` extends outside `allowed_zone`.

    Returns True if a violation was detected.
    """
    bot, top = _ZONE_BOUNDS[allowed_zone]
    violates = mob.get_top()[1] > top or mob.get_bottom()[1] < bot
    if violates:
        warnings.warn(
            f"[layout] {mob_name!r} top={mob.get_top()[1]:.2f} "
            f"bot={mob.get_bottom()[1]:.2f} outside {allowed_zone} "
            f"zone [{bot:.2f}, {top:.2f}]"
        )
    return violates
