"""Render Biscuit & Friends: python3 render.py [collect|sheet|full] [out.mp4]"""
import os, subprocess, sys, time
import numpy as np
import soundfile as sf
import skia
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(os.path.dirname(HERE), "pip"))
import draw as D
import audio as A
from show import build
import voice

OUT_W, OUT_H = 1920, 1080
FPS = A.FPS
HALF = 0.42  # transition half-length

SCENES = build()
STARTS = []
_acc = 0.0
for sc in SCENES:
    STARTS.append(_acc)
    _acc += sc.dur
TOTAL = _acc


def scene_at(T):
    for i in range(len(SCENES) - 1, -1, -1):
        if T >= STARTS[i]:
            return i
    return 0


def render_frame(T, surf):
    c = surf.getCanvas()
    c.save()
    c.scale(OUT_W / D.W, OUT_H / D.H)
    i = scene_at(T)
    sc = SCENES[i]
    t = T - STARTS[i]
    sc.draw(c, t)
    if i > 0 and sc.trans and t < HALF:
        D.cover(c, sc.trans, (HALF - t) / HALF, T)
    if i + 1 < len(SCENES) and SCENES[i + 1].trans and t > sc.dur - HALF:
        D.cover(c, SCENES[i + 1].trans, (t - (sc.dur - HALF)) / HALF, T)
    c.restore()


def render_chunk(args):
    k, f0, f1, path = args
    surf = skia.Surface(OUT_W, OUT_H)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OUT_W}x{OUT_H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        surf.getCanvas().clear(0xFFFFFFFF)
        render_frame(f / FPS, surf)
        img = surf.makeImageSnapshot()
        arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
        p.stdin.write(arr.tobytes())
    p.stdin.close()
    p.wait()
    return k


def build_audio(path):
    n = int((TOTAL + 1) * A.SR)
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    mus = np.zeros(n, np.float32)
    bed = np.zeros(n, np.float32)
    for st, sc in zip(STARTS, SCENES):
        for L in sc.lines:
            A.put(voice, L["y"] * L["gain"], st + L["start"])
        for (at, name, g) in sc.sfx:
            A.put(fx, A.get_sfx(name) * g, st + at)
        if sc.music:
            m = A.music(sc.music, sc.dur + 0.3) * 0.5 * sc.music_gain
            # music drop-outs (dramatic pauses)
            for (a, b) in sc.duck_zero:
                ia, ib = int(a * A.SR), int(b * A.SR)
                rampn = int(0.25 * A.SR)
                g = np.ones(len(m))
                g[ia:ib] = 0.12
                g[max(ia - rampn, 0):ia] = np.linspace(1, 0.12, ia - max(ia - rampn, 0))
                g[ib:ib + rampn] = np.linspace(0.12, 1, len(g[ib:ib + rampn]))
                m = m * g
            A.put(mus, m, st - 0.15)
        if sc.rain:
            r = A.rain_bed(sc.dur + 0.5, heavy=sc.rain == "heavy")
            fade = int(0.4 * A.SR)
            r[:fade] *= np.linspace(0, 1, fade)
            r[-fade:] *= np.linspace(1, 0, fade)
            A.put(bed, r * (0.5 if sc.rain == "heavy" else 0.35), st)
    # duck music + bed under voices
    env = np.abs(voice)
    k = int(0.15 * A.SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.clip(env * 6, 0, 1)
    duck = 1 - 0.55 * env
    mix = voice * 1.0 + fx * 0.75 + mus * duck + bed * duck
    mix = np.tanh(mix * 1.1) * 0.9
    stereo = np.stack([mix, mix], axis=1)
    sf.write(path, stereo, A.SR)


def sheet(path, times=None):
    """Contact sheet of frames for review."""
    times = times or []
    if not times:
        for st, sc in zip(STARTS, SCENES):
            for f in (0.15, 0.5, 0.85):
                times.append(st + sc.dur * f)
    cols = 6
    tw, th = 480, 270
    rows = (len(times) + cols - 1) // cols
    big = skia.Surface(cols * tw, rows * th)
    bc = big.getCanvas()
    bc.clear(0xFF000000)
    surf = skia.Surface(OUT_W, OUT_H)
    for j, T in enumerate(times):
        surf.getCanvas().clear(0xFFFFFFFF)
        render_frame(T, surf)
        img = surf.makeImageSnapshot()
        bc.drawImageRect(img, skia.Rect.MakeXYWH((j % cols) * tw, (j // cols) * th, tw - 4, th - 4),
                         skia.SamplingOptions(skia.FilterMode.kLinear))
        D.text(bc, f"{T:.1f}", (j % cols) * tw + 40, (j // cols) * th + 20, 22, 0xFFFFFFFF, tf=D.ROUND_TF, ow=4)
    big.makeImageSnapshot().save(path, skia.kPNG)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    print("total seconds:", round(TOTAL, 1))
    for st, sc in zip(STARTS, SCENES):
        print(f"  {sc.name:12s} {st:7.1f}  {sc.dur:5.1f}s")
    if mode == "collect":
        print("missing voice lines:", voice.write_todo())
    elif mode == "sheet":
        sheet(os.path.join(HERE, "sheet.png"))
    elif mode == "at":
        sheet(os.path.join(HERE, "sheet.png"), [float(x) for x in sys.argv[2:]])
    elif mode == "audio":
        build_audio(os.path.join(HERE, "audio.wav"))
    elif mode == "full":
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "episode.mp4")
        t0 = time.time()
        build_audio(os.path.join(HERE, "audio.wav"))
        nf = int(TOTAL * FPS)
        nproc = 4
        seg = (nf + nproc * 4 - 1) // (nproc * 4)
        jobs = []
        os.makedirs(os.path.join(HERE, "segs"), exist_ok=True)
        for k in range(0, nf, seg):
            jobs.append((len(jobs), k, min(k + seg, nf), os.path.join(HERE, "segs", f"s{len(jobs):03d}.mp4")))
        with Pool(nproc) as pool:
            for k in pool.imap_unordered(render_chunk, jobs):
                print(f"  chunk {k + 1}/{len(jobs)} done  {time.time() - t0:.0f}s", flush=True)
        with open(os.path.join(HERE, "segs", "list.txt"), "w") as f:
            for j in jobs:
                f.write(f"file '{j[3]}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                        os.path.join(HERE, "segs", "list.txt"), "-i", os.path.join(HERE, "audio.wav"),
                        "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
        print("wrote", out, f"{time.time() - t0:.0f}s")
