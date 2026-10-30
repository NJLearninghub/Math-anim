"""Shared script data: (start second, spoken text for TTS, caption text).

`speech` is phrased for the TTS engine (symbols spelled out); `caption` is what
viewers read on screen. Each line must finish before the next line's start.
"""
TOTAL = 45.0

LINES = [
    (0.0,
     "Half-wave or full-wave — which one is better? Half-wave uses just one diode with the load.",
     "Half-wave or full-wave — which one is better? Half-wave uses just one diode with the load."),
    (5.3,
     "In the positive half cycle, the diode is forward biased, so current flows.",
     "In the positive half cycle, the diode is forward biased, so current flows."),
    (9.3,
     "And in the negative half, it's reverse biased, so the current is zero.",
     "And in the negative half, it's reverse biased, so the current is zero."),
    (13.3,
     "So only the positive half cycles reach the output — the negative halves just go unused. Just one pulse per cycle.",
     "So only the positive half cycles reach the output — the negative halves just go unused. Just one pulse per cycle."),
    (20.4,
     "Now full-wave: a centre-tap transformer with two diodes.",
     "Now full-wave: a centre-tap transformer with two diodes."),
    (23.6,
     "When A is positive, D one conducts… and when B is positive, D two takes over.",
     "When A is positive, D1 conducts… and when B is positive, D2 takes over."),
    (29.2,
     "The clever part — either way, load current flows the same direction.",
     "The clever part — either way, load current flows the same direction."),
    (33.0,
     "So both half cycles get used — two pulses every cycle.",
     "So both half cycles get used — two pulses every cycle."),
    (37.4,
     "The result? DC value doubles — two V m by pi — and efficiency jumps from forty point six to eighty one point two percent!",
     "The result? DC value doubles — 2Vm/π — and efficiency jumps from 40.6% to 81.2%!"),
]
