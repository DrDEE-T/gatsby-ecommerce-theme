# Biscuit & Friends: audit against the CoComelon / Baby Shark research

| Rule | Episode 1: Where's the Red Ball? | Episode 2: Bubble Bath Time! |
|---|---|---|
| Problem stated in the first 15 seconds | Secret shown at about 5s. Biscuit says the ball is gone at about 22s, after a 3s title. Close enough, since the secret is the hook. | Mud at about 5s, "Baths are scary" at about 13s. Passes. |
| One problem, one plan, one solution | Lost ball, three-place search, ball pops off Prickles | Scared of the bath, five steps, clean and happy |
| Calm ending | Group hug, "Best ball day ever" | Towel, hug, "Bath time, then bedtime" |
| Length 2 to 4 minutes | 3:23 | 2:19 (extended from 1:49 with a step count, a fourth scrub and a recap chant) |
| Repeating hook with a one-word swap and an action | "Is it in the bucket / grass / tree? No, no, no!" | "Scrub your tummy / ears / paws / tail!" with scrubbing, plus the "Water! Bubbles! Scrub! Rinse! Dry!" recap chant said twice |
| Nonsense words only on the beat | None used | None used |
| Shots held 3 to 6 seconds, gentle zooms | Yes | Yes |
| Quiet at kids' turns, then show the answer | Music drops under every kids' turn (fixed in this audit) | Same |
| One signature sound per character | Biscuit: tail-wag "fwip-fwip" (added in this audit). Mittens: mrrp. Prickles: roll and pok. | Same |
| Routine or familiar theme | Lost toy | Bath time |
| Thumbnail: big face plus the object, few words | thumb-ep1.png | thumb-ep2.png |

## Known gaps
- No sung songs yet. The free voice engine can't sing, so the hooks are chanted over the music. A real sung theme would need a singing voice model or a recorded singer.
- Shorts and compilations are planned: a 10-minute compilation after Episode 3, and 1 or 2 vertical Shorts per episode.

## Independent parent/child audit, and the fixes made

| Finding | Fix |
|---|---|
| Ep 1, 2:43: the laugh cue before "That's okay!" could sound like a swear word | All episodes re-voiced with the approved Edge voices. Every [laugh]/[sigh]/[gasp] cue was removed; emotion now comes from pace and pitch. Every line was transcribed and scanned for rude-sounding words: none found. |
| Other emotion cues came out as odd sounds ("Oh no" heard as "Huh, I know") | Same fix |
| Ep 3 ended in the morning with an upbeat song, which spoils bedtime | Now ends at night: "Goodnight, friends. Sweet dreams!" with a calm night end card. The morning gag lives in Short 3. |
| Ep 2 bath song was 75 seconds and static | Cut to the 24-second excerpt, shown close up in the yard |
| Kids' turns were too short (about 2 seconds) | 3 to 3.6 seconds, with the music dropped underneath |
| 30-second theme outro on every episode | Cut to 12 seconds |
| "Oopsie-prickle" overused | About 3 per episode |
| No grown-up mentioned in the bath episode | "With a grown-up, fill the tub with warm water." |
| Confusing Ep 2 closing line | Mittens: "Now it's almost bedtime." |
| Shorts framing too wide; overlap in Short 2; 5 seconds of dead air in Short 3 | Closer framing, overlap fixed, dead air cut to 1.6 seconds with a sunrise cue |

## Second independent audit, and the fixes made

| Finding | Fix |
|---|---|
| Ep 2 still played the full 31-second theme, with mouths moving to the singer | Uses the 12-second outro like Ep 1 and Ep 3; mouths closed while the singer sings |
| Ep 1 "Psst. Friends" could be heard as a rude word | Now "Hey, friends! Did you see something red?" |
| Ep 2 song badges covered Biscuit's face | Badges moved to the top-right corner |
| Some kids' turns still short ("Can you scrub/brush with Biscuit?", "Is Biscuit clean yet?") | 3 to 3.5 seconds |
| Ep 3 had no "Oopsie-prickle" and a bright yellow wipe | Catchphrase added; soft bubble transition instead |
| Unclear words ("Shh" heard as "Shoo", "Minty fresh" as "Minty flesh", "super finders" as "super fine girls") | "Shh" lines reworded, "Minty clean!", "super helpers" |
| Shorts loosely framed, Mittens clipped, Prickles overlapping Biscuit | Characters raised to mid-frame, spacing fixed |
| Short 3 quieter than the others | Volume raised to match |

Final safety check: every video's full audio transcribed with two speech models (medium.en and small.en). No rude-sounding words in any video.
