"""Generate the Sarvam (Bulbul) voiceover, one clip per script line, fitted to its slot.

Reads the key from $SARVAM_API_KEY. Writes clips + timing.json into --outdir.
A line that overruns its slot is re-requested at a faster `pace`; any small
remainder is absorbed by the mixer with a gentle atempo.
"""
import argparse
import base64
import json
import os
import sys
import wave

import requests

from script import LINES, TOTAL

URL = "https://api.sarvam.ai/text-to-speech"
GAP = 0.25  # silence kept before the next line starts


def synth(key, text, args, pace):
    body = {
        "text": text,
        "language_code": "en-IN",
        "model": args.model,
        "speaker": args.speaker,
        "pace": round(pace, 2),
        "speech_sample_rate": 24000,
    }
    headers = {"api-subscription-key": key, "Content-Type": "application/json"}
    for attempt in range(2):
        r = requests.post(URL, headers=headers, json=body, timeout=60)
        if r.status_code == 422 and "language_code" in r.text and attempt == 0:
            body["target_language_code"] = body.pop("language_code")  # older field name
            continue
        break
    if not r.ok:
        sys.exit(f"Sarvam TTS error {r.status_code}: {r.text[:400]}")
    return base64.b64decode(r.json()["audios"][0])


def wav_seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--model", default="bulbul:v3")
    ap.add_argument("--speaker", default="shubh")
    ap.add_argument("--pace", type=float, default=1.1, help="starting pace (energetic Shorts delivery)")
    args = ap.parse_args()

    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        sys.exit("SARVAM_API_KEY is not set")
    os.makedirs(args.outdir, exist_ok=True)

    starts = [s for s, _, _ in LINES] + [TOTAL]
    timing = []
    for i, (start, speech, caption) in enumerate(LINES):
        slot = starts[i + 1] - start - GAP
        path = os.path.join(args.outdir, f"line_{i:02d}.wav")
        pace = args.pace
        for _ in range(4):
            with open(path, "wb") as f:
                f.write(synth(key, speech, args, pace))
            dur = wav_seconds(path)
            if dur <= slot:
                break
            pace = min(pace * dur / slot * 1.02, 2.0)
        print(f"line {i}: start={start:5.1f}s dur={dur:5.2f}s slot={slot:4.2f}s pace={pace:.2f}")
        timing.append({"file": path, "start": start, "dur": dur, "slot": slot, "caption": caption})

    with open(os.path.join(args.outdir, "timing.json"), "w") as f:
        json.dump(timing, f, indent=2)


if __name__ == "__main__":
    main()
