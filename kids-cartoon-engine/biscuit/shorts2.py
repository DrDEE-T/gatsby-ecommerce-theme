"""Biscuit & Friends Shorts, v2: song-first, hook in the first second, constant movement.
Shorts A and B use only the sung songs. Short C uses a few lines in the approved Edge voices."""
import hashlib, math, os, subprocess
import numpy as np
import soundfile as sf
from shorts import *  # noqa: F401,F403  (vcam, vtitle, vprompt, end_card, shared kit)
import shorts as SH
import audio as A

HERE2 = os.path.dirname(os.path.abspath(__file__))
ECACHE = os.path.join(HERE2, "ecache")
os.makedirs(ECACHE, exist_ok=True)

# approved free Edge voices: who -> (voice, base rate, base pitch)
EDGE_CAST = {"biscuit": ("en-US-AnaNeural", 0, 0), "mittens": ("en-GB-SoniaNeural", -5, 0),
             "prickles": ("en-US-RogerNeural", 5, 12), "narr": ("en-US-EmmaNeural", -5, 0)}
# mood -> (rate %, pitch Hz, volume %) added on top of the voice
MOODS = {"happy": (8, 10, 0), "excited": (15, 18, 10), "sleepy": (-22, -10, -15), "calm": (-8, -2, 0), "": (0, 0, 0)}


def edge_speak(who, text, mood=""):
    voice, br, bp = EDGE_CAST[who]
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
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(A.SR), "-ac", "1", wav], check=True)
        os.remove(mp3)
        y, _ = sf.read(wav, dtype="float32")
        nz = np.where(np.abs(y) > 0.01)[0]
        if len(nz):
            y = y[max(nz[0] - 400, 0): nz[-1] + 2500]
        sf.write(wav, y / (np.abs(y).max() + 1e-6) * 0.9, A.SR)
    y, _ = sf.read(wav, dtype="float32")
    return y


def esay(s, who, text, mood="", key=None, gap=0.3):
    y = edge_speak(who, text, mood)
    d = len(y) / A.SR
    s.lines.append(dict(who=who, start=s.t, end=s.t + d, y=y, env=A.envelope(y), gain=1.0))
    if key:
        s.m[key] = s.t
        s.m[key + "_end"] = s.t + d
    s.t += d + gap


def lyric_lines(c, line, k):
    """Big on-screen lyric, wrapped onto two lines when long."""
    line = line.upper()
    if len(line) > 16:
        cut = min((i for i, ch in enumerate(line) if ch == " "), key=lambda i: abs(i - len(line) / 2))
        rows = [line[:cut], line[cut + 1:]]
    else:
        rows = [line]
    for i, r in enumerate(rows):
        text(c, r, VW / 2, 160 + i * 74, 60 if len(r) <= 14 else 50, 0xFFFFD93B, ow=10, scale=back_out(k))


def burst_word(c, word, x, y, t, t0, dur=0.9, size=70, color=0xFFE8343B):
    if t0 <= t < t0 + dur:
        k = back_out((t - t0) / 0.25)
        fade = 1 - ramp(t, t0 + dur - 0.2, t0 + dur)
        c.saveLayerAlpha(None, int(255 * fade))
        burst(c, x, y, 70 * k, t, 0xFFFFE15A)
        text(c, word, x, y, size, color, scale=k, ow=10)
        c.restore()


def confetti(c, t, t0, n=40):
    if t < t0:
        return
    k = t - t0
    cols = [0xFFE8343B, 0xFFFFC21A, 0xFF3D8BFF, 0xFF6CCB5F, 0xFFFF9BD5, 0xFF8E5CF7]
    for i in range(n):
        x = hsh(i, 31) * VW
        y = -40 + k * (300 + hsh(i, 32) * 300)
        if y > VH:
            continue
        c.save(); c.translate(x + math.sin(k * 3 + i) * 30, y); c.rotate(k * 300 * (hsh(i, 33) - 0.5))
        c.drawRect(skia.Rect.MakeLTRB(-8, -4, 8, 4), fill(cols[i % 6]))
        c.restore()


