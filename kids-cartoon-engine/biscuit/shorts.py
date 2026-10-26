"""Biscuit & Friends vertical Shorts (720x1280 design space). Each is a full mini-story: beginning, middle, end."""
import math, os
import numpy as np
import soundfile as sf
import show  # shared sound effects, voice cache, songs, finish()
import show2  # bath sounds and props
from show import *  # noqa: F401,F403
import audio as A

VW, VH = 720, 1280
SY = 650  # feet line in world space


def vcam(c, z, cx, cy):
    c.save()
    c.translate(VW / 2, VH / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


def vprompt(c, s_, t, t0, t1, y=1110, size=78, color=0xFFFFD93B):
    if not (t0 <= t < t1):
        return
    k = t - t0
    sc = back_out(k / 0.3) * (1 + 0.06 * math.sin(k * 10))
    text(c, s_, VW / 2, y, size, color, scale=sc)


def vtitle(c, s_, t, t0, t1, y=170, size=64, color=0xFFFFFFFF):
    if t0 <= t < t1:
        text(c, s_, VW / 2, y, size, color, scale=back_out((t - t0) / 0.4), ow=10)


def end_card(c, t, s):
    tt = t - s.M("end")
    hero_rays(c, t * 0.4, 0xFF6CC8FF, 0xFF8ED8FF)
    k = ease_out(tt / 0.6)
    text(c, "BISCUIT", VW / 2, 260, 110, 0xFFFFD93B, scale=k, ow=16)
    text(c, "& FRIENDS", VW / 2, 380, 90, 0xFFFFFFFF, scale=k, ow=14)
    draw_mittens(c, 170, 1000, 0.9 * k, t, paw_up=0.5 + 0.5 * math.sin(t * 6))
    draw_biscuit(c, 380, 1010, 1.0 * k, t, ears=0.7, wag=1.6)
    draw_prickles(c, 580, 1010, 0.9 * k, t, face=-1)


def finish_short(s):
    s.mark("end"); s.fx("tada", gain=0.7); s.wait(2.4)


# ===================================================================== Short 1: Prickles' Sticky Spikes
def build1():
    s = Scene("sticky", music="theme", trans=None, music_gain=0.5)
    s.fx("roll", 0.2); s.fx("pok", 1.6)
    s.wait(1.9)
    s.say("prickles", "[chuckle] Oopsie-prickle! A leaf stuck on my spikes!", key="p1", gap=0.3)
    s.mark("biscuit"); s.fx("patter"); s.fx("wag", s.t + 0.8)
    s.wait(1.0)
    s.say("biscuit", "Hi, Prickles! Want to play ball?", key="b1", gap=0.2)
    s.mark("throw"); s.fx("whistle", gain=0.6); s.fx("pok", s.t + 0.9)
    s.wait(1.3)
    s.say("biscuit", "[gasp] Where did my ball go?", key="b2", gap=0.2)
    s.say("prickles", "I don't see it!", key="p2", gap=0.3)
    s.say("narr", "Can you see the red ball? Tell them! It's on Prickles' back!", key="tell", gap=0.1)
    s.mark("kids"); s.wait(2.6)
    s.say("biscuit", "Prickles... turn around!", key="b3", gap=0.2)
    s.mark("spin"); s.fx("roll")
    s.say("prickles", "I can't see my back! [laugh] It's always behind me!", key="p3", gap=0.3)
    s.say("prickles", "Okay. Silly dance time!", key="p4", gap=0.1)
    s.mark("dance"); s.fx("pop", s.t + 0.9); s.fx("boing", s.t + 1.6); s.fx("boing", s.t + 2.1)
    s.wait(2.8)
    s.say("biscuit", "[laugh] That's okay! Woof! Woof! Hooray!", key="b4", gap=0.4)
    finish_short(s)

    def d(c, t, s=s):
        if t >= s.M("end"):
            return end_card(c, t, s)
        vcam(c, 1.75, 610, 445)
        garden(c, t, props=("tree",))
        # prickles rolls in, stands up with a leaf
        items = []
        if t > 1.6:
            items.append("leaf")
        tw = s.M("throw")
        if t > tw + 0.9:
            items.append("ball")
        dt0 = s.M("dance")
        if t > dt0 + 0.9:
            items = [i for i in items if i != "leaf"]
        if t > dt0 + 1.6:
            items = [i for i in items if i != "ball"]
        spin = s.M("spin") < t < s.M("p3_end")
        face = -1 if not spin or int((t - s.M("spin")) * 6) % 2 == 0 else 1
        dancing = dt0 < t < dt0 + 1.8
        if t < 1.6:
            px = kf(t, [(0.1, 1100), (1.5, 700)], lambda x: x)
            draw_prickles(c, px, SY, 1.0, t, roll=-(t * 600))
        else:
            draw_prickles(c, 700, SY - (abs(math.sin(t * 9)) * 20 if dancing else 0), 1.0, t, mouth=s.mouth("prickles", t),
                          face=face, items=items, wiggle=1.0 if dancing else 0, look=(-1, 0),
                          sparkle=1.0 if s.M("tell") < t < s.M("b3") else 0)
        bt = s.M("biscuit")
        if t > bt:
            bx = kf(t, [(bt, 250), (bt + 0.9, 515)])
            happy = t > s.M("b4") - 0.2
            draw_biscuit(c, bx, SY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.7 if happy else 0.2,
                         wag=1.6 if happy or t < tw else 0.4, sad=0.5 if s.M("b2") < t < s.M("b4") else 0, look=(1, 0))
        # thrown ball arcs onto his back
        if tw < t < tw + 0.9:
            k = ramp(t, tw, tw + 0.9)
            stuck_item(c, "ball", lerp(570, 650, k), lerp(560, 610, k) - math.sin(k * math.pi) * 200, 1.3, k * 600, t)
        if dt0 + 1.6 < t:
            k = ramp(t, dt0 + 1.6, dt0 + 2.6)
            stuck_item(c, "ball", lerp(650, 580, k), 620 + bounce_y(t, dt0 + 1.6, 2, 160, 1.0), 1.3, -k * 500, t, sparkle=1.0)
        if dt0 + 0.9 < t < dt0 + 2.4:
            k = t - dt0 - 0.9
            stuck_item(c, "leaf", 680 + k * 160, 540 - k * 300 + k * k * 300, 1.3, k * 400, t)
        c.restore()
        vtitle(c, "PRICKLES' STICKY SPIKES", t, 0.0, 3.0, size=50)
        vprompt(c, "IT'S ON HIS BACK!", t, s.M("kids") - 0.2, s.M("b3"), size=74)
        if t > s.M("b4"):
            vtitle(c, "HOORAY!", t, s.M("b4"), s.M("end"), y=200, size=110, color=0xFFFFD93B)
    s.draw = d
    return finish([s])


# ===================================================================== Short 2: Bath Time Song
def bath_excerpt():
    """Song opening + the 'scrub your tummy' verse, then jump to 'all clean and fluffy, hooray'."""
    path = os.path.join(SONGS, "bath_short.wav")
    if not os.path.exists(path):
        y = load_song("bath.mp3")
        a = y[: int(17.4 * A.SR)]
        b = y[int(55.3 * A.SR): int(61.6 * A.SR)]
        x = int(0.25 * A.SR)
        a[-x:] *= np.linspace(1, 0, x)
        b[:x] *= np.linspace(0, 1, x)
        sf.write(path, np.concatenate([a, b]), A.SR)
    return "bath_short.wav"


def build2():
    s = Scene("bath", music="theme", trans=None, music_gain=0.45)
    s.fx("patter", 0.1); s.wait(0.9); s.mark("jump"); s.fx("splash", s.t + 0.5); s.wait(0.9)
    s.fx("wag")
    s.say("biscuit", "[laugh] Mud! Mud! I love mud!", key="b1", gap=0.3)
    s.say("mittens", "Biscuit! You're all muddy. It's bath time.", key="m1", gap=0.2)
    s.say("biscuit", "[sigh] No bath! Baths are scary.", key="b2", gap=0.2)
    s.say("prickles", "[laugh] Bath time can be fun! Look, bubbles!", key="p1", gap=0.3)
    s.mark("tub"); s.fx("splash_small"); s.wait(0.8)
    add_song(s, bath_excerpt(), "song", gain=1.0)
    s.say("biscuit", "Bath time is fun! I'm all clean and fluffy.", key="b3", gap=0.4)
    finish_short(s)
    lyr = [(0.0, 4.6, "It's bath time, bath time!"), (4.6, 8.6, "Water, bubbles, scrub, rinse, dry!"),
           (8.6, 13.0, "Scrub your tummy, scrub, scrub, scrub!"), (13.0, 17.4, "Scrub your tummy!"),
           (17.4, 21.5, "All clean and fluffy!"), (21.5, 23.6, "Hooray!")]

    def d(c, t, s=s):
        if t >= s.M("end"):
            return end_card(c, t, s)
        vcam(c, 1.6, 555, 430)
        garden(c, t, props=("tree",))
        intub = t > s.M("tub")
        st = s.M("song")
        tt = t - st
        clean = ease(ramp(tt, 8.6, 16.0))
        if not intub:
            mud_puddle(c, 540, 668, 120, t)
            jt = s.M("jump")
            bx = kf(t, [(0, 250), (jt, 430), (jt + 0.5, 540)])
            by = SY + 10 + (hop(t, jt, 0.5, 120) if t < jt + 0.5 else 0)
            sad = ease(ramp(t, s.M("b2"), s.M("b2") + 0.4)) * (1 - ease(ramp(t, s.M("p1"), s.M("p1") + 0.5)))
            draw_biscuit(c, bx, by, 1.0, t, mouth=s.mouth("biscuit", t), face=1, mud=ease(ramp(t, jt + 0.45, jt + 0.6)),
                         sad=sad, ears=lerp(0.6, -1, sad))
            splash_fx(c, 540, 668, jt + 0.5, t, 1.0, 0xFF8B5A2B)
            draw_mittens(c, 385, SY, 0.85, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0))
            draw_prickles(c, 715, SY, 0.85, t, mouth=s.mouth("prickles", t), face=-1, look=(-1, 0))
        else:
            sing = s.mouth("song", t)
            scrub = 8.6 < tt < 17.4
            fluffy = tt > 17.4
            tub_back(c, 560, 700, 1.0)
            draw_biscuit(c, 560 + (math.sin(t * 14) * 5 if scrub else 0), 600, 1.0, t, mouth=max(sing, s.mouth("biscuit", t)),
                         face=1, mud=1 - clean, ears=0.7, wag=1.6)
            tub_front(c, 560, 700, 1.0, water=0.75, t=t, bubbles=1.0)
            if fluffy:
                sparkles(c, 560, 480, t, 10, 110)
            for i in range(5):
                ph = (t * 0.3 + i / 5) % 1
                bubble(c, 420 + i * 60, 560 - ph * 300, 10 + 5 * hsh(i), t)
        c.restore()
        vtitle(c, "BATH TIME SONG!", t, 0.0, s.M("song"), size=64)
        if t > st:
            for (a_, b_, line) in lyr:
                if a_ <= tt < b_:
                    vtitle(c, line.upper(), t, st + a_, st + b_, y=200, size=44 if len(line) < 24 else 36, color=0xFFFFD93B)
            if 8.6 < tt < 17.4:
                vprompt(c, "SCRUB YOUR TUMMY!", t, st + 8.6, st + 17.4, size=66)
    s.draw = d
    return finish([s])


