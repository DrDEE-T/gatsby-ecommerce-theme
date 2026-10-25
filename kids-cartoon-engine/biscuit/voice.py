"""Voice cache for Chatterbox Turbo lines.

speak() returns a cached line, or records it as missing and returns placeholder silence.
Run gen_voices.py (in the cbx venv) to voice everything that is missing, then build again.
"""
import hashlib, json, os
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "vcache")
TODO = os.path.join(HERE, "todo.json")
SR = 44100
missing = []


def key(who, text):
    return hashlib.md5(f"turbo1|{who}|{text}".encode()).hexdigest()


def path_for(who, text):
    return os.path.join(CACHE, f"{who}_{key(who, text)}.wav")


def speak(who, text):
    p = path_for(who, text)
    if os.path.exists(p):
        y, _ = sf.read(p, dtype="float32")
        return y
    missing.append({"who": who, "text": text, "path": p})
    return np.zeros(int((0.6 + 0.065 * len(text)) * SR), np.float32)


def write_todo():
    seen, out = set(), []
    for m in missing:
        if m["path"] not in seen:
            seen.add(m["path"])
            out.append(m)
    with open(TODO, "w") as f:
        json.dump(out, f, indent=1)
    return len(out)