# ===================================================================== Short A: theme song story
def buildA():
    s = Scene("themeA", music=None, trans=None)
    s.t = 0.05
    add_song(s, "theme.mp3", "song", gain=1.0)
    s.fx("pop", 0.05); s.fx("boing", 6.6); s.fx("roll", 8.4, 0.6); s.fx("boing", 12.6); s.fx("boing", 13.1)
    s.fx("whoosh" if "whoosh" in A.SFX else "whoomp", 19.0, 0.6); s.fx("pok", 20.2); s.fx("sparkle", 21.5); s.fx("tada", 28.0, 0.5)
    s.mark("end"); s.wait(1.6)
    BEAT = 0.5

    def d(c, t, s=s):
        if t >= s.M("end"):
            return end_card(c, t, s)
        tt = t - s.M("song")
        beat = hop(tt % BEAT, 0, BEAT, 22)
        # the song comes from an off-screen singer: mouths only open for Woof and Hooray
        woof = 0.8 if 4.0 < tt < 6.0 and (tt % 1.0) < 0.45 else 0.0
        cheer = 0.8 if tt > 28.0 else 0.0
        vcam(c, 1.85, 575, 520)
        garden(c, t, props=())
        tree(c, 745, 560, 0.72)
        # Biscuit pops up on frame 1
        bk = back_out(ramp(tt, 0.0, 0.5))
        sad = 1.0 if 12.8 < tt < 20.6 else 0.0
        jump = hop(tt, 4.0, 0.5, 70) + hop(tt, 5.0, 0.5, 70) + hop(tt, 28.0, 0.7, 140)
        bx = 540 if tt < 24 else lerp(540, 590, ease(ramp(tt, 24, 25)))
        draw_biscuit(c, bx, SY + (1 - bk) * 300 + (0 if sad else beat) + jump, 1.0, t, mouth=max(woof, cheer),
                     face=1, ears=-0.8 if sad else 0.7, wag=0.2 if sad else 1.8, sad=sad, look=(0.5, -1) if sad else (0, 0))
        # Mittens slides in, later leaps to the tree
        if tt > 6.4:
            mk = ease_out(ramp(tt, 6.4, 7.2))
            mx, my = lerp(250, 420, mk), SY
            if 18.6 < tt < 20.6:
                k = ramp(tt, 18.6, 19.6) if tt < 19.6 else 1 - ramp(tt, 19.6, 20.6)
                mx, my = lerp(420, 715, k), SY - math.sin(min(k, 1) * math.pi / 2) * 290
            if tt > 24:
                mx = lerp(420, 450, ease(ramp(tt, 24, 25)))
            draw_mittens(c, mx, my + (beat * 0.7 if not (18.6 < tt < 20.6) else 0) + hop(tt, 28.0, 0.7, 120), 0.85, t,
                         mouth=cheer, face=1, paw_up=0.5 + 0.5 * math.sin(t * 8) if tt > 24 else 0)
        # Prickles rolls in
        if tt > 8.4:
            if tt < 9.6:
                px = lerp(900, 725, ramp(tt, 8.4, 9.4))
                draw_prickles(c, px, SY, 0.9, t, roll=-(tt * 700))
            else:
                items = ["ball"] if 20.2 < tt < 22.0 else []
                px = 725 if tt < 24 else lerp(725, 745, ease(ramp(tt, 24, 25)))
                draw_prickles(c, px, SY + beat * 0.8 + hop(tt, 28.0, 0.7, 120), 0.9, t, mouth=cheer, face=-1,
                              items=items, sparkle=1.0 if items else 0, look=(-1, -0.6) if 12.8 < tt < 20.2 else (-1, 0))
        # the ball: bounced up into the tree (problem), knocked down (help), lands on spikes, back to Biscuit
        if 12.4 < tt < 20.2:
            if tt < 13.2:
                k = ramp(tt, 12.4, 13.2)
                bpos = (lerp(620, 735, k), lerp(600, 395, k) - math.sin(k * math.pi) * 120)
            elif tt < 19.6:
                bpos = (735 + math.sin(tt * 6) * 3, 395)
            else:
                k = ramp(tt, 19.6, 20.2)
                bpos = (lerp(735, 660, k), lerp(395, 600, k * k))
            stuck_item(c, "ball", bpos[0], bpos[1], 1.3, 0, t, sparkle=1.0 if tt > 13.2 else 0)
        elif 22.0 < tt:
            k = ramp(tt, 22.0, 22.8)
            stuck_item(c, "ball", lerp(650, 620, k), 620 - math.sin(k * math.pi) * 100 + (beat if tt > 22.8 else 0), 1.3, 0, t)
        c.restore()
        confetti(c, t, s.M("song") + 28.0)
        burst_word(c, "WOOF!", 220, 560, tt, 4.0, 0.8)
        burst_word(c, "WOOF!", 500, 500, tt, 5.0, 0.8)
        burst_word(c, "UH OH!", VW / 2, 470, tt, 13.3, 1.4, 60, 0xFF3D8BFF)
        for i, (st, line) in enumerate(SH.THEME_LYRICS if hasattr(SH, "THEME_LYRICS") else THEME_LYRICS):
            en = (SH.THEME_LYRICS if hasattr(SH, "THEME_LYRICS") else THEME_LYRICS)[i + 1][0] if i + 1 < len(THEME_LYRICS) else 30.5
            if st <= tt < en:
                lyric_lines(c, line, (tt - st) / 0.3)
    s.draw = d
    return [s]


