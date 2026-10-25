"""Audio kit: character voices (Kokoro TTS), synthesized sound effects and music."""
import hashlib, os, re
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

SR = 44100
FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
rng = np.random.default_rng(7)

# who: (kokoro voice, pitch factor, final speed, gap between "..." chunks)
VOICES = {
    "pip":   ("af_sky",     1.0, 0.92, 0.0),
    "bitsy": ("af_nova",    1.0, 1.02, 0.0),
    "gus":   ("am_onyx",    1.0, 0.80, 0.18),
    "dot":   ("af_nicole",  1.0, 0.92, 0.0),
    "mama":  ("af_sarah",   1.0, 0.88, 0.0),
    "narr":  ("af_heart",   1.0, 0.95, 0.0),
}

# Free Microsoft Edge neural voices: who -> (voice, rate, pitch)
EDGE = {
    "pip":   ("en-US-AnaNeural",    "+0%",  "+0Hz"),
    "bitsy": ("en-GB-MaisieNeural", "+22%", "+0Hz"),
    "gus":   ("en-US-AndrewNeural", "-10%", "-6Hz"),
    "dot":   ("en-US-AnaNeural",    "-8%",  "+30Hz"),
    "mama":  ("en-US-JennyNeural",  "-5%",  "+0Hz"),
    "narr":  ("en-US-EmmaNeural",   "-5%",  "+0Hz"),
}

def edge_say(who, text, out_wav):
    import subprocess, tempfile
    voice, rate, pitch = EDGE[who]
    mp3 = out_wav + ".mp3"
    env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
    cmd = ["edge-tts", "--voice", voice, f"--rate={rate}", f"--pitch={pitch}", "--text", text, "--write-media", mp3]
    if os.environ.get("HTTPS_PROXY"):
        cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
    for attempt in range(4):
        r = subprocess.run(cmd, env=env, capture_output=True)
        if r.returncode == 0 and os.path.getsize(mp3) > 1000:
            break
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", out_wav], check=True)
    y, _ = sf.read(out_wav, dtype="float32")
    os.remove(mp3)
    return y

_kokoro = None

def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(HERE, "models", "kokoro.onnx"), os.path.join(HERE, "models", "voices.bin"))
    return _kokoro

def resample(x, ratio):
    """Read x at `ratio` speed (ratio > 1 shortens and raises pitch)."""
    n = int(len(x) / ratio)
    idx = np.arange(n) * ratio
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)

def speak(who, text):
    """Returns mono float32 at SR, cached on disk."""
    key = hashlib.md5(f"edge1|{who}|{text}".encode()).hexdigest()
    path = os.path.join(CACHE, f"{who}_{key}.wav")
    if os.path.exists(path):
        y, _ = sf.read(path, dtype="float32")
        return y
    gap = VOICES[who][3]
    chunks = [c.strip() for c in text.split("...")] if gap else [text]
    chunks = [c for c in chunks if c]
    out = []
    for i, ch in enumerate(chunks):
        a = edge_say(who, ch, path + f".part{i}.wav")
        os.remove(path + f".part{i}.wav")
        nz = np.where(np.abs(a) > 0.01)[0]
        if len(nz):
            a = a[max(nz[0] - 400, 0): nz[-1] + 2000]
        out.append(a)
        if i < len(chunks) - 1:
            out.append(np.zeros(int(gap * SR), np.float32))
    y = np.concatenate(out)
    y = y / (np.max(np.abs(y)) + 1e-6) * 0.9
    sf.write(path, y, SR)
    return y

def fit_length(y, n):
    """Time-stretch y (without changing pitch) to exactly n samples, so group lines stay in sync."""
    import subprocess, tempfile
    ratio = len(y) / n
    if abs(ratio - 1) < 0.02:
        out = y
    else:
        filt = []
        r = ratio
        while r > 2.0:
            filt.append("atempo=2.0"); r /= 2.0
        while r < 0.5:
            filt.append("atempo=0.5"); r /= 0.5
        filt.append(f"atempo={r:.4f}")
        with tempfile.TemporaryDirectory() as d:
            src, dst = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
            sf.write(src, y, SR)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", ",".join(filt), dst], check=True)
            out, _ = sf.read(dst, dtype="float32")
    if len(out) >= n:
        return out[:n]
    return np.concatenate([out, np.zeros(n - len(out), np.float32)])

