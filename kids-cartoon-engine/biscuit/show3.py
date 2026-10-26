"""Biscuit & Friends, Episode 3: Sleepy Time! Scene timing + drawing."""
import math
import numpy as np
import show  # shared Biscuit sound effects, voice cache, finish()
import show2  # bath sound effects (scrub is reused for brushing)
from show import *  # noqa: F401,F403
import audio as A

STEP_COLS3 = [0xFF3D8BFF, 0xFFFFC21A, 0xFFFF9BD5, 0xFF8E5CF7]
STEP_NAMES3 = ["BRUSH", "STORY", "CUDDLE", "GOODNIGHT"]
BED_X = 600


def steps_bar3(c, t, s, done_marks):
    for i in range(4):
        x, y = 430 + i * 140, 66
        done = done_marks[i] is not None and t > s.M(done_marks[i])
        circle(c, x, y, 36, STEP_COLS3[i] if done else 0xFFFFFFFF, 5)
        if done:
            k = back_out((t - s.M(done_marks[i])) / 0.3)
            p = skia.Path(); p.moveTo(x - 14 * k, y); p.lineTo(x - 3 * k, y + 12 * k); p.lineTo(x + 16 * k, y - 12 * k)
            c.drawPath(p, stroke(0xFFFFFFFF, 8))
        else:
            text(c, str(i + 1), x, y, 40, STEP_COLS3[i], ow=0)
        text(c, STEP_NAMES3[i], x, y + 54, 20, 0xFFFFFFFF, ow=4)


def world3(c, t, sun_set=0.0, sunset=0.0, night=0.0, bed=True):
    garden(c, t, props=("tree", "box"), sun_set=sun_set)
    dusk_overlay(c, night, sunset)
    night_sky(c, t, night)
    if bed:
        dog_bed(c, BED_X, 660)


def zzz(c, x, y, t, a=1.0):
    for i in range(3):
        ph = (t * 0.5 + i / 3) % 1
        text(c, "z", x + ph * 40, y - ph * 70, 22 + 16 * ph, alpha(0xFFFFFFFF, (1 - ph) * a), tf=ROUND_TF, ow=4)