# ===================================================================== Short B: bath song story
def buildB():
    s = Scene("bathB", music=None, trans=None)
    s.t = 0.05
    add_song(s, SH.bath_excerpt(), "song", gain=1.0)
    s.fx("splash", 0.35); s.fx("splash_small", 5.2); s.fx("shake" if "shake" in A.SFX else "cape", 18.0)
    s.fx("pop", 10.0, 0.6); s.fx("pop", 12.5, 0.6); s.fx("pop", 15.0, 0.6); s.fx("tada", 21.5, 0.5)
    s.mark("end"); s.wait(1.6)
    lyr = [(0.0, 4.6, "It's bath time, bath time!"), (4.6, 8.6, "Water, bubbles, scrub, rinse, dry!"),
           (8.6, 13.0, "Scrub your tummy!"), (13.0, 17.4, "Scrub, scrub, scrub!"),
           (17.4, 21.5, "All clean and fluffy!"), (21.5, 24.0, "Hooray!")]

    def d(c, t, s=s, lyr=lyr):
        if t >= s.M("end"):
            return end_card(c, t, s)
        tt = t - s.M("song")
        beat = hop(tt % 0.536, 0, 0.536, 20)
        # off-screen singer: characters only open their mouths to cheer Hooray
        cheer = 0.8 if tt > 21.5 else 0.0
        vcam(c, 1.45, 575, 480)
        garden(c, t, props=())
        # tub slides in after the mud splash
        tub_x = lerp(1000, 580, ease_out(ramp(tt, 2.0, 3.0)))
        in_tub = 5.0 < tt < 17.6
        out = tt >= 17.6
        clean = ease(ramp(tt, 8.6, 16.5))
        mud_puddle(c, 480, 668, 95, t)
        if tt > 2.0:
            tub_back(c, tub_x, 700, 0.9)
        if tt < 5.0:
            # frame 1: Biscuit leaps into the mud
            bx = lerp(560, 480, ramp(tt, 0.0, 0.35)) if tt < 0.35 else lerp(480, tub_x, ease(ramp(tt, 4.4, 5.0)))
            by = SY + 10 + hop(tt, 0.0, 0.35, 110) + hop(tt, 4.4, 0.6, 160) + (beat if 0.6 < tt < 4.4 else 0)
            draw_biscuit(c, bx, by, 1.0, t, mouth=cheer, face=1, mud=ease(ramp(tt, 0.3, 0.4)), ears=0.7, wag=1.8)
            splash_fx(c, 480, 668, s.M("song") + 0.35, t, 1.0, 0xFF8B5A2B)
        elif in_tub:
            draw_biscuit(c, tub_x + math.sin(t * 14) * 5 * (tt > 8.6), 610 + beat * 0.3, 1.0, t, mouth=cheer, face=1,
                         mud=1 - clean, ears=0.7, wag=1.6)
        if tt > 2.0:
            tub_front(c, tub_x, 700, 0.9, water=0.75, t=t, bubbles=ease(ramp(tt, 5.0, 6.0)) * (0 if out else 1))
        if out:
            k = ramp(tt, 17.6, 18.2)
            bx = lerp(tub_x, 480, ease(k))
            shaking = 18.0 < tt < 19.4
            draw_biscuit(c, bx, SY + hop(tt, 17.6, 0.6, 140) + (beat if tt > 19.4 else 0) + hop(tt, 21.5, 0.7, 120), 1.0, t,
                         mouth=cheer, face=-1, ears=0.7, wag=2.0, tilt=math.sin(t * 40) * 12 if shaking else 0,
                         blink=1.0 if shaking else None)
            if shaking:
                for i in range(14):
                    a = hsh(i, int(t * 8)) * math.tau
                    dd = 60 + ((tt - 18.0) * 400) % 220
                    circle(c, bx + math.cos(a) * dd, 560 + math.sin(a) * dd * 0.6, 6, 0xCC7FD3FF, 0)
            if tt > 19.4:
                towel(c, bx, SY + 4, 0.95)
                sparkles(c, bx, 500, t, 8, 90)
        # friends dance on the sides; Mittens gets splashed by the shake
        wet = tt > 18.3
        draw_mittens(c, 400, SY + beat * 0.7 + hop(tt, 21.5, 0.7, 110), 0.72, t, mouth=cheer, face=1,
                     lid=0.0 if 18.3 < tt < 19.6 else 0.25, paw_up=0.5 + 0.5 * math.sin(t * 9))
        if wet and tt < 21.5:
            for i in range(4):
                ph = (t * 1.2 + i / 4) % 1
                circle(c, 350 + i * 20, 540 + ph * 120, 5, 0xCC7FD3FF, 0)
        draw_prickles(c, 745, SY + beat * 0.7 + hop(tt, 21.5, 0.7, 110), 0.72, t, mouth=cheer, face=-1, look=(-1, -0.3))
        for i, tp in enumerate((10.0, 12.5, 15.0)):
            if tp - 0.8 < tt < tp + 0.3:
                k = ramp(tt, tp - 0.8, tp)
                bubble(c, lerp(600, 760, k), lerp(560, 600 - i * 15, k) - math.sin(k * math.pi) * 60, 20, t,
                       pop=0 if tt < tp else (tt - tp) / 0.3)
        c.restore()
        confetti(c, t, s.M("song") + 21.5)
        burst_word(c, "SPLASH!", VW / 2, 480, tt, 0.35, 1.0, 64, 0xFF3D8BFF)
        burst_word(c, "POP!", 560, 520, tt, 10.0, 0.6, 54)
        burst_word(c, "POP!", 600, 500, tt, 12.5, 0.6, 54)
        burst_word(c, "POP!", 580, 540, tt, 15.0, 0.6, 54)
        for (a_, b_, line) in lyr:
            if a_ <= tt < b_:
                lyric_lines(c, line, (tt - a_) / 0.3)
    s.draw = d
    return [s]