def envelope(y):
    """Mouth-open amount per video frame."""
    hop = SR // FPS
    n = int(np.ceil(len(y) / hop))
    e = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(n)])
    e = e / (e.max() + 1e-6)
    return np.clip((e - 0.08) * 1.6, 0, 1)


# ---------- synthesis helpers ----------
def t_arr(d):
    return np.arange(int(d * SR)) / SR

def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    out = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); out[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na); out[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n); out[n - nr:] *= np.linspace(1, 0, nr)
    return out

def lp(x, f, order=2):
    b, a = butter(order, min(f / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)

def hp(x, f, order=2):
    b, a = butter(order, min(f / (SR / 2), 0.99), "high")
    return lfilter(b, a, x)

def bp(x, f1, f2, order=2):
    b, a = butter(order, [f1 / (SR / 2), min(f2 / (SR / 2), 0.99)], "band")
    return lfilter(b, a, x)

def noise(d):
    return rng.standard_normal(int(d * SR))

def sweep(f0, f1, d, shape="sin"):
    t = t_arr(d)
    f = np.geomspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == "sq":
        return np.sign(np.sin(ph))
    return np.sin(ph)

def norm(x, g=0.8):
    return (x / (np.max(np.abs(x)) + 1e-9) * g).astype(np.float32)

NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}

def hz(name):
    m = re.match(r"([A-G]#?)(\d)", name)
    return 440.0 * 2 ** ((NOTE[m.group(1)] + 12 * (int(m.group(2)) + 1) - 69) / 12)


# ---------- sound effects ----------
def sfx_splash(size=1.0):
    d = 0.9
    n = noise(d)
    body = bp(n, 300, 5000) * np.exp(-t_arr(d) * 6)
    hiss = hp(noise(d), 3000) * np.exp(-t_arr(d) * 9) * 0.4
    y = body + hiss
    bloop = sweep(700, 180, 0.18) * np.exp(-t_arr(0.18) * 10)
    y[:len(bloop)] += bloop * 0.9
    for k in range(6):
        st = int((0.15 + rng.random() * 0.5) * SR)
        bub = sweep(500 + rng.random() * 900, 1500 + rng.random() * 1000, 0.05) * np.hanning(int(0.05 * SR))
        y[st:st + len(bub)] += bub * 0.35
    return norm(y, 0.85 * size)

def sfx_ding(note="C6"):
    f = hz(note)
    t = t_arr(1.0)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.4 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 12) \
        + 0.15 * np.sin(2 * np.pi * f * 9.1 * t) * np.exp(-t * 25)
    return norm(y, 0.6)

def sfx_pop():
    y = sweep(350, 1400, 0.07) * np.hanning(int(0.07 * SR))
    return norm(np.concatenate([y, np.zeros(1000)]), 0.6)

def sfx_boing():
    t = t_arr(0.55)
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4) + 140 * t
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    return norm(y, 0.55)

def sfx_zoom():
    d = 0.4
    n = noise(d)
    out = np.zeros_like(n)
    seg = len(n) // 8
    for k in range(8):
        f = 600 * 1.4 ** k
        out[k * seg:(k + 1) * seg] = bp(n, f, f * 2)[k * seg:(k + 1) * seg]
    y = out * np.sin(np.linspace(0, np.pi, len(out))) + 0.3 * sweep(400, 2400, d) * np.sin(np.linspace(0, np.pi, len(out)))
    return norm(y, 0.5)

def sfx_creak():
    d = 0.8
    t = t_arr(d)
    saw = sweep(70, 95, d, "saw")
    am = (np.sin(2 * np.pi * 23 * t) > 0.3).astype(float) * 0.7 + 0.3
    creak = lp(saw * am, 900) * np.sin(np.linspace(0, np.pi, len(t)))
    tuba = sum(np.sin(2 * np.pi * hz("F2") * k * t) / k for k in range(1, 5)) * env_adsr(len(t), 0.05, 0.2, 0.7, 0.3)
    return norm(creak * 0.5 + tuba * 0.6, 0.55)

