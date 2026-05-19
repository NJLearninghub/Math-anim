#!/usr/bin/env bash
# Usage:
#   bash render.sh          → low quality preview of full animation
#   bash render.sh high     → 1080p60 final render
set -e
cd "$(dirname "$0")"

QUALITY="${1:-low}"
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
