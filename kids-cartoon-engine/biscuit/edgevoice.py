"""Approved free Edge voices for Biscuit & Friends, with mood from pace and pitch (no [laugh]/[sigh] cues:
the audit found those turn into odd, sometimes rude-sounding syllables)."""
import hashlib, os, re, subprocess
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ECACHE = os.path.join(HERE, "ecache")
os.makedirs(ECACHE, exist_ok=True)

# who -> (voice, base rate %, base pitch Hz)
CAST = {"biscuit": ("en-US-AnaNeural", 0, 0), "mittens": ("en-GB-SoniaNeural", -5, 0),
        "prickles": ("en-US-RogerNeural", 5, 12), "narr": ("en-US-EmmaNeural", -5, 0)}
# mood -> (rate %, pitch Hz, volume %)
MOODS = {"happy": (8, 10, 0), "excited": (15, 18, 10), "sleepy": (-22, -10, -15), "sad": (-15, -8, -10),
         "calm": (-8, -2, 0), "": (0, 0, 0)}
TAG_MOOD = {"laugh": "happy", "chuckle": "happy", "gasp": "excited", "sigh": "sad"}


def speak_mood(who, text, mood=""):
    voice, br, bp = CAST[who]
    r, p, v = MOODS[mood]
    key = hashlib.md5(f"e2|{who}|{mood}|{text}".encode()).hexdigest()
    wav = os.path.join(ECACHE, f"{who}_{key}.wav")
    if not os.path.exists(wav):
        mp3 = wav + ".mp3"
        env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
        cmd = ["edge-tts", "--voice", voice, f"--rate={br + r:+d}%", f"--pitch={bp + p:+d}Hz", f"--volume={v:+d}%",
               "--text", text, "--write-media", mp3]
        if os.environ.get("HTTPS_PROXY"):
            cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
        for _ in range(4):
            if subprocess.run(cmd, env=env, capture_output=True).returncode == 0 and os.path.getsize(mp3) > 1000:
                break
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav], check=True)
        os.remove(mp3)
        y, _ = sf.read(wav, dtype="float32")
        nz = np.where(np.abs(y) > 0.01)[0]
        if len(nz):
            y = y[max(nz[0] - 400, 0): nz[-1] + 2500]
        sf.write(wav, y / (np.abs(y).max() + 1e-6) * 0.9, SR)
    y, _ = sf.read(wav, dtype="float32")
    return y


def speak(who, text):
    """Drop-in for the episode engine: [laugh]-style cues become a mood, never a sound."""
    tags = re.findall(r"\[([a-z]+)\]", text)
    mood = next((TAG_MOOD[t] for t in tags if t in TAG_MOOD), "")
    clean = re.sub(r"\s*\[[a-z]+\]\s*", " ", text).strip()
    if who == "biscuit" and "sleepy" in clean.lower():
        mood = "sleepy"
    return speak_mood(who, clean, mood)