def sfx_cape():
    d = 0.45
    t = t_arr(d)
    y = lp(noise(d), 1500) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)) * np.sin(np.linspace(0, np.pi, len(t)))
    return norm(y, 0.45)

def sfx_gasp():
    d = 0.42
    y = bp(noise(d), 900, 3500) * np.linspace(0.2, 1, int(d * SR)) ** 2 * np.hanning(int(d * SR)) ** 0.3
    sp = sfx_sparkle() * 0.6
    out = np.zeros(int(1.0 * SR))
    out[:len(y)] += y
    out[int(0.3 * SR):int(0.3 * SR) + len(sp)] += sp[:len(out) - int(0.3 * SR)]
    return norm(out, 0.5)

def sfx_sparkle():
    out = np.zeros(int(0.8 * SR))
    for k in range(7):
        st = int(k * 0.07 * SR)
        f = hz(["C7", "E7", "G7", "B6", "D7", "G7", "C8"][k])
        t = t_arr(0.3)
        tone = np.sin(2 * np.pi * f * t) * np.exp(-t * 14)
        out[st:st + len(tone)] += tone[:len(out) - st]
    return norm(out, 0.4)

def sfx_heartbeat():
    out = np.zeros(int(0.9 * SR))
    for st in (0.0, 0.22):
        t = t_arr(0.18)
        th = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 22)
        i = int(st * SR)
        out[i:i + len(th)] += th
    return norm(out, 0.6)

def brass(notes, beat=0.18, gain=0.7):
    out = []
    for nm, b in notes:
        d = b * beat
        t = t_arr(d)
        f = hz(nm)
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        saw = sum(np.sin(ph * k) / k for k in range(1, 9))
        saw += 0.6 * sum(np.sin(ph * 1.005 * k) / k for k in range(1, 9))
        out.append(lp(saw, 2600) * env_adsr(len(t), 0.03, 0.08, 0.8, min(0.08, d / 3)))
    return norm(np.concatenate(out), gain)

def sfx_hero():
    return brass([("G4", 1), ("C5", 1), ("E5", 1), ("G5", 4)], beat=0.12, gain=0.6)

def sfx_tada():
    a = brass([("C5", 1)], beat=0.14)
    chord = sum(brass([(n, 8)], beat=0.14) for n in ("C5", "E5", "G5", "C6"))
    return norm(np.concatenate([a, np.zeros(int(0.04 * SR)), chord]), 0.65)

