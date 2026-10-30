"""Mix voiceover + ducked music onto the video and burn in word-highlight captions."""
import argparse
import json
import os
import subprocess
import tempfile

GAP = 0.25
ACCENT = "&H004D8CFF&"  # BGR of the video's orange accent
WHITE = "&H00FFFFFF&"


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def shout(word):
    """Uppercase for punch, but leave math tokens (2Vm/π) alone."""
    return word if "π" in word else word.upper()


def build_ass(timing, path, margin_v, font_size):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,{font_size},{WHITE},{WHITE},&H00101010&,&H80000000&,1,0,0,0,100,100,0,0,1,7,2,2,70,70,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for clip in timing:
        words = clip["caption"].split()
        weights = [len(w) + 2 for w in words]
        # word timing: clip duration split by character weight (Sarvam returns no timestamps)
        t = clip["start"]
        total = sum(weights)
        times = []
        for w in weights:
            d = clip["dur"] * w / total
            times.append((t, t + d))
            t += d
        # 3-word chunks; one event per word with that word highlighted
        for c in range(0, len(words), 3):
            idx = range(c, min(c + 3, len(words)))
            for k in idx:
                text = " ".join(
                    (f"{{\\c{ACCENT}}}{shout(words[j])}{{\\c{WHITE}}}" if j == k else shout(words[j])) for j in idx
                )
                pop = "{\\fscx88\\fscy88\\t(0,90,\\fscx100\\fscy100)}"
                events.append(f"Dialogue: 0,{ts(times[k][0])},{ts(times[k][1])},Cap,,0,0,0,,{pop}{text}")
    with open(path, "w", encoding="utf8") as f:
        f.write(head + "\n".join(events) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--timing", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--music-gain", type=float, default=0.5, help="music level before ducking")
    ap.add_argument("--caption-margin", type=int, default=190, help="px from bottom")
    ap.add_argument("--font-size", type=int, default=74)
    a = ap.parse_args()

    timing = json.load(open(a.timing))
    inputs = ["-i", a.video, "-i", a.music]
    filt = []
    labels = []
    for i, c in enumerate(timing):
        inputs += ["-i", c["file"]]
        ms = int(c["start"] * 1000)
        tempo = max(1.0, min(c["dur"] / (c["slot"] + GAP * 0.8), 1.25))
        chain = f"[{i + 2}:a]aresample=48000,aformat=channel_layouts=mono"
        if tempo > 1.001:
            chain += f",atempo={tempo:.3f}"
        chain += f",adelay={ms}|{ms}[v{i}]"
        filt.append(chain)
        labels.append(f"[v{i}]")
    n = len(timing)
    filt.append("".join(labels) + f"amix=inputs={n}:normalize=0:dropout_transition=0,"
                "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,asplit=2[vox][vsc]")
    filt.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.music_gain}[mus]")
    filt.append("[mus][vsc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[duck]")
    filt.append("[vox][duck]amix=inputs=2:normalize=0:duration=longest,"
                "loudnorm=I=-14:TP=-1.5:LRA=9,atrim=0:45,aresample=48000[aout]")

    vf = "null"
    tmp = None
    if not a.no_captions:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".ass", delete=False)
        tmp.close()
        build_ass(timing, tmp.name, a.caption_margin, a.font_size)
        vf = f"ass={tmp.name}"
    filt.append(f"[0:v]{vf}[vout]")

    cmd = ["ffmpeg", "-hide_banner", "-y", *inputs, "-filter_complex", ";".join(filt),
           "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-t", "45", a.out]
    subprocess.run(cmd, check=True)
    if tmp:
        os.unlink(tmp.name)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
