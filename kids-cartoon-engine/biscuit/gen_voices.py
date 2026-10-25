"""Voice every line in todo.json with Chatterbox Turbo (run with the cbx venv python)."""
import json, os, time
import numpy as np
import soundfile as sf
import torch
import librosa, re
from difflib import SequenceMatcher
from chatterbox.tts_turbo import ChatterboxTurboTTS
from faster_whisper import WhisperModel

NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "too": "two", "to": "two"}

def words(s):
    s = re.sub(r"\[[a-z]+\]", "", s.lower()).replace("-", " ")
    return [NUM.get(w, w) for w in re.sub(r"[^a-z0-9 ]", "", s).split()]

def score(want, got):
    return SequenceMatcher(None, words(want), words(got)).ratio()

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = {w: os.path.join(HERE, "vs", f"ref_{w}.wav") for w in ("biscuit", "mittens", "prickles", "narr")}
SR = 44100

torch.set_num_threads(4)
todo = json.load(open(os.path.join(HERE, "todo.json")))
print(f"{len(todo)} lines to voice", flush=True)
m = ChatterboxTurboTTS.from_pretrained(device="cpu")
asr = WhisperModel("small.en", device="cpu", compute_type="int8")
for i, item in enumerate(todo):
    t0 = time.time()
    best, best_r = None, -1
    for attempt in range(6):
        torch.manual_seed(1234 + i + 97 * attempt)
        w = m.generate(item["text"], audio_prompt_path=REFS[item["who"]], norm_loudness=False)
        y = w.squeeze(0).numpy().astype(np.float32)
        got = " ".join(s.text for s in asr.transcribe(librosa.resample(y, orig_sr=m.sr, target_sr=16000))[0])
        r = score(item["text"], got)
        if r > best_r:
            best, best_r = y, r
        if r >= 0.8:
            break
    y = librosa.resample(best, orig_sr=m.sr, target_sr=SR)
    nz = np.where(np.abs(y) > 0.02)[0]
    if len(nz):
        y = y[max(nz[0] - 600, 0): nz[-1] + 3000]
    y = y / (np.max(np.abs(y)) + 1e-6) * 0.9
    sf.write(item["path"], y, SR)
    print(f"  {i + 1}/{len(todo)} {item['who']:8s} {time.time() - t0:4.1f}s  match {best_r:.2f}  {item['text'][:50]}", flush=True)
print("done", flush=True)