def sfx_buzz(d=0.6):
    t = t_arr(d)
    y = lp(np.sign(np.sin(2 * np.pi * 210 * t)), 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * np.sin(np.linspace(0, np.pi, len(t)))
    return norm(y, 0.22)

def sfx_swirl(d=3.0):
    t = t_arr(d)
    f = 300 + 80 * np.sin(2 * np.pi * 1.5 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bp(noise(d), 200, 900) * 0.5
    return norm(y * np.minimum(1, np.minimum(t * 3, (d - t) * 3)), 0.25)

def sfx_badge():
    ting = sfx_ding("E7")
    t = t_arr(1.4)
    choir = sum(np.sin(2 * np.pi * hz(n) * t * (1 + 0.003 * np.sin(2 * np.pi * 5 * t + k))) for k, n in enumerate(["C5", "E5", "G5", "C6"]))
    choir = lp(choir, 1800) * env_adsr(len(t), 0.2, 0.2, 0.8, 0.5)
    out = np.zeros(len(t))
    out[:len(ting)] += ting
    out += choir * 0.25
    return norm(out, 0.6)

def sfx_drumroll(d=1.6):
    t = t_arr(d)
    hits = (np.sin(2 * np.pi * 24 * t) > 0.6).astype(float)
    y = bp(noise(d), 200, 4000) * lp(hits, 300) * np.linspace(0.4, 1, len(t))
    return norm(y, 0.45)

def sfx_whoomp():
    d = 0.8
    y = lp(noise(d), 300) * np.sin(np.linspace(0, np.pi, int(d * SR)))
    return norm(y, 0.5)

def sfx_squelch():
    d = 0.22
    y = lp(noise(d), 1200) * np.exp(-t_arr(d) * 14) + 0.5 * sweep(500, 140, d) * np.exp(-t_arr(d) * 12)
    return norm(y, 0.4)

def sfx_bonk():
    t = t_arr(0.35)
    y = np.sin(2 * np.pi * 220 * t) * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 550 * t) * np.exp(-t * 30)
    return norm(y, 0.55)

def sfx_wahwah():
    a = brass([("D4", 3), ("C#4", 3), ("C4", 8)], beat=0.12, gain=0.45)
    t = np.arange(len(a)) / SR
    return norm(a * (0.7 + 0.3 * np.sin(2 * np.pi * 5 * t)), 0.4)

def sfx_whistle_up(d=1.0):
    t = t_arr(d)
    y = sweep(500, 1800, d) * np.sin(np.linspace(0, np.pi / 2, len(t))) * 0.6
    return norm(y, 0.35)

def sfx_chirp():
    out = np.zeros(int(0.8 * SR))
    for k, st in enumerate((0.0, 0.15, 0.45)):
        c = sweep(2500, 4200, 0.08) * np.hanning(int(0.08 * SR))
        i = int(st * SR)
        out[i:i + len(c)] += c
    return norm(out, 0.18)

def sfx_choir():
    t = t_arr(2.4)
    ch = sum(np.sin(2 * np.pi * hz(n) * t * (1 + 0.004 * np.sin(2 * np.pi * 5 * t + k))) for k, n in enumerate(["C5", "G5", "E6"]))
    return norm(lp(ch, 2000) * env_adsr(len(t), 0.4, 0.2, 0.8, 0.8), 0.3)

def sfx_cheer():
    """Small kids' 'yay' crowd made of filtered noise bursts and pitched vowels."""
    d = 1.6
    t = t_arr(d)
    y = bp(noise(d), 600, 3500) * env_adsr(len(t), 0.1, 0.3, 0.6, 0.8) * 0.5
    for k in range(10):
        f0 = 380 + rng.random() * 300
        st = rng.random() * 0.3
        tt = t_arr(0.8)
        f = f0 * (1 + 0.25 * np.sin(np.linspace(0, np.pi, len(tt))))
        v = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in range(1, 6))
        v = bp(v, 500, 3000) * np.hanning(len(tt))
        i = int(st * SR)
        y[i:i + len(v)] += v * 0.25
    return norm(y, 0.35)

def rain_bed(d, heavy=False):
    n = noise(d)
    y = lp(n, 5000 if heavy else 3500) * (0.5 if heavy else 0.25)
    y = hp(y, 400)
    drops = np.zeros(len(n))
    k = int(d * (60 if heavy else 25))
    for _ in range(k):
        i = rng.integers(0, len(n) - 800)
        drops[i:i + 400] += np.sin(2 * np.pi * (1500 + rng.random() * 2500) * t_arr(400 / SR)) * np.exp(-t_arr(400 / SR) * 120) * 0.4
    if heavy:
        y += lp(noise(d), 120) * 0.25
    return (y + drops).astype(np.float32) * 0.5

SFX = {
    "splash": lambda: sfx_splash(), "splash_small": lambda: sfx_splash(0.6),
    "pop": sfx_pop, "boing": sfx_boing, "zoom": sfx_zoom, "creak": sfx_creak, "cape": sfx_cape,
    "gasp": sfx_gasp, "sparkle": sfx_sparkle, "heartbeat": sfx_heartbeat, "hero": sfx_hero, "tada": sfx_tada,
    "buzz": sfx_buzz, "swirl": sfx_swirl, "badge": sfx_badge, "drumroll": sfx_drumroll, "whoomp": sfx_whoomp,
    "squelch": sfx_squelch, "bonk": sfx_bonk, "wahwah": sfx_wahwah, "whistle": sfx_whistle_up, "chirp": sfx_chirp,
    "choir": sfx_choir, "cheer": sfx_cheer,
}
for i, n in enumerate(["C6", "D6", "E6", "F6", "G6", "A6", "B6", "C7"]):
    SFX[f"ding{i + 1}"] = (lambda n=n: sfx_ding(n))