# ===================================================================== Short C: hedgehogs sleep in the day
def buildC():
    s = Scene("nightC", music="brave", trans=None, music_gain=0.5)
    s.fx("sparkle", 0.1)
    s.t = 0.15
    s.mark("yawn")
    esay(s, "biscuit", "I'm so sleepy. Goodnight, Prickles!", "sleepy", key="b1", gap=0.2)
    s.fx("pok")
    esay(s, "prickles", "Goodnight? I'm wide awake! Hedgehogs love the night!", "excited", key="p1", gap=0.3)
    s.mark("sleep"); s.fx("roll", s.t + 0.3, 0.4); s.fx("boing", s.t + 0.9, 0.5)
    s.wait(1.6)
    s.mark("morning"); s.fx("sparkle"); s.fx("chirp", s.t + 0.2); s.fx("chirp", s.t + 0.8)
    s.wait(1.0)
    s.fx("wag")
    esay(s, "biscuit", "Good morning, Prickles! Let's play!", "excited", key="b2", gap=0.2)
    esay(s, "prickles", "Not now. Hedgehogs sleep in the daytime. Goodnight!", "sleepy", key="p2", gap=0.2)
    s.mark("curl"); s.fx("roll", gain=0.4)
    s.wait(2.2)
    s.mark("end"); s.wait(1.6)
    BX = 520

    def d(c, t, s=s):
        if t >= s.M("end"):
            return end_card(c, t, s)
        m = ease(ramp(t, s.M("morning"), s.M("morning") + 0.9))
        vcam(c, 1.6, 580, 500)
        garden(c, t, props=(), sun_set=lerp(1.0, 0.2, m))
        dusk_overlay(c, 1.0 - m, 0.0)
        night_sky(c, t, 1.0 - m)
        dog_bed(c, BX, 660)
        asleep = s.M("sleep") < t < s.M("b2") - 0.4
        yawn = t < s.M("b1") + 0.6
        draw_biscuit(c, BX, 640, 1.0, t, mouth=0.9 if t < 0.7 else s.mouth("biscuit", t), face=1, sit=1,
                     ears=0.7 if t > s.M("b2") else -0.4, wag=1.8 if t > s.M("b2") else 0.2,
                     blink=1.0 if asleep or (yawn and t < 0.9) else None)
        if asleep:
            for i in range(3):
                ph = (t * 0.5 + i / 3) % 1
                text(c, "z", BX + 40 + ph * 40, 480 - ph * 70, 22 + 16 * ph, alpha(0xFFFFFFFF, 1 - ph), tf=ROUND_TF, ow=4)
        # Prickles: wide awake at night (tiptoes and hops around), asleep in the morning
        if t > s.M("curl"):
            draw_prickles(c, 720, SY, 0.9, t, roll=0)
            for i in range(3):
                ph = (t * 0.5 + i / 3) % 1
                text(c, "z", 750 + ph * 40, 560 - ph * 70, 22 + 16 * ph, alpha(0xFFFFFFFF, 1 - ph), tf=ROUND_TF, ow=4)
        else:
            sl = s.M("sleep")
            night_fun = sl < t < s.M("morning")
            px = 720 + (math.sin((t - sl) * 2.2) * 60 if night_fun else 0)
            py = SY + (hop((t - sl) % 0.8, 0, 0.8, 50) if night_fun else 0)
            draw_prickles(c, px, py, 0.9, t, mouth=s.mouth("prickles", t), face=-1 if math.cos((t - sl) * 2.2) > 0 or not night_fun else 1,
                          look=(-0.6, -0.4), blink=1.0 if s.M("p2") < t and int(t * 2) % 2 == 0 else None)
        c.restore()
        burst_word(c, "YAWN!", VW / 2, 470, t, 0.1, 1.0, 60, 0xFF8E5CF7)
        burst_word(c, "WIDE AWAKE!", VW / 2, 470, t, s.M("p1") + 0.3, 1.4, 52, 0xFF3D8BFF)
        if t > s.M("curl"):
            text(c, "HEDGEHOGS SLEEP", VW / 2, 170, 54, 0xFFFFD93B, ow=9, scale=back_out((t - s.M("curl")) / 0.4))
            text(c, "IN THE DAY!", VW / 2, 245, 54, 0xFFFFD93B, ow=9, scale=back_out((t - s.M("curl") - 0.2) / 0.4))
    s.draw = d
    return [s]


build = {"1": buildA, "2": buildB, "3": buildC}[os.environ.get("SHORT", "1")]
