"""Biscuit & Friends, Episode 1: Where's the Red Ball? Scene timing + drawing."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chars import *  # noqa: F401,F403  (also brings the shared drawing kit)
import numpy as np
import episode as PE  # shared Scene / camera / prompt helpers from the Pip engine
import audio as A
import voice

PE.speak = voice.speak
Scene, cam, prompt, hero_rays = PE.Scene, PE.cam, PE.prompt, PE.hero_rays
ALL = ["biscuit", "mittens", "prickles"]
GY = 650  # where feet stand


# ---------------------------------------------------------------- extra sound effects
def sfx_roll():
    d = 1.6
    t = A.t_arr(d)
    y = A.lp(A.noise(d), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * np.minimum(1, t * 4)
    return A.norm(y, 0.45)

def sfx_squeak():
    t = A.t_arr(0.25)
    f = 900 + 700 * np.sin(np.pi * t / 0.25)
    return A.norm(np.sin(2 * np.pi * np.cumsum(f) / A.SR) * np.hanning(len(t)), 0.4)

def sfx_pok():
    t = A.t_arr(0.12)
    y = np.sin(2 * np.pi * (600 - 3000 * t) * t) * np.exp(-t * 40) + A.lp(A.noise(0.12), 2500) * np.exp(-t * 60) * 0.4
    return A.norm(y, 0.55)

def sfx_patter():
    out = np.zeros(int(1.4 * A.SR))
    for k in range(10):
        tt = A.t_arr(0.05)
        tap = A.lp(A.noise(0.05), 1500) * np.exp(-tt * 80)
        i = int(k * 0.13 * A.SR)
        out[i:i + len(tap)] += tap * (0.7 + 0.3 * (k % 2))
    return A.norm(out, 0.35)

def sfx_mrrp():
    t = A.t_arr(0.3)
    f = 420 + 260 * np.sin(np.pi * t / 0.3)
    y = sum(np.sin(2 * np.pi * np.cumsum(f * h) / A.SR) / h for h in range(1, 5)) * np.hanning(len(t))
    return A.norm(A.lp(y, 2500), 0.35)

def sfx_scratch():
    out = np.zeros(int(1.0 * A.SR))
    for k in range(6):
        b = A.bp(A.noise(0.08), 1500, 6000) * np.hanning(int(0.08 * A.SR))
        i = int(k * 0.15 * A.SR)
        out[i:i + len(b)] += b
    return A.norm(out, 0.3)

def sfx_sniff():
    out = np.zeros(int(0.9 * A.SR))
    for k in range(3):
        b = A.bp(A.noise(0.12), 800, 3000) * np.hanning(int(0.12 * A.SR))
        i = int(k * 0.25 * A.SR)
        out[i:i + len(b)] += b
    return A.norm(out, 0.35)

A.SFX.update({"roll": sfx_roll, "squeak": sfx_squeak, "pok": sfx_pok, "patter": sfx_patter, "mrrp": sfx_mrrp,
              "scratch": sfx_scratch, "sniff": sfx_sniff})


# ---------------------------------------------------------------- helpers
def checklist(c, t, s, n_done_marks):
    """Three numbered circles in the top-right corner, checked as each place is searched."""
    for i in range(3):
        x, y = 1000 + i * 90, 70
        done = t > s.M(n_done_marks[i]) if n_done_marks[i] else False
        circle(c, x, y, 34, 0xFF6CCB5F if done else 0xFFFFFFFF, 5)
        if done:
            k = back_out((t - s.M(n_done_marks[i])) / 0.3)
            p = skia.Path(); p.moveTo(x - 14 * k, y); p.lineTo(x - 3 * k, y + 12 * k); p.lineTo(x + 16 * k, y - 12 * k)
            c.drawPath(p, stroke(0xFFFFFFFF, 8))
        else:
            text(c, str(i + 1), x, y, 40, 0xFF3D8BFF, ow=0)


def bounce_y(t, t0, n, h, dur):
    """Ball bouncing n times, each lower, over dur seconds."""
    k = (t - t0) / dur * n
    if k < 0 or k >= n:
        return 0.0
    i = int(k)
    return hop(k - i, 0, 1, h * (0.75 ** i))


# ===================================================================== scenes
def build():
    S = []

    # ---------------- TITLE CARD
    s = Scene("title", music="theme", trans=None, music_gain=1.2)
    for i in range(3):
        s.fx("boing", 0.3 + i * 0.45)
    s.fx("sparkle", 1.7)
    s.t = 4.2

    def d0(c, t, s=s):
        hero_rays(c, t, 0xFF6CC8FF, 0xFF8ED8FF)
        bx = kf(t, [(0.0, -60), (1.6, 640)], lambda x: x)
        by = 420 + bounce_y(t, 0.0, 3, 260, 1.6)
        stuck_item(c, "ball", bx, by, 3.0, t * 200 if t < 1.6 else 0, t)
        k = back_out((t - 1.6) / 0.5)
        if t > 1.6:
            text(c, "BISCUIT & FRIENDS", 640, 170, 96, 0xFFFFD93B, scale=k, ow=14)
            text(c, "Where's the Red Ball?", 640, 600, 64, 0xFFFFFFFF, scale=back_out((t - 2.0) / 0.5))
            draw_biscuit(c, 330, 560, 0.9 * k, t, ears=0.6)
            draw_prickles(c, 950, 560, 0.9 * k, t, face=-1)
    s.draw = d0
    S.append(s)

    # ---------------- 0. THE SECRET: the ball sticks to Prickles (kids see it, Biscuit doesn't)
    s = Scene("secret", music="theme", trans="bubble", music_gain=0.5)
    s.fx("roll", 0.3); s.fx("pok", 2.6); s.fx("sparkle", 2.7)
    s.wait(4.1)
    s.say("narr", "Uh oh! Did you see that?", key="uh", gap=0.1)
    s.mark("kids"); s.wait(1.6)
    s.say("narr", "Shh. It's our secret!", key="shh", gap=0.6)

    def d_secret(c, t, s=s):
        cam(c, 1.25, 560, 460)
        garden(c, t, props=("box", "tree"))
        px = kf(t, [(0.3, 1450), (3.8, -200)], lambda x: x)
        stuck = px < 365
        if not stuck:
            stuck_item(c, "ball", 365, 628, 1.4, 0, t)
        draw_prickles(c, px, GY, 1.0, t, roll=-(t * 600), items=["ball"] if stuck else [], sparkle=1.0)
        if 0.3 < t < 3.8:
            speed_lines(c, px + 60, GY - 50, 1, 4, 100)
        c.restore()
        if s.M("uh") < t < s.M("shh_end"):
            text(c, "?", 640, 300, 140, 0xFFFFD93B, scale=back_out((t - s.M("uh")) / 0.3) * (1 + 0.08 * math.sin(t * 8)))
    s.draw = d_secret
    S.append(s)

    # ---------------- 1. BALL DAY
    s = Scene("ballday", music="theme", trans="bubble", music_gain=0.5)
    s.fx("patter", 0.1); s.fx("chirp", 0.0)
    s.wait(1.6)
    s.say("biscuit", "[laugh] Hi, friends! I'm Biscuit! Today is the best day ever. It's ball day!", key="hi", gap=0.4)
    s.mark("dig"); s.fx("pok", s.t + 0.6); s.fx("squeak", s.t + 1.3)
    s.say("biscuit", "Where is it? Where is it?", key="where", gap=0.6)
    s.mark("sad"); s.fx("wahwah", s.t + 0.1, 0.7)
    s.wait(0.4)
    s.say("biscuit", "[sigh] Oh no. My red ball is gone.", key="gone", gap=0.8)

    def d1(c, t, s=s):
        z, cx, cy = 1.2, 560, 460
        if t > s.M("sad"):
            k = ease(ramp(t, s.M("sad"), s.M("sad") + 0.6))
            z, cx, cy = lerp(1.2, 1.8, k), lerp(560, 400, k), lerp(460, 470, k)
        cam(c, z, cx, cy)
        garden(c, t)
        bx = kf(t, [(0, 1450), (1.5, 410)], ease_out)
        running = t < 1.5
        dig = s.M("dig") < t < s.M("sad")
        tilt = -30 if dig else 0
        px = bx - (70 if dig else 0)
        sad = ease(ramp(t, s.M("sad"), s.M("sad") + 0.5))
        draw_biscuit(c, px, GY - (abs(math.sin(t * 12)) * 16 if running else 0) - (30 if dig else 0), 1.05, t,
                     mouth=s.mouth("biscuit", t), face=-1, tilt=tilt, sad=sad, ears=lerp(0.4, -1, sad),
                     wag=lerp(1.4, 0.1, sad), blink=1.0 if dig else None)
        # toys flying out of the box
        for i, (kind, t0) in enumerate((("bone", s.M("dig") + 0.5), ("toy", s.M("dig") + 1.2))):
            if t0 < t < t0 + 1.2:
                k = (t - t0) / 1.2
                x = lerp(250, 80 + i * 120, k)
                y = 500 - math.sin(k * math.pi) * 200 + k * 140
                c.save(); c.translate(x, y); c.rotate(k * 500)
                if kind == "bone":
                    for sx in (-1, 1):
                        circle(c, sx * 22, -7, 9, 0xFFFFF4DC, 3.5); circle(c, sx * 22, 7, 9, 0xFFFFF4DC, 3.5)
                    c.drawRect(skia.Rect.MakeLTRB(-22, -6, 22, 6), fill(0xFFFFF4DC))
                else:
                    circle(c, 0, 0, 16, 0xFF8E5CF7, 3.5); circle(c, 0, -20, 7, 0xFFFFD93B, 3)
                c.restore()
        c.restore()
    s.draw = d1
    S.append(s)

    # ---------------- 2. MITTENS
    s = Scene("mittens", music="theme", trans="bubble", music_gain=0.5)
    s.fx("mrrp", 0.4); s.wait(1.4); s.mark("hop"); s.fx("boing"); s.wait(0.7); s.fx("pok", s.t - 0.1, 0.5)
    s.say("mittens", "Good morning, Biscuit. Why the sad face?", key="m1", gap=0.3)
    s.say("biscuit", "I lost my red ball. It's my favorite ball in the whole world.", key="b1", gap=0.3)
    s.say("mittens", "Don't worry. Cats are very good at finding things. We'll find it together.", key="m2", gap=0.3)
    s.mark("yay"); s.fx("boing", s.t + 0.1); s.fx("boing", s.t + 0.6)
    s.say("biscuit", "[laugh] Woof! Woof! Hooray!", key="b2", gap=0.7)

    def d2(c, t, s=s):
        cam(c, 1.3, 560, 460)
        garden(c, t)
        ht = s.M("hop")
        happy = t > s.M("yay")
        draw_biscuit(c, 400, GY + hop(t, s.M("yay") + 0.1, 0.45, 60) + hop(t, s.M("yay") + 0.6, 0.45, 60), 1.0, t,
                     mouth=s.mouth("biscuit", t), face=1, sad=0 if happy else 1, ears=0.6 if happy else -1,
                     wag=1.5 if happy else 0.2, look=(1, 0))
        if t < ht:
            st = ease(ramp(t, 0.3, 1.2)) * (1 - ease(ramp(t, 1.2, 1.4)))
            draw_mittens(c, 680, 392, 0.8, t, stretch=st, blink=1.0 if st > 0.5 else None, look=(-1, 0.4))
        else:
            k = ramp(t, ht, ht + 0.7)
            mx, my = lerp(680, 640, k), lerp(392, GY, k) - math.sin(k * math.pi) * 90
            sc = lerp(0.8, 1.0, k)
            draw_mittens(c, mx, my, sc, t, mouth=s.mouth("mittens", t), face=-1, look=(-0.6, 0))
        c.restore()
    s.draw = d2
    S.append(s)

    # ---------------- 3. PRICKLES ROLLS IN
    s = Scene("prickles", music="theme", trans="spin", music_gain=0.5)
    s.fx("roll", 0.0); s.mark("bonk"); s.m["bonk"] = 1.6; s.fx("bonk", 1.6); s.fx("pok", 1.9)
    s.wait(2.2); s.mark("back")
    s.wait(2.2)
    s.say("prickles", "[chuckle] Oopsie-prickle! Hi, everybody!", key="p1", gap=0.3)
    s.say("mittens", "Prickles, you have a flower on your spikes.", key="m1", gap=0.3)
    s.say("prickles", "Do I? Ooh, pretty!", key="p2", gap=0.6)
    s.say("narr", "Psst. Friends. Did you see something red?", key="psst", gap=0.1)
    s.mark("kids"); s.fx("sparkle", s.t + 0.2); s.wait(2.2)
    s.say("narr", "Shh. Let's keep watching!", key="shh", gap=0.6)

    def d3(c, t, s=s):
        z, cx, cy = 1.15, 600, 450
        bt = s.M("back")
        if bt < t < s.M("p1"):
            k = ease(ramp(t, bt, bt + 0.5)) * (1 - ease(ramp(t, s.M("p1") - 0.4, s.M("p1"))))
            z, cx, cy = lerp(1.15, 2.6, k), lerp(600, 880, k), lerp(450, 600, k)
        if s.M("psst") < t < s.M("shh_end"):
            k = ease(ramp(t, s.M("psst"), s.M("psst") + 0.5)) * (1 - ease(ramp(t, s.M("shh_end") - 0.3, s.M("shh_end"))))
            z, cx, cy = lerp(1.15, 2.2, k), lerp(600, 880, k), lerp(450, 590, k)
        cam(c, z, cx, cy)
        garden(c, t, pot_wobble=math.sin((t - 1.6) * 20) * 10 * max(0, 1 - (t - 1.6) * 2) if t > 1.6 else 0)
        draw_biscuit(c, 380, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.2, look=(1, 0))
        draw_mittens(c, 580, GY, 1.0, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0))
        items = ["ball"] + (["flower"] if t > 1.9 else [])
        if t < 1.7:
            px = kf(t, [(0, 1450), (1.6, 860)], lambda x: x)
            draw_prickles(c, px, GY, 1.0, t, roll=-(t * 600), items=["ball"])
            if t < 1.6:
                speed_lines(c, px + 60, GY - 50, 1, 4, 100)
        else:
            k = ramp(t, 1.7, 2.0)
            sq = math.sin(clamp(t - 1.9) * 14) * 0.4 * max(0, 1 - (t - 1.9) * 2) if t > 1.9 else 0
            look = (1, -0.3) if s.M("p2") < t < s.M("p2_end") + 0.3 else (-1, 0)
            draw_prickles(c, 860, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, items=items, squash=sq,
                          look=look, sparkle=1.0 if s.M("kids") - 0.5 < t < s.M("shh_end") or bt < t < s.M("p1") else 0)
        c.restore()
        if s.M("kids") < t < s.M("shh"):
            text(c, "?", 1010, 300, 120, 0xFFFFD93B, scale=back_out((t - s.M("kids")) / 0.3) * (1 + 0.08 * math.sin(t * 8)))
    s.draw = d3
    S.append(s)

    # ---------------- 4a. SEARCH: THE BUCKET
    s = Scene("bucket", music="search", trans="boots", music_gain=0.7)
    s.wait(0.3)
    s.say("mittens", "Here's the plan. We look in three places. Ready?", key="plan", gap=0.2)
    s.say(ALL, "Ready!", key="ready", gap=0.5)
    s.fx("patter"); s.wait(1.2)
    s.mark("tip"); s.fx("bonk"); s.fx("squeak", s.t + 0.5)
    s.wait(1.2)
    s.say("biscuit", "A duck! Not my ball.", key="duck", gap=0.3)
    s.say(["biscuit", "mittens"], "Is it in the bucket?", key="ask", gap=0.1)
    s.mark("kids"); s.wait(1.9)
    s.say("narr", "No, no, no! Let's keep looking.", key="no", gap=0.3)
    s.mark("backup"); s.fx("pok", s.t + 0.9)
    s.wait(1.1)
    s.say("prickles", "[chuckle] Oopsie-prickle!", key="oops", gap=0.3)
    s.mark("check1"); s.fx("ding5"); s.wait(1.0)

    def d4(c, t, s=s):
        cam(c, 1.25, 620, 460)
        tip = ease(ramp(t, s.M("tip"), s.M("tip") + 0.4))
        garden(c, t, props=("pot", "tree"))
        bucket(c, 600, 640, 1.0, tip * 0.9)
        bx = kf(t, [(s.M("tip") - 1.2, 300), (s.M("tip"), 470)])
        draw_biscuit(c, bx, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.3, look=(1, 0.3) if t > s.M("tip") else (1, 0))
        draw_mittens(c, 230, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1)
        # duck rolls out, past Prickles, then sticks to his back
        bk = s.M("backup")
        px = 820 if t < bk else kf(t, [(bk, 820), (bk + 0.9, 880)])
        items = ["ball"] + (["duck"] if t > bk + 0.9 else [])
        if s.M("tip") + 0.3 < t < bk + 0.9:
            dk = ease_out(ramp(t, s.M("tip") + 0.3, s.M("tip") + 1.1))
            stuck_item(c, "duck", lerp(640, 960, dk), 630 - math.sin(dk * math.pi) * 40, 1.4, 0, t)
        draw_prickles(c, px, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, items=items)
        c.restore()
        checklist(c, t, s, ["check1", None, None])
        prompt(c, "NO, NO, NO!", t, s.M("kids"), s.M("no"), y=170, size=90)
    s.draw = d4
    S.append(s)

    # ---------------- 4b. SEARCH: THE TALL GRASS
    s = Scene("grass", music="search", trans="spin", music_gain=0.6)
    s.wait(0.6)
    s.say("mittens", "Look carefully.", key="look", gap=0.4)
    s.mark("sniff"); s.fx("sniff"); s.wait(1.2); s.fx("pop")
    s.say("biscuit", "Look, a sock! Not my ball.", key="sock", gap=0.3)
    s.say(["biscuit", "mittens"], "Is it in the grass?", key="ask", gap=0.1)
    s.mark("kids"); s.wait(1.9)
    s.say("narr", "No, no, no!", key="no", gap=0.3)
    s.mark("sit"); s.fx("pok", s.t + 0.5)
    s.wait(0.8)
    s.say("prickles", "[chuckle] Oopsie-prickle! Again!", key="oops", gap=0.3)
    s.mark("check2"); s.fx("ding6")
    s.wait(0.4); s.mark("peek"); s.fx("sparkle", s.t + 0.3); s.wait(2.0)

    def d5(c, t, s=s):
        z, cx, cy = 1.3, 640, 470
        if t > s.M("peek"):
            k = ease(ramp(t, s.M("peek"), s.M("peek") + 0.6))
            z, cx, cy = lerp(1.3, 2.4, k), lerp(640, 830, k), lerp(470, 600, k)
        cam(c, z, cx, cy)
        garden(c, t, props=("tree",))
        draw_mittens(c, 330, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(0.5, 0.5))
        sn = s.M("sniff") < t < s.M("sock")
        draw_biscuit(c, 540, GY + (8 if sn else 0), 1.0, t, mouth=s.mouth("biscuit", t), face=1, tilt=18 if sn else 0,
                     look=(0.5, 1) if sn else (0, 0), ears=0.2)
        sock_out = t > s.M("sock") - 0.2
        items = ["ball", "duck"] + (["sock"] if t > s.M("sit") + 0.5 else [])
        draw_prickles(c, 760, GY + (10 if s.M("sit") < t < s.M("sit") + 0.6 else 0), 1.0, t, mouth=s.mouth("prickles", t),
                      face=-1, items=items, sparkle=1.0 if t > s.M("peek") else 0)
        tall_grass(c, 260, 1060, 690, t, 110)
        if sock_out and t < s.M("sit") + 0.5:
            k = ease_out(ramp(t, s.M("sock") - 0.2, s.M("sock") + 0.4))
            kk = ease(ramp(t, s.M("sit"), s.M("sit") + 0.5))
            stuck_item(c, "sock", lerp(lerp(600, 640, k), 820, kk), lerp(lerp(640, 520, k), 560, kk), 1.3, 0, t)
        c.restore()
        checklist(c, t, s, ["_", "check2", None])
        prompt(c, "NO, NO, NO!", t, s.M("kids"), s.M("no_end"), y=170, size=90)
    s.m["_"] = -1.0
    s.draw = d5
    S.append(s)

    # ---------------- 4c. SEARCH: UP THE TREE
    s = Scene("tree", music="brave", trans="bubble", music_gain=0.7)
    s.wait(0.3)
    s.say("mittens", "Cats are good at climbing. I'll look up high.", key="m1", gap=0.2)
    s.mark("climb"); s.fx("scratch"); s.wait(1.6)
    s.say("mittens", "Shh... It's a nest with baby birds. Let's count them, quietly.", key="m2", gap=0.3)
    for i, w in enumerate(["One.", "Two.", "Three."]):
        s.mark(f"n{i}"); s.fx(f"ding{i + 1}", gain=0.5)
        s.say("narr", w, gap=0.5)
    s.say("mittens", "Three baby birds. But no red ball.", key="m3", gap=0.3)
    s.mark("check3"); s.fx("ding7", gain=0.6)
    s.mark("down"); s.wait(1.4)
    s.say(["biscuit", "prickles"], "Is it in the tree?", key="ask", gap=0.1)
    s.mark("kids"); s.wait(1.8)
    s.say("narr", "No, no, no!", key="no", gap=0.6)

    def d6(c, t, s=s):
        ct = s.M("climb")
        k = ease(ramp(t, ct, ct + 1.4)) * (1 - ease(ramp(t, s.M("down"), s.M("down") + 1.2)))
        z, cx, cy = lerp(1.25, 2.3, k), lerp(700, 1110, k), lerp(460, 270, k)
        cam(c, z, cx, cy)
        garden(c, t, props=("box",))
        tree(c, 1110, 560, 1.0)
        nest(c, 1080, 248, 1.0, t)
        draw_biscuit(c, 520, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, look=(1, -1), ears=0.2)
        draw_prickles(c, 720, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, items=["ball", "duck", "sock"], look=(-0.2, -1))
        my = lerp(GY, 345, k)
        mx = lerp(960, 1160, k)
        draw_mittens(c, mx, my, lerp(0.95, 0.7, k), t, mouth=s.mouth("mittens", t), face=-1 if k > 0.5 else 1, look=(1, 0.3), lid=0.4)
        c.restore()
        for i in range(3):
            nt = s.M(f"n{i}")
            if nt < t < s.M("check3") + 0.3:
                text(c, str(i + 1), 520 + i * 120, 140, 96, [0xFF7FD3FF, 0xFFFFD93B, 0xFFFF9BD5][i], scale=back_out((t - nt) / 0.3), ow=10)
        checklist(c, t, s, ["_", "_", "check3"])
        prompt(c, "NO, NO, NO!", t, s.M("kids"), s.M("no_end"), y=170, size=90)
    s.m["_"] = -1.0
    s.draw = d6
    S.append(s)

    # ---------------- 5. BISCUIT IS SAD / TELL THEM
    s = Scene("tell", music="brave", trans="spin", music_gain=0.6)
    s.wait(0.4)
    s.say("biscuit", "[sigh] We looked everywhere. My red ball is gone forever.", key="b1", gap=0.4)
    s.say("prickles", "Don't be sad, Biscuit! I know! I'll do my silly dance. It always makes everybody laugh!", key="p1", gap=0.3)
    s.say("narr", "Wait! Friends, you know where the red ball is! Let's tell them! Say: it's on Prickles' back!", key="tell", gap=0.1)
    s.mark("kids"); s.wait(3.0)
    s.say("mittens", "Prickles... turn around.", key="m1", gap=0.2)
    s.mark("spin"); s.fx("roll")
    s.wait(0.6)
    s.say("prickles", "I can't see my back! [laugh] It's always behind me!", key="p2", gap=0.6)
    s.duck_zero.append((s.M("kids") - 0.1, s.M("m1")))

    def d7(c, t, s=s):
        z, cx, cy = 1.3, 620, 470
        if s.M("tell") < t < s.M("m1"):
            k = ease(ramp(t, s.M("tell"), s.M("tell") + 0.6))
            z, cx, cy = lerp(1.3, 1.9, k), lerp(620, 860, k), lerp(470, 560, k)
        cam(c, z, cx, cy)
        garden(c, t, props=("tree",))
        draw_biscuit(c, 380, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, sad=1, ears=-1, wag=0.1, sit=1)
        draw_mittens(c, 600, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0))
        spin = s.M("spin") < t < s.M("p2_end")
        face = -1
        if spin:
            face = -1 if int((t - s.M("spin")) * 6) % 2 == 0 else 1
        draw_prickles(c, 860, GY, 1.0, t, mouth=s.mouth("prickles", t), face=face, items=["ball", "duck", "sock", "flower"],
                      sparkle=1.0 if s.M("tell") < t < s.M("m1") else 0, look=(-1, 0))
        c.restore()
        prompt(c, "IT'S ON PRICKLES' BACK!", t, s.M("kids") - 0.2, s.M("m1"), y=110, size=70)
    s.draw = d7
    S.append(s)

    # ---------------- 6. THE SILLY DANCE
    s = Scene("dance", music="theme", trans="hero", music_gain=0.8)
    s.say("prickles", "Okay. Silly dance time!", key="p1", gap=0.2)
    s.mark("dance")
    offs = [("flower", 0.8, "pop"), ("duck", 1.5, "squeak"), ("sock", 2.2, "pop"), ("ball", 2.9, "boing")]
    for kind, dt, fx in offs:
        s.fx(fx, s.t + dt)
    s.fx("boing", s.t + 3.5); s.fx("boing", s.t + 3.95)
    s.wait(4.6)
    s.mark("hush"); s.wait(1.6)
    s.say("biscuit", "[gasp] My red ball! It was on Prickles the whole time!", key="b1", gap=0.3)
    s.say("prickles", "Oopsie-prickle! Sorry, Biscuit!", key="p2", gap=0.3)
    s.say("biscuit", "[laugh] That's okay! Woof! Woof! Hooray!", key="b2", gap=0.3)
    s.say("mittens", "Purr-fect.", key="m1", gap=0.3)
    s.fx("sparkle")
    s.say("biscuit", "Thank you, friends! You found it! You're super finders!", key="b3", gap=0.7)
    s.duck_zero.append((s.M("hush"), s.M("b1")))

    def d8(c, t, s=s):
        k = ease(ramp(t, s.M("hush"), s.M("hush") + 1.4)) * (1 - ease(ramp(t, s.M("b1_end"), s.M("b1_end") + 0.6)))
        cam(c, lerp(1.3, 2.3, k), lerp(600, 470, k), lerp(470, 570, k))
        garden(c, t, props=("tree",))
        dt0 = s.M("dance")
        happy = t > s.M("b1")
        draw_biscuit(c, 400, GY + (hop((t - s.M("b2")) % 0.5, 0, 0.5, 50) if s.M("b2") < t < s.M("b2_end") else 0), 1.0, t,
                     mouth=s.mouth("biscuit", t), face=1, sad=0 if happy else 0.6, ears=0.7 if happy else -0.5,
                     wag=1.6 if happy else 0.3, look=(1, 0.4))
        draw_mittens(c, 230, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0))
        items, offsets = [], {}
        flying = []
        for kind, d, _ in offs:
            ft = dt0 + d
            if t < ft:
                items.append(kind)
            else:
                flying.append((kind, ft))
        dancing = dt0 < t < dt0 + 3.2
        draw_prickles(c, 860, GY - (abs(math.sin(t * 9)) * 20 if dancing else 0), 1.0, t, mouth=s.mouth("prickles", t),
                      face=-1, items=items, wiggle=1.0 if dancing else 0)
        for kind, ft in flying:
            k = t - ft
            if kind == "ball":
                bk = ramp(t, ft, ft + 1.6)
                bx = lerp(900, 470, bk)
                by = 610 + bounce_y(t, ft, 3, 220, 1.6)
                if t > ft + 1.6:
                    bx, by = 470, 625
                stuck_item(c, "ball", bx, by, 1.5, -bk * 600, t, sparkle=1.0)
            elif k < 1.4:
                x0 = {"flower": 840, "duck": 800, "sock": 820}[kind]
                dirx = {"flower": 1, "duck": 1.4, "sock": 0.8}[kind]
                stuck_item(c, kind, x0 + k * 260 * dirx, 540 - k * 420 + k * k * 420, 1.3, k * 400, t)
        if happy and t < s.M("b1") + 1.0:
            sparkles(c, 470, 560, t, 10, 90)
        c.restore()
    s.draw = d8
    S.append(s)

    # ---------------- 7. COUNT THE BOUNCES
    s = Scene("game", music="theme", trans="boots", music_gain=0.7)
    s.say("biscuit", "Let's play! Count the bounces with me!", key="b1", gap=0.3)
    s.mark("c0")
    for i, w in enumerate(["One!", "Two!", "Three!", "Four!", "Five!"]):
        s.mark(f"n{i}"); s.fx("boing", gain=0.6); s.fx(f"ding{i + 1}")
        st = s.say(ALL, w, gap=0.0)
        s.t = st + 1.0
    s.mark("throw"); s.fx("whistle", gain=0.6)
    s.wait(1.0); s.fx("pok")
    s.say("prickles", "[laugh] Oopsie-prickle!", key="oops", gap=0.3)
    s.fx("cheer", gain=0.5)
    s.wait(1.2)

    def d9(c, t, s=s):
        cam(c, 1.25, 620, 460)
        garden(c, t, props=("tree",))
        draw_mittens(c, 250, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, -0.3))
        draw_biscuit(c, 480, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.7, wag=1.6, look=(0.5, -0.6))
        tw = s.M("throw")
        stuck = t > tw + 1.0
        draw_prickles(c, 900, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, items=["ball"] if stuck else [],
                      squash=0.3 * math.sin((t - tw - 1.0) * 14) * max(0, 1 - (t - tw - 1.0) * 2) if stuck else 0)
        if s.M("c0") < t < tw:
            k = ((t - s.M("c0")) % 1.0)
            stuck_item(c, "ball", 560, 600 + hop(k, 0, 1, 230), 1.4, 0, t)
        elif tw <= t < tw + 1.0:
            k = ramp(t, tw, tw + 1.0)
            stuck_item(c, "ball", lerp(560, 850, k), 600 - math.sin(k * math.pi) * 200, 1.4, k * 720, t)
        c.restore()
        cols = [0xFF3D8BFF, 0xFFE8343B, 0xFFFFC21A, 0xFF6CCB5F, 0xFF8E5CF7]
        for i in range(5):
            nt = s.M(f"n{i}")
            if nt < t < tw + 0.3:
                text(c, str(i + 1), 330 + i * 155, 130, 100, cols[i], scale=back_out((t - nt) / 0.3), ow=10)
    s.draw = d9
    S.append(s)

    # ---------------- 8. GOODBYE
    s = Scene("bye", music="rainbow", trans="rainbow", music_gain=0.8)
    s.wait(0.3)
    s.say("mittens", "When you lose something, ask your friends to help.", key="m1", gap=0.3)
    s.say("biscuit", "And always look behind you!", key="b1", gap=0.3)
    s.say("prickles", "Especially if you're a hedgehog! [laugh]", key="p1", gap=0.4)
    s.mark("hug"); s.fx("sparkle", s.t + 0.6)
    s.wait(1.2)
    s.say("biscuit", "[sigh] Best ball day ever.", key="best", gap=0.5)
    s.say("biscuit", "Bye, friends! See you next time!", key="b2", gap=0.2)
    s.say("mittens", "Bye-bye.", key="m2", gap=0.5)
    s.mark("end"); s.fx("choir", gain=0.5); s.wait(3.6)

    def d10(c, t, s=s):
        if t < s.M("end"):
            cam(c, 1.25, 620, 460)
            garden(c, t, props=("tree",))
            wave = math.sin(t * 6)
            hk = ease(ramp(t, s.M("hug"), s.M("hug") + 1.0))
            waving = t > s.M("b2")
            draw_mittens(c, lerp(330, 470, hk), GY, 0.95, t, mouth=s.mouth("mittens", t), face=1,
                         paw_up=0.5 + 0.5 * wave if waving else 0, lid=lerp(0.25, 0.5, hk))
            draw_prickles(c, lerp(820, 700, hk), GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1)
            draw_biscuit(c, 590, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.7, wag=lerp(1.6, 0.7, hk),
                         blink=1.0 if s.M("best") < t < s.M("best_end") else None)
            if hk > 0:
                for i in range(4):
                    ph = ((t - s.M("hug")) * 0.6 + i / 4) % 1
                    hx, hy = 520 + i * 45, 470 - ph * 120
                    hp_ = skia.Path()
                    hp_.moveTo(hx, hy + 8)
                    hp_.cubicTo(hx - 12, hy - 2, hx - 6, hy - 12, hx, hy - 5)
                    hp_.cubicTo(hx + 6, hy - 12, hx + 12, hy - 2, hx, hy + 8)
                    c.drawPath(hp_, fill(alpha(0xFFFF6B9A, (1 - ph) * hk)))
            c.restore()
        else:
            tt = t - s.M("end")
            hero_rays(c, t * 0.3, 0xFF8FD6FF, 0xFFA8E0FF)
            k = ease_out(tt / 0.8)
            text(c, "BISCUIT & FRIENDS", 640, 150, 96, 0xFFFFD93B, scale=k, ow=14)
            draw_mittens(c, 380, 600, 0.95 * k, t, paw_up=0.5 + 0.5 * math.sin(t * 6))
            draw_biscuit(c, 640, 610, 1.05 * k, t, ears=0.7, wag=1.6)
            draw_prickles(c, 900, 610, 1.0 * k, t, face=-1)
            text(c, "SEE YOU NEXT TIME!", 640, 680, 44, 0xFFFFFFFF, scale=back_out((tt - 0.4) / 0.4))
    s.draw = d10
    S.append(s)
    return S