SFX["ding"] = lambda: sfx_ding("G6")

_sfx_cache = {}

def get_sfx(name):
    if name not in _sfx_cache:
        _sfx_cache[name] = SFX[name]()
    return _sfx_cache[name]


# ---------- music ----------
def ks_pluck(f, d, decay=0.996, bright=0.5):
    n = int(d * SR)
    p = max(int(SR / f), 2)
    buf = rng.uniform(-1, 1, p)
    buf = lp(buf, 2000 + 6000 * bright, 1)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out

_pluck_cache = {}

def pluck(note, d=1.0, decay=0.996, bright=0.5):
    k = (note, d, decay, bright)
    if k not in _pluck_cache:
        _pluck_cache[k] = ks_pluck(hz(note), d, decay, bright)
    return _pluck_cache[k]

def tone(note, d, kind="tri", a=0.01, r=0.08, vib=0.0):
    t = t_arr(d)
    f = hz(note) * (1 + vib * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == "tri":
        y = 2 / np.pi * np.arcsin(np.sin(ph))
    elif kind == "glock":
        y = np.sin(ph) * np.exp(-t * 3) + 0.3 * np.sin(ph * 2.76) * np.exp(-t * 8)
        return y
    elif kind == "piano":
        y = sum(np.sin(ph * k) * (0.6 ** k) for k in range(1, 6)) * np.exp(-t * 2.2)
        return y * env_adsr(len(t), 0.005, 0.1, 1.0, 0.05)
    elif kind == "pad":
        y = sum(np.sin(ph * k * (1 + 0.003 * j)) / k for k in range(1, 6) for j in (-1, 1))
        y = lp(y, 1400)
    else:
        y = np.sin(ph)
    return y * env_adsr(len(t), a, 0.05, 0.85, r)

def clap(d=0.2):
    y = bp(noise(d), 800, 3000) * np.exp(-t_arr(d) * 30)
    return y * 0.6

def snare(d=0.2):
    t = t_arr(d)
    return (bp(noise(d), 1500, 7000) * np.exp(-t * 25) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5)

def kick(d=0.25):
    t = t_arr(d)
    f = 120 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)

def woodblock():
    t = t_arr(0.12)
    return np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) * 0.5