# ===================================================================== scenes
def build():
    S = []

    # ---------------- TITLE
    s = Scene("title", music="brave", trans=None, music_gain=1.0)
    s.fx("sparkle", 0.6)
    s.t = 3.0

    def d0(c, t, s=s):
        hero_rays(c, t * 0.3, 0xFF26336E, 0xFF2F3E80)
        night_sky(c, t, 1.0)
        k = back_out(t / 0.5)
        text(c, "BISCUIT & FRIENDS", 640, 260, 64, 0xFFFFFFFF, scale=k, ow=12)
        text(c, "SLEEPY TIME!", 640, 360, 110, 0xFFFFD93B, scale=back_out((t - 0.3) / 0.5), ow=14)
        dog_bed(c, 640, 720, 1.0)
        draw_biscuit(c, 640, 700, 1.0, t, blink=1.0, ears=-0.3, wag=0.1)
        zzz(c, 700, 540, t)
    s.draw = d0
    S.append(s)

    # ---------------- 1. NOT SLEEPY
    s = Scene("evening", music="theme", trans="bubble", music_gain=0.5)
    s.fx("boing", 0.4); s.fx("boing", 1.0); s.fx("wag", 0.2)
    s.wait(1.2)
    s.say("biscuit", "[laugh] Let's play! Let's play! I'm not sleepy at all!", key="b1", gap=0.3)
    s.say("mittens", "[sigh] Biscuit, the sun is going down. It's almost bedtime.", key="m1", gap=0.3)
    s.say("biscuit", "But I'm not sleepy! Not one bit!", key="b2", gap=0.7)

    def d1(c, t, s=s):
        k = ramp(t, 0, s.dur)
        cam(c, 1.3, 600, 470)
        world3(c, t, sun_set=lerp(0.35, 0.85, k), sunset=lerp(0.4, 1.0, k), night=lerp(0.0, 0.25, k))
        bx = 420 + math.sin(t * 2) * 30
        draw_biscuit(c, bx, GY + hop((t % 0.6), 0, 0.6, 50), 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.7, wag=1.8)
        stuck_item(c, "ball", bx + 90, 600 + hop((t + 0.3) % 0.6, 0, 0.6, 120), 1.3, t * 300, t)
        draw_mittens(c, 820, GY, 0.95, t, mouth=s.mouth("mittens", t), face=-1, look=(-1, 0), lid=0.45)
        c.restore()
    s.draw = d1
    S.append(s)

    # ---------------- 2. WIDE-AWAKE PRICKLES + THE PLAN
    s = Scene("plan", music="theme", trans="spin", music_gain=0.5)
    s.fx("pok", 0.5)
    s.wait(0.7)
    s.say("prickles", "[laugh] Hi! I'm wide awake! Hedgehogs love the nighttime!", key="p1", gap=0.3)
    s.say("mittens", "Let's do our bedtime steps. Brush, story, cuddle, goodnight.", key="m1", gap=0.3)
    s.say("narr", "Four bedtime steps. Let's count them!", key="n1", gap=0.2)
    for i, w in enumerate(["One!", "Two!", "Three!", "Four!"]):
        s.mark(f"st{i}"); s.fx(f"ding{i + 1}")
        s.say("narr", w, gap=0.45)
    s.wait(0.4)

    def d2(c, t, s=s):
        cam(c, 1.3, 600, 470)
        world3(c, t, sun_set=0.95, sunset=1.0, night=0.4)
        draw_biscuit(c, 380, GY, 1.0, t, face=1, ears=0.6, wag=1.2, look=(1, 0))
        draw_mittens(c, 580, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0), lid=0.45)
        pk = back_out(ramp(t, 0.3, 0.8))
        draw_prickles(c, 860, GY + (1 - pk) * 80, 1.0, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.5, -0.3))
        c.restore()
        for i in range(4):
            st = s.M(f"st{i}")
            if t > st:
                x, y = 430 + i * 140, 120
                k = back_out((t - st) / 0.3)
                circle(c, x, y, 50 * k, STEP_COLS3[i], 6)
                text(c, str(i + 1), x, y, 56 * k, 0xFFFFFFFF, ow=6)
                text(c, STEP_NAMES3[i], x, y + 74, 26 * k, 0xFFFFFFFF, ow=5)
    s.draw = d2
    S.append(s)

    # ---------------- 3. STEP 1: BRUSH (kids brush along)
    s = Scene("brush", music="theme", trans="boots", music_gain=0.45)
    s.wait(0.3)
    s.say("narr", "Step one. Brush your teeth! Can you brush with Biscuit?", key="n1", gap=0.2)
    for i, w in enumerate(["top", "bottom"]):
        s.say(["biscuit", "mittens"], f"Brush the {w} teeth!", key=f"br{i}", gap=0.1)
        s.mark(f"b{i}"); s.fx("scrub"); s.wait(3.0)
    s.say("biscuit", "[laugh] Minty fresh!", key="fresh", gap=0.2)
    s.mark("done1"); s.fx("ding5"); s.fx("sparkle")
    s.wait(0.8)

    def d3(c, t, s=s):
        cam(c, 1.5, 560, 470)
        world3(c, t, sun_set=1.0, sunset=1.0, night=0.55, bed=False)
        brushing = any(s.M(f"b{i}") < t < s.M(f"b{i}") + 3.0 for i in range(2))
        draw_biscuit(c, 470, GY, 1.0, t, mouth=0.4 if brushing else s.mouth("biscuit", t), face=1, ears=0.6, wag=1.0,
                     blink=1.0 if s.M("fresh") < t < s.M("fresh_end") else None)
        hy = GY - 128 + 26
        toothbrush(c, 505 + (math.sin(t * 18) * 10 if brushing else 0), hy + (8 if t > s.M("b1") else -4), -10, 0.9)
        if brushing:
            for i in range(4):
                bubble(c, 520 + hsh(i, int(t * 4)) * 50, hy - 20 + hsh(i, int(t * 4) + 1) * 30, 6 + 4 * hsh(i, 5), t)
        draw_mittens(c, 700, GY, 0.95, t, mouth=s.mouth("mittens", t), face=-1, look=(-1, 0), lid=0.45)
        if t > s.M("done1"):
            sparkles(c, 470, 470, t, 8, 80)
        c.restore()
        for i, w in enumerate(["TOP", "BOTTOM"]):
            prompt(c, f"BRUSH THE {w} TEETH!", t, s.M(f"br{i}"), s.M(f"b{i}") + 3.0, y=180, size=64)
        steps_bar3(c, t, s, ["done1", None, None, None])
    s.draw = d3
    S.append(s)

    # ---------------- 4. STEP 2: STORY (count the stars, the big yawn)
    s = Scene("story", music="brave", trans="bubble", music_gain=0.55)
    s.wait(0.3)
    s.say("mittens", "Step two. A bedtime story. Once upon a time, there were five little stars.", key="m1", gap=0.2)
    s.say("narr", "Let's count the stars!", key="n1", gap=0.2)
    for i, w in enumerate(["One!", "Two!", "Three!", "Four!", "Five!"]):
        s.mark(f"s{i}"); s.fx(f"ding{i + 1}", gain=0.7)
        s.say("narr", w, gap=0.45)
    s.say("mittens", "And all the little stars said... goodnight.", key="m2", gap=0.3)
    s.mark("yawn")
    s.say("biscuit", "[sigh] I'm a little bit sleepy.", key="b1", gap=0.2)
    s.say("narr", "Uh oh! Biscuit did a big yawn! Can you do a big yawn?", key="n2", gap=0.1)
    s.mark("kids"); s.wait(3.5)
    s.say("prickles", "Not me! [laugh] I'm wide awake!", key="p1", gap=0.3)
    s.mark("done2"); s.fx("ding6", gain=0.6)
    s.wait(0.6)

    def d4(c, t, s=s):
        cam(c, 1.15, 620, 420)
        world3(c, t, sun_set=1.0, sunset=1.0, night=0.8)
        yawn = s.M("yawn") - 0.2 < t < s.M("b1_end") + 0.3
        draw_biscuit(c, BED_X, 640, 1.0, t, mouth=0.9 if yawn and t < s.M("b1") + 0.6 else s.mouth("biscuit", t), face=1,
                     ears=-0.2, wag=0.3, blink=1.0 if yawn else None, sit=1)
        draw_mittens(c, 360, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, -0.5), lid=0.5)
        draw_prickles(c, 880, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.5, -0.8))
        c.restore()
        for i in range(5):
            st = s.M(f"s{i}")
            if t > st:
                x, y = 300 + i * 170, 170 + (i % 2) * 50
                story_star(c, x, y, 46, t, (t - st) / 0.4)
                text(c, str(i + 1), x, y + 80, 40, 0xFFFFFFFF, ow=6)
        prompt(c, "BIG YAWN!", t, s.M("kids") - 0.2, s.M("p1"), y=400, size=90)
        steps_bar3(c, t, s, ["_", "done2", None, None])
    s.m["_"] = -1.0
    s.draw = d4
    S.append(s)

    # ---------------- 5. STEP 3: CUDDLE (the red ball callback)
    s = Scene("cuddle", music="brave", trans="spin", music_gain=0.5)
    s.wait(0.3)
    s.say("mittens", "Step three. Cuddle your favorite toy.", key="m1", gap=0.2)
    s.mark("ball"); s.fx("boing"); s.fx("wag", s.t + 0.8)
    s.wait(1.0)
    s.say("biscuit", "My red ball! [sigh] Night night, ball.", key="b1", gap=0.3)
    s.mark("done3"); s.fx("ding7", gain=0.6); s.fx("sparkle")
    s.wait(0.8)

    def d5(c, t, s=s):
        k = ease(ramp(t, s.M("ball"), s.M("ball") + 1.0))
        cam(c, lerp(1.15, 1.9, k), lerp(620, BED_X, k), lerp(420, 520, k))
        world3(c, t, sun_set=1.0, sunset=1.0, night=0.9)
        draw_biscuit(c, BED_X, 640, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=-0.2, wag=0.4, sit=1,
                     blink=1.0 if t > s.M("b1") + 1.0 else None)
        bt = s.M("ball")
        bx = lerp(BED_X + 200, BED_X + 40, ease(ramp(t, bt, bt + 0.8)))
        by = 600 + (hop(t, bt, 0.8, 80) if t < bt + 0.8 else 0)
        if t > bt:
            stuck_item(c, "ball", bx, by, 1.2, 0, t)
        draw_mittens(c, 360, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0), lid=0.55)
        draw_prickles(c, 900, GY, 1.0, t, face=-1, look=(-1, 0))
        if t > s.M("b1") + 0.5:
            for i in range(3):
                ph = ((t - s.M("b1")) * 0.6 + i / 3) % 1
                hx, hy = BED_X - 20 + i * 30, 500 - ph * 90
                hp_ = skia.Path()
                hp_.moveTo(hx, hy + 8)
                hp_.cubicTo(hx - 12, hy - 2, hx - 6, hy - 12, hx, hy - 5)
                hp_.cubicTo(hx + 6, hy - 12, hx + 12, hy - 2, hx, hy + 8)
                c.drawPath(hp_, fill(alpha(0xFFFF6B9A, 1 - ph)))
        c.restore()
        steps_bar3(c, t, s, ["_", "_", "done3", None])
    s.m["_"] = -1.0
    s.draw = d5
    S.append(s)

    # ---------------- 6. STEP 4: GOODNIGHT CHANT (the repeating hook)
    s = Scene("goodnight", music="rainbow", trans="bubble", music_gain=0.45)
    s.wait(0.3)
    s.say("narr", "Step four. Let's say goodnight! Wave with Biscuit!", key="n1", gap=0.3)
    things = ["tree", "stars", "moon"]
    for i, w in enumerate(things):
        s.say(["biscuit", "mittens"], f"Goodnight, {w}!", key=f"g{i}", gap=0.1)
        s.mark(f"k{i}"); s.wait(3.0)
    s.say(["biscuit", "mittens"], "Goodnight, friends!", key="g3", gap=0.4)
    s.mark("done4"); s.fx("ding8", gain=0.5); s.fx("sparkle")
    s.wait(0.6)
    for i in range(3):
        s.duck_zero.append((s.M(f"k{i}") - 0.1, s.M(f"k{i}") + 2.9))

    def d6(c, t, s=s):
        cam(c, 1.1, 640, 400)
        world3(c, t, sun_set=1.0, sunset=1.0, night=1.0)
        waving = t > s.M("n1")
        wave = 0.5 + 0.5 * math.sin(t * 7)
        draw_biscuit(c, BED_X, 640, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.2, wag=0.6 + 0.6 * wave if waving else 0.3, sit=1)
        stuck_item(c, "ball", BED_X + 60, 610, 1.1, 0, t)
        draw_mittens(c, 380, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, lid=0.5, paw_up=wave if waving else 0)
        draw_prickles(c, 900, GY, 1.0, t, face=-1, look=(-0.5, -0.8))
        # highlight what we're saying goodnight to
        for i, w in enumerate(things):
            if s.M(f"g{i}") < t < s.M(f"k{i}") + 3.0:
                p = (0.5 + 0.5 * math.sin(t * 6))
                spot = {"tree": (1110, 250), "stars": (330, 150), "moon": (960, 160)}[w]
                c.drawCircle(spot[0], spot[1], 110 + 10 * p, stroke(alpha(0xFFFFD93B, 0.9), 8))
        c.restore()
        for i, w in enumerate(things):
            prompt(c, f"GOODNIGHT, {w.upper()}!", t, s.M(f"k{i}") - 0.1, s.M(f"k{i}") + 3.0, y=200, size=70)
        steps_bar3(c, t, s, ["_", "_", "_", "done4"])
    s.m["_"] = -1.0
    s.draw = d6
    S.append(s)

    # ---------------- 7. SLEEP, THEN MORNING (Prickles' turn to sleep)
    s = Scene("sleep", music="brave", trans="fade", music_gain=0.4)
    s.wait(1.6)
    s.say("prickles", "Shh... They're sleeping. I'll keep watch all night.", key="p1", gap=0.3)
    s.wait(2.4)
    s.say("narr", "Goodnight, friends. Sweet dreams!", key="n1", gap=0.6)
    s.mark("end"); s.fx("choir", gain=0.35); s.wait(5.0)

    def d7(c, t, s=s):
        if t < s.M("end"):
            m = ease(ramp(t, s.M("morning"), s.M("morning") + 1.8))
            cam(c, 1.15, 620, 420)
            world3(c, t, sun_set=lerp(1.0, 0.2, m), sunset=lerp(0.0, 0.5, m) * (1 - m) * 2, night=1.0 - m)
            awake = t > s.M("b1") - 0.3
            draw_biscuit(c, BED_X, 640, 1.0, t, mouth=s.mouth("biscuit", t), face=1, sit=1, ears=0.6 if awake else -0.3,
                         wag=1.6 if awake else 0.0, blink=None if awake else 1.0)
            stuck_item(c, "ball", BED_X + 60, 610, 1.1, 0, t)
            draw_mittens(c, 400, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, blink=1.0 if t < s.M("m1") - 0.5 else None, lid=0.5)
            if not awake:
                zzz(c, BED_X + 40, 480, t)
                zzz(c, 440, 500, t + 0.4)
            curled = t > s.M("curl")
            if curled:
                draw_prickles(c, 900, GY, 1.0, t, roll=0)
                zzz(c, 930, 540, t)
            else:
                draw_prickles(c, 900, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.6, -0.4),
                              blink=1.0 if s.M("p2") < t < s.M("p2_end") and int(t * 2) % 2 == 0 else None)
            c.restore()
        else:
            tt = t - s.M("end")
            hero_rays(c, t * 0.2, 0xFF26336E, 0xFF2F3E80)
            night_sky(c, t, 1.0)
            k = ease_out(tt / 0.8)
            text(c, "GOODNIGHT!", 640, 230, 110, 0xFFFFD93B, scale=k, ow=14)
            dog_bed(c, 640, 720, 1.0)
            draw_biscuit(c, 640, 700, 1.0, t, blink=1.0, ears=-0.3, wag=0.1, sit=1)
            zzz(c, 700, 540, t)
    s.draw = d7
    S.append(s)
    return finish(S)
