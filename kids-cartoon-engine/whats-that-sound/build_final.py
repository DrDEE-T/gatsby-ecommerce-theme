"""Final ocean episode edit: Veo clips + voice lines + Veo native sound + music bed.
Each shot is stretched (slow motion, then hold) when its dialogue runs longer than the clip."""
import subprocess, wave, json, os, sys
import numpy as np

D = sys.argv[1]
SR, W, H, FPS, XF = 44100, 1080, 1920, 30, 0.3
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"


def run(*a):
    subprocess.run(a, check=True)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def pcm(f, start=0.0, end=None, trim=True, norm=0.8):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    a = a[int(start * SR): int(end * SR) if end else None]
    if trim:
        idx = np.where(np.abs(a) > 0.01)[0]
        a = a[max(idx[0] - 400, 0): idx[-1] + 2000] if len(idx) else a
    return a / (np.abs(a).max() + 1e-9) * norm if norm else a


V = lambda n, **k: pcm(os.path.join(D, f"v{n}.mp3"), **k)
# (clip, first line start, [voice lines], gap between lines)
shots = [
    ("c1.mp4", 1.6, [V(1, end=1.85)]),
    ("c2.mp4", 1.0, [V(2)]),
    ("c3.mp4", 0.6, [V(3), V(4)]),
    ("c4.mp4", 1.8, [V(5), V(6)]),
    ("c5.mp4", 0.5, [V(7), V(8)]),
]
GAP, TAIL, END = 0.35, 0.6, 3.0

plan, t0 = [], 0.0
for clip, start, lines in shots:
    path = os.path.join(D, clip)
    cd = dur(path)
    cues, t = [], start
    for a in lines:
        cues.append((t, a)); t += len(a) / SR + GAP
    sd = max(cd, t - GAP + TAIL)
    plan.append(dict(path=path, clip=cd, dur=sd, cues=cues, t0=t0))
    t0 += sd
total = t0 + END
n = int((total + 1) * SR)

voice, sfx = np.zeros(n), np.zeros(n)
for p in plan:
    for t, a in p["cues"]:
        i = int((p["t0"] + t) * SR); voice[i:i + len(a)] += a
    # Veo native audio; stretched with the picture when the shot is slowed
    f = min(p["dur"] / p["clip"], 1.5)
    a = pcm(p["path"], trim=False, norm=None)
    if f > 1.01:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p["path"], "-af", f"atempo={1 / f:.4f}", "-ac", "1",
                              "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    a = a[: int(p["dur"] * SR)]
    k = min(int(0.15 * SR), len(a) // 2)
    a[:k] *= np.linspace(0, 1, k); a[-k:] *= np.linspace(1, 0, k)
    i = int(p["t0"] * SR); sfx[i:i + len(a)] += a

music = pcm(os.path.join(D, "music.mp3"), trim=False, norm=1.0)
music = np.pad(music, (0, max(0, n - len(music))))[:n]
fade = int(2.5 * SR); music[int(total * SR) - fade:int(total * SR)] *= np.linspace(1, 0, fade); music[int(total * SR):] = 0

sp = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
duck = 1 - 0.65 * np.clip(sp / 0.04, 0, 1)
sfx = sfx / (np.abs(sfx).max() + 1e-9)
mix = voice * 1.0 + sfx * 0.45 * duck + music * 0.18 * duck
mix = mix[: int(total * SR)]
mix = mix / np.abs(mix).max() * 0.92
with wave.open(os.path.join(D, "final_mix.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

for fn, txt in [("t1.txt", "What's That Sound?"), ("t2.txt", "At the Ocean"), ("e1.txt", "Bye, ocean animals!"),
                ("e2.txt", "Visuals and voices are AI-generated.")]:
    open(os.path.join(D, fn), "w").write(txt)

parts = []
for i, p in enumerate(plan):
    f = min(p["dur"] / p["clip"], 1.5)
    hold = p["dur"] + XF - p["clip"] * f
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setpts={f:.4f}*PTS,fps={FPS},"
          f"tpad=stop_mode=clone:stop_duration={max(hold, 0):.3f}")
    if i == 0:
        for tf, size, y, col in [("t1.txt", 96, "h*0.07", "0x5b3a8a"), ("t2.txt", 72, "h*0.07+120", "0x2a7fa8")]:
            vf += (f",drawtext=fontfile={FONT}:textfile={os.path.join(D, tf)}:fontsize={size}:fontcolor=white:"
                   f"borderw=6:bordercolor={col}:x=(w-tw)/2:y={y}:enable='lt(t,2.6)':alpha='if(lt(t,2),1,(2.6-t)/0.6)'")
    out = os.path.join(D, f"s{i + 1}.mp4")
    run("ffmpeg", "-v", "error", "-y", "-i", p["path"], "-an", "-vf", vf, "-t", f"{p['dur'] + XF:.3f}",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out)
    parts.append((out, p["dur"] + XF))

endcard = os.path.join(D, "end.mp4")
vf = (f"drawtext=fontfile={FONT}:textfile={os.path.join(D, 'e1.txt')}:fontsize=88:fontcolor=white:x=(w-tw)/2:y=h*0.44,"
      f"drawtext=fontfile={FONT}:textfile={os.path.join(D, 'e2.txt')}:fontsize=40:fontcolor=0xdfefff:x=(w-tw)/2:y=h*0.56")
run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x1f6f9c:s={W}x{H}:d={END}:r={FPS}", "-vf", vf,
    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", endcard)
parts.append((endcard, END))

inputs, filt, last, off = [], [], "0:v", 0.0
for p, _ in parts:
    inputs += ["-i", p]
for i in range(1, len(parts)):
    off += parts[i - 1][1] - XF
    filt.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]"); last = f"x{i}"
run("ffmpeg", "-v", "error", "-y", *inputs, "-i", os.path.join(D, "final_mix.wav"), "-filter_complex", ";".join(filt),
    "-map", f"[{last}]", "-map", f"{len(parts)}:a", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", os.path.join(D, "ocean_episode_final.mp4"))
print(json.dumps([dict(clip=round(p["clip"], 2), dur=round(p["dur"], 2)) for p in plan]), round(total, 2))