THEME_MEL = [("C5", 1), ("E5", 1), ("G5", 1), ("E5", 1), ("F5", 1), ("A5", 1), ("G5", 2),
             ("E5", .5), ("E5", .5), ("D5", .5), ("C5", .5), ("D5", 1), ("E5", 1), ("D5", 2), ("G4", 2),
             ("C5", 1), ("E5", 1), ("G5", 1), ("C6", 1), ("A5", 1), ("F5", 1), ("G5", 2),
             ("E5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("C5", 1), ("D5", 1), ("C5", 3), ("R", 1)]
THEME_CH = ["C", "F", "C", "G", "C", "F", "G", "C"]
CHORDS = {"C": ["C4", "E4", "G4"], "F": ["F3", "A3", "C4"], "G": ["G3", "B3", "D4"], "Am": ["A3", "C4", "E4"]}
BASS = {"C": "C3", "F": "F2", "G": "G2", "Am": "A2"}

def put(buf, x, t):
    i = int(t * SR)
    if i < 0:
        x, i = x[-i:], 0
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]

def music(style, dur):
    """Loop a style for dur seconds."""
    buf = np.zeros(int(dur * SR) + SR)
    if style in ("theme", "rescue", "hero"):
        bpm = {"theme": 120, "rescue": 132, "hero": 124}[style]
        beat = 60 / bpm
        bar = beat * 4
        loop = bar * 8
        t0 = 0.0
        while t0 < dur:
            # melody
            tt = t0
            for nm, b in THEME_MEL:
                if nm != "R":
                    if style == "hero":
                        x = brass([(nm, b)], beat=beat, gain=0.32)
                    else:
                        x = tone(nm, b * beat * 0.95, "tri", vib=0.006) * 0.22
                        x = x + 0.08 * tone(nm, b * beat * 0.95, "glock")
                    put(buf, x, tt)
                tt += b * beat
            for bi, ch in enumerate(THEME_CH):
                bt = t0 + bi * bar
                for k in range(4):
                    # strum (uke) on each beat, offbeat lighter
                    for j, n in enumerate(CHORDS[ch]):
                        put(buf, pluck(n, 0.6, 0.994) * (0.16 if k % 2 == 0 else 0.11), bt + k * beat + j * 0.012)
                    if style != "theme":
                        for j, n in enumerate(CHORDS[ch]):
                            put(buf, pluck(n, 0.3, 0.99) * 0.07, bt + k * beat + beat / 2 + j * 0.01)
                    # bass
                    if k in (0, 2):
                        put(buf, tone(BASS[ch], beat * 0.9, "sin") * 0.3, bt + k * beat)
                    # percussion
                    if style == "theme":
                        if k in (1, 3):
                            put(buf, clap(), bt + k * beat)
                    else:
                        put(buf, kick() * 0.5, bt + k * beat) if k in (0, 2) else put(buf, snare() * 0.5, bt + k * beat)
                        if style == "hero":
                            put(buf, snare() * 0.2, bt + k * beat + beat / 2)
            t0 += loop
    elif style == "search":
        beat = 60 / 104
        pat = ["C4", "G4", "E4", "G4", "C4", "G4", "E4", "G4", "B3", "G4", "D4", "G4", "B3", "G4", "D4", "F4",
               "A3", "E4", "C4", "E4", "A3", "E4", "C4", "E4", "G3", "D4", "B3", "D4", "G3", "B3", "D4", "G4"]
        t0 = 0.0
        i = 0
        while t0 < dur:
            n = pat[i % len(pat)]
            put(buf, pluck(n, 0.25, 0.985, 0.3) * 0.32, t0)
            if i % 4 == 0:
                put(buf, woodblock() * 0.5, t0)
            if i % 8 == 2:
                put(buf, tone(n.replace("3", "5").replace("4", "5"), 0.3, "glock") * 0.12, t0)
            t0 += beat / 2
            i += 1
    elif style == "brave":
        beat = 60 / 68
        prog = ["C", "Am", "F", "G"]
        t0 = 0.0
        k = 0
        while t0 < dur:
            ch = prog[k % 4]
            notes = CHORDS[ch] + [CHORDS[ch][0].replace("3", "4").replace("4", "5")]
            for j, n in enumerate(notes):
                put(buf, tone(n, beat * 2, "piano") * 0.22, t0 + j * beat)
            swell = min(1.0, t0 / max(dur, 1))
            pad = sum(tone(n, beat * 4, "pad", a=1.0, r=0.6) for n in CHORDS[ch]) * 0.03 * (0.3 + swell)
            put(buf, pad, t0)
            t0 += beat * 4
            k += 1
    elif style == "rainbow":
        beat = 60 / 92
        t0 = 0.0
        while t0 < dur:
            tt = t0
            for nm, b in THEME_MEL:
                if nm != "R":
                    put(buf, tone(nm, b * beat * 1.5, "glock") * 0.22, tt)
                tt += b * beat
            for bi, ch in enumerate(THEME_CH):
                pad = sum(tone(n, beat * 4, "pad", a=0.4, r=0.5) for n in CHORDS[ch]) * 0.03
                put(buf, pad, t0 + bi * beat * 4)
                put(buf, tone(BASS[ch], beat * 3.5, "sin") * 0.2, t0 + bi * beat * 4)
            t0 += beat * 32
    elif style == "tension":
        beat = 60 / 112
        t0 = 0.0
        i = 0
        while t0 < dur:
            n = ["C4", "D#4", "G4", "D#4"][i % 4]
            put(buf, pluck(n, 0.25, 0.985, 0.4) * 0.25, t0)
            if i % 2 == 0:
                put(buf, kick() * 0.25, t0)
            t0 += beat / 2
            i += 1
    y = buf[:int(dur * SR)]
    fade = int(0.4 * SR)
    if len(y) > 2 * fade:
        y[:fade] *= np.linspace(0, 1, fade)
        y[-fade:] *= np.linspace(1, 0, fade)
    return y.astype(np.float32)
