# Kids Cartoon Engine

Free, code-animated kids episodes. No paid tools.

- `pip/`: shared drawing kit, sound effects, music, scene timing and renderer. Also Pip & the Puddle Patrol, Episode 1.
- `biscuit/`: Biscuit & Friends characters, episode script (`show.py`), voice pipeline and process notes (`PROCESS.md`).

## Setup on a fresh machine

```
pip install skia-python numpy scipy soundfile kokoro-onnx edge-tts
python3 -m venv cbx && cbx/bin/pip install chatterbox-tts faster-whisper
```

Then follow `biscuit/PROCESS.md`.
