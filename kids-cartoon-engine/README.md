# Kids Cartoon Engine

Free, code-animated kids episodes. No paid tools.

- `pip/`: shared drawing kit, sound effects, music, scene timing and renderer. Also Pip & the Puddle Patrol, Episode 1.
- `biscuit/`: Biscuit & Friends characters, episode script (`show.py`), voice pipeline and process notes (`PROCESS.md`).
- `whats-that-sound/`: final edit for What's That Sound? (`build_final.py`). It cuts AI-generated clips, voice lines and a music bed into one episode. Process notes are in `whats-that-sound/PROCESS.md` at the repo root.

## Setup on a fresh machine

```
pip install skia-python numpy scipy soundfile kokoro-onnx edge-tts
python3 -m venv cbx && cbx/bin/pip install chatterbox-tts faster-whisper
```

Then follow `biscuit/PROCESS.md`.