# ===================================================================== Short 3: Hedgehogs Sleep in the Day
def build3():
    s = Scene("night", music="brave", trans=None, music_gain=0.45)
    s.wait(0.8)
    s.mark("yawn")
    s.say("biscuit", "[sigh] I'm a little bit sleepy.", key="b1", gap=0.2)
    s.say("narr", "Can you do a big yawn?", key="n1", gap=0.1)
    s.mark("kids"); s.wait(2.2)
    s.say("prickles", "Not me! [laugh] I'm wide awake!", key="p1", gap=0.3)
    s.say("mittens", "Shh. Goodnight, Biscuit.", key="m1", gap=0.4)
    s.mark("sleep")
    s.say("prickles", "Shh... They're sleeping. I'll keep watch all night.", key="p2", gap=0.3)
    s.wait(1.6)
    s.mark("morning"); s.fx("chirp"); s.fx("chirp", s.t + 1.0)
    s.wait(1.6)
    s.say("biscuit", "[laugh] Good morning! I feel great!", key="b2", gap=0.2)
    s.fx("wag", s.M("b2") + 0.3)
    s.say("prickles", "[sigh] Good morning... Hedgehogs sleep in the daytime. Goodnight...", key="p3", gap=0.2)
    s.mark("curl"); s.fx("roll", gain=0.4)
    s.wait(0.6)
    s.say("narr", "Shh. Prickles is sleeping now!", key="n2", gap=0.4)
    finish_short(s)
    BX = 545

    def d(c, t, s=s):
        if t >= s.M("end"):
            return end_card(c, t, s)
        m = ease(ramp(t, s.M("morning"), s.M("morning") + 1.6))
        vcam(c, 1.6, 560, 430)
        garden(c, t, props=("tree",), sun_set=lerp(1.0, 0.2, m))
        dusk_overlay(c, 1.0 - m, 0.0)
        night_sky(c, t, 1.0 - m)
        dog_bed(c, BX, 660)
        asleep = s.M("sleep") < t < s.M("b2") - 0.3
        yawn = s.M("yawn") - 0.2 < t < s.M("b1") + 0.7
        draw_biscuit(c, BX, 640, 1.0, t, mouth=0.9 if yawn else s.mouth("biscuit", t), face=1, sit=1,
                     ears=0.6 if t > s.M("b2") else -0.2, wag=1.6 if t > s.M("b2") else 0.2,
                     blink=1.0 if asleep or yawn else None)
        draw_mittens(c, 385, SY, 0.85, t, mouth=s.mouth("mittens", t), face=1, lid=0.5, blink=1.0 if asleep else None)
        if asleep:
            for i in range(3):
                ph = (t * 0.5 + i / 3) % 1
                text(c, "z", BX + 40 + ph * 40, 480 - ph * 70, 22 + 16 * ph, alpha(0xFFFFFFFF, 1 - ph), tf=ROUND_TF, ow=4)
        if t > s.M("curl"):
            draw_prickles(c, 730, SY, 0.9, t, roll=0)
            for i in range(3):
                ph = (t * 0.5 + i / 3) % 1
                text(c, "z", 760 + ph * 40, 560 - ph * 70, 22 + 16 * ph, alpha(0xFFFFFFFF, 1 - ph), tf=ROUND_TF, ow=4)
        else:
            draw_prickles(c, 730, SY, 0.9, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.6, -0.4))
        c.restore()
        vtitle(c, "WHEN DO HEDGEHOGS SLEEP?", t, 0.0, 3.2, size=46)
        vprompt(c, "BIG YAWN!", t, s.M("kids") - 0.2, s.M("p1"), size=96)
        if t > s.M("curl"):
            vtitle(c, "IN THE DAYTIME!", t, s.M("curl"), s.M("end"), y=200, size=70, color=0xFFFFD93B)
    s.draw = d
    return finish([s])


build = {"1": build1, "2": build2, "3": build3}[os.environ.get("SHORT", "1")]
