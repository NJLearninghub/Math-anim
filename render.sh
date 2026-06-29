#!/usr/bin/env bash
# Usage:
#   bash render.sh                  → low quality preview, full N-S animation
#   bash render.sh high             → 1080p60 full N-S animation
#   bash render.sh low  shorts      → 540x960 preview, Bernoulli YouTube Short (9:16)
#   bash render.sh high shorts      → 1080x1920 Bernoulli YouTube Short (9:16)
set -e
cd "$(dirname "$0")"

QUALITY="${1:-low}"
TARGET="${2:-full}"

if [ "$TARGET" = "shorts" ]; then
    if [ "$QUALITY" = "high" ]; then
        RES="1080,1920"
        SUBDIR="1920p60"
        EXTRA_FLAGS="--fps 60"
    else
        RES="540,960"
        SUBDIR="960p15"
        EXTRA_FLAGS=""
    fi
    echo "Rendering BernoulliShortScene ($QUALITY quality, 9:16 vertical @ ${RES})..."
    manim -ql -r "$RES" $EXTRA_FLAGS --config_file manim_shorts.cfg \
          src/scenes/s10_bernoulli_short.py BernoulliShortScene
    OUTPUT="media/videos/s10_bernoulli_short/${SUBDIR}/BernoulliShortScene.mp4"
    mkdir -p media/final
    cp "$OUTPUT" media/final/BernoulliShort.mp4
    echo ""
    echo "Done! Video: $OUTPUT"
    echo "       Also: media/final/BernoulliShort.mp4"
else
    if [ "$QUALITY" = "high" ]; then
        FLAG="-qh"
        SUBDIR="1080p60"
    else
        FLAG="-ql"
        SUBDIR="480p15"
    fi
    echo "Rendering NavierStokesAirfoilFull ($QUALITY quality)..."
    manim $FLAG src/main.py NavierStokesAirfoilFull
    OUTPUT="media/videos/main/$SUBDIR/NavierStokesAirfoilFull.mp4"
    echo ""
    echo "Done! Video: $OUTPUT"
fi
