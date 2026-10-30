"""Synthesise a royalty-free lo-fi background loop (no samples, no downloads).

Am - F - C - G at 96 BPM, soft pad + bass + muted pluck + light drums.
Output: 44.1 kHz stereo 16-bit WAV, `--duration` seconds with fade in/out.
"""
import argparse
import wave

import numpy as np

SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT

# (root, chord tones) in Hz, one chord per bar
CHORDS = [
    (110.00, [220.00, 261.63, 329.63, 392.00]),  # Am7
    (87.31, [174.61, 220.00, 261.63, 329.63]),   # Fmaj7
    (130.81, [196.00, 261.63, 329.63, 392.00]),  # C
    (98.00, [196.00, 246.94, 293.66, 392.00]),   # G
]


def lowpass(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def env(n, attack, release):
    t = np.arange(n) / SR
    e = np.minimum(t / max(attack, 1e-4), 1.0)
    e *= np.minimum((n / SR - t) / max(release, 1e-4), 1.0)
    return np.clip(e, 0, 1)


def place(buf, sig, start):
    i = int(start * SR)
    j = min(i + len(sig), len(buf))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def tone(freq, dur, harmonics=((1, 1.0),), detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for h, amp in harmonics:
        out += amp * np.sin(2 * np.pi * freq * h * t)
        if detune:
            out += 0.6 * amp * np.sin(2 * np.pi * freq * h * (1 + detune) * t)
    return out


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def snare(rng):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    noise = lowpass(rng.standard_normal(n), 5000)
    return (0.5 * noise + 0.3 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 18)


def hat(rng):
    n = int(0.06 * SR)
    noise = rng.standard_normal(n)
    noise = noise - lowpass(noise, 6000)  # crude high-pass
    return noise * np.exp(-np.arange(n) / SR * 90)


def build(duration):
    rng = np.random.default_rng(7)
    n = int(duration * SR)
    pad = np.zeros(n)
    bass = np.zeros(n)
    pluck = np.zeros(n)
    drums = np.zeros(n)

    bars = int(np.ceil(duration / BAR))
    k, s, h = kick(), snare(rng), hat(rng)
    for b in range(bars):
        root, tones = CHORDS[b % len(CHORDS)]
        t0 = b * BAR
        for f in tones:
            sig = tone(f, BAR + 0.6, ((1, 1.0), (2, 0.25)), detune=0.004)
            place(pad, sig * env(len(sig), 0.6, 0.9) * 0.12, t0)
        sig = tone(root, BAR, ((1, 1.0), (2, 0.2)))
        place(bass, sig * env(len(sig), 0.03, 0.35) * 0.45, t0)
        # arpeggiated muted pluck on 8ths, gentle swing
        for i in range(8):
            swing = 0.06 * BEAT if i % 2 else 0
            f = tones[[0, 2, 1, 3, 2, 1, 3, 2][i]] * 2
            sig = tone(f, 0.5, ((1, 1.0), (3, 0.15)))
            place(pluck, sig * np.exp(-np.arange(len(sig)) / SR * 7) * 0.10, t0 + i * BEAT / 2 + swing)
        # drums
        for beat in (0, 2):
            place(drums, k * 0.9, t0 + beat * BEAT)
        for beat in (1, 3):
            place(drums, s * 0.45, t0 + beat * BEAT)
        for i in range(8):
            swing = 0.06 * BEAT if i % 2 else 0
            place(drums, h * (0.25 if i % 2 else 0.4), t0 + i * BEAT / 2 + swing)

    mix = lowpass(pad + pluck, 3200) + bass + drums * 0.8
    # tiny stereo width via a short haas delay on one channel of the pad/pluck
    left = mix
    d = int(0.012 * SR)
    right = mix.copy()
    right[d:] = 0.85 * mix[d:] + 0.15 * lowpass(pad + pluck, 3200)[:-d]
    stereo = np.stack([left, right], axis=1)
    stereo *= env(n, 1.0, 2.5)[:, None]
    stereo /= np.max(np.abs(stereo)) / 0.9
    return stereo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, default=45.0)
    ap.add_argument("--out", default="music.wav")
    a = ap.parse_args()
    data = (build(a.duration) * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"wrote {a.out} ({a.duration:.1f}s)")


if __name__ == "__main__":
    main()
