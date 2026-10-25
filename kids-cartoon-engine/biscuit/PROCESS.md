# Kids Cartoon Process ($0 per episode)

One person, one session, no paid tools. Claude does every step.

## 1. Script (10 min)
- One problem, one plan, one payoff. Say each out loud in the script.
- One running joke that builds (Prickles: things stick to his spikes).
- A secret the kids can see and the characters can't. It gives them something to shout.
- A "kids' turn" every 30 to 40 seconds: shout yes or no, count, point, tell them.
- Read every line aloud. Cut anything a 2-year-old can't follow.
- Only short lines like "Ready!" or counting are spoken together, and they're synced.

## 2. Voices (free, about 10 min)
- Engine: Chatterbox Turbo, open source, running locally. MIT license, so commercial use is fine.
- Each character has a short reference clip (`vs/ref_<name>.wav`) that sets their voice.
- Emotion comes from cues in the line: `[laugh]`, `[chuckle]`, `[sigh]`, `[gasp]`.
- Commands:
  1. `python3 render.py collect` lists every missing line.
  2. `../cbx/bin/python gen_voices.py` voices them all.
- Check: transcribe the voice track and fix any line that comes out garbled.

## 3. Characters and world (free)
- Drawn in code (`chars.py`), so they look identical in every shot.
- Render a test still before animating anything.

## 4. Animation (free, about 5 min to render)
- `show.py`: each scene is a list of lines, sound effects and marks. Visuals key off the marks, so timing follows the voices automatically.
- Contact sheet first (`python3 render.py sheet`), then fix overlaps and framing.
- Full render: `python3 render.py full out.mp4`. That's 1080p, 24 fps, with loudness set to YouTube's standard.

## 5. Optional hero shots (Flow, about 10 credits each)
- Only for 1 or 2 big moments. The free daily Flow credits usually cover them.

## 6. Ship
- Push the MP4 and script to GitHub. Upload to YouTube with "Made for Kids" on.

## Reuse for the next episode
Keep `chars.py`, the voice refs, the sound kit and the music. A new episode only needs a new script and a new `show.py`.
