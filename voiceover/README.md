# Rectifiers Short: voiceover + music

Adds a Sarvam (Bulbul) voiceover, ducked lo-fi music and word-highlight captions to the 45s Short.

```bash
cd voiceover
export SARVAM_API_KEY=...            # from the environment's secrets

python3 make_music.py --duration 45 --out /tmp/music.wav
python3 make_voiceover.py --outdir /tmp/vo            # --speaker / --model / --pace to taste
python3 build.py --video rectifiers_short_45s.mp4 --timing /tmp/vo/timing.json \
                 --music /tmp/music.wav --out rectifiers_short_voiced.mp4
```

- `script.py` holds the timestamped lines (TTS phrasing vs on-screen caption text).
- Each line is fitted to its slot: re-requested at a faster pace if it overruns.
- Output is mixed to -14 LUFS (YouTube's target); music is ducked under speech.
- `build.py --no-captions` skips the burned-in captions; `--music-gain` changes the music level.
