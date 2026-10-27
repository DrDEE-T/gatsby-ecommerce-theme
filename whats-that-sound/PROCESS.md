# What's That Sound? Process

A kids series where two sisters hear an animal sound, guess, and learn the animal's name and one fact. Short vertical episodes, posted as YouTube Shorts.

This file is the handoff. Any assistant (Claude or ChatGPT) can pick up the next episode from here.

## The format
- Open on a sound. The little sister asks "What was that?" or "Who's that?"
- Reveal the animal and say its name clearly.
- Lizzie gives one simple fact, one short sentence.
- 4 or 5 animals per episode, 35 to 45 seconds total.
- No gap longer than 2 seconds. A soft music bed runs under the dialogue.
- End with "Bye, [place] animals!" and an end card saying visuals and voices are AI-generated.

## Characters
- Lizzie (older sister): long curly brown hair, purple bow, lavender t-shirt, denim shorts, white socks and sneakers.
- Little sister (toddler): shorter curly brown hair, yellow bow, peach t-shirt, mint green shorts, white socks and sneakers.
- 3D animated style. Toddlers have tiny baby teeth and mostly closed-mouth smiles. Check faces up close before animating anything.
- Saved in Higgsfield as the reference element "Lizzie-and-Sister".
- Voices: cloned from the pilot audio with Higgsfield Seed Audio (0.2 credits per line).

## Animals
- Realistic, nature-documentary look, in the same frame and the same light as the girls.
- Keep them true to life: a whale breaches in deep water past the end of a pier, not off a shallow beach.

## Cost rules
- Cheapest route that still looks smooth.
- Hard ceiling: 150 Runway credits per episode. Anything above that needs the owner's approval first.
- Quote the cost before generating. Run one test clip before batching.
- Veo 3.1 on Runway costs 40 credits per second. Episode 2 used it for every shot (1,295 credits). Don't repeat that.
- The cheaper route: keyframes and voices on Higgsfield's free credits, camera moves on stills for quiet shots, one low-cost video model for action shots, or the $0 code-animated engine in `kids-cartoon-engine/` (see `biscuit-and-friends/PROCESS.md`).

## Steps
1. Script: 4 or 5 animals, one name and one fact each. Read it aloud.
2. Keyframes: one image per shot with the "Lizzie-and-Sister" element, 9:16.
3. Voices: one line per call, cloned from the pilot voices.
4. Motion: cheapest option per shot (see cost rules).
5. Edit: `kids-cartoon-engine/whats-that-sound/build_final.py <folder>`. It expects `c1.mp4` to `c5.mp4`, `v1.mp3` to `v8.mp3` and `music.mp3`. It sizes each shot to its dialogue, mixes the animal sounds, and ducks the music under speech.
6. Check: transcribe the final audio, look at a frame grid, and check faces and teeth.
7. Thumbnail: a 1280x720 frame with big "WHAT'S THAT SOUND?" text and no open-mouth faces.
8. Ship: push the MP4, thumbnail and script here, then upload to YouTube with "Made for kids" and "Altered or synthetic content" both set to Yes.

## Episodes
- Ep 1: At the Zoo (pilot, made outside this repo)
- Ep 2: At the Ocean, `Whats-That-Sound-Ep2-Ocean.mp4`. Script and YouTube copy are in `ep2-ocean.md`.
