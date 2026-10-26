"""Biscuit & Friends, Episode 2: Bubble Bath Time! Scene timing + drawing."""
import math
import numpy as np
import show  # registers the shared Biscuit sound effects and voice cache
from show import *  # noqa: F401,F403
import audio as A
import os


# ---------------------------------------------------------------- bath sound effects
def sfx_pour(d=2.5):
    t = A.t_arr(d)
    y = A.bp(A.noise(d), 300, 3000) * np.minimum(1, np.minimum(t * 4, (d - t) * 4)) * (0.8 + 0.2 * np.sin(2 * np.pi * 7 * t))
    return A.norm(y, 0.35)

def sfx_scrub(d=1.4):
    t = A.t_arr(d)
    y = A.bp(A.noise(d), 1500, 6000) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)) ** 2 * np.minimum(1, (d - t) * 4)
    return A.norm(y, 0.3)

def sfx_shake():
    d = 1.0
    t = A.t_arr(d)
    y = A.lp(A.noise(d), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.sin(np.linspace(0, np.pi, len(t)))
    return A.norm(y, 0.45)

A.SFX.update({"pour": sfx_pour, "scrub": sfx_scrub, "shake": sfx_shake})

STEP_COLS = [0xFF3D8BFF, 0xFFFF9BD5, 0xFFFFC21A, 0xFF6CCB5F, 0xFF8E5CF7]
STEP_NAMES = ["WATER", "BUBBLES", "SCRUB", "RINSE", "DRY"]


def steps_bar(c, t, s, done_marks):
    """Five numbered bath steps across the top, checked off one by one."""
    for i in range(5):
        x, y = 360 + i * 140, 66
        done = done_marks[i] is not None and t > s.M(done_marks[i])
        circle(c, x, y, 36, STEP_COLS[i] if done else 0xFFFFFFFF, 5)
        if done:
            k = back_out((t - s.M(done_marks[i])) / 0.3)
            p = skia.Path(); p.moveTo(x - 14 * k, y); p.lineTo(x - 3 * k, y + 12 * k); p.lineTo(x + 16 * k, y - 12 * k)
            c.drawPath(p, stroke(0xFFFFFFFF, 8))
        else:
            text(c, str(i + 1), x, y, 40, STEP_COLS[i], ow=0)
        text(c, STEP_NAMES[i], x, y + 54, 20, 0xFFFFFFFF, ow=4)


def floating_bubbles(c, t, x0, y0, n=8, spread=200, seed=0, pop_x=None):
    for i in range(n):
        ph = (t * 0.25 + hsh(i, seed)) % 1
        bx = x0 + (hsh(i, seed + 1) - 0.5) * spread + math.sin(t * 1.5 + i) * 20
        by = y0 - ph * 260
        bubble(c, bx, by, 12 + hsh(i, seed + 2) * 14, t)


# ===================================================================== scenes
def build():
    S = []

    # ---------------- TITLE
    s = Scene("title", music="theme", trans=None, music_gain=1.2)
    for i in range(4):
        s.fx("pop", 0.5 + i * 0.35)
    s.fx("sparkle", 1.8)
    s.t = 3.0

    def d0(c, t, s=s):
        hero_rays(c, t, 0xFF8FD6FF, 0xFFA8E0FF)
        floating_bubbles(c, t, 640, 760, 14, 1100, 3)
        k = back_out((t - 0.4) / 0.5)
        text(c, "BISCUIT & FRIENDS", 640, 140, 72, 0xFFFFFFFF, scale=k, ow=12)
        text(c, "BUBBLE BATH TIME!", 640, 250, 100, 0xFFFFD93B, scale=back_out((t - 0.8) / 0.5), ow=14)
        tub_back(c, 640, 690, 1.0)
        draw_biscuit(c, 640, 600, 1.0, t, ears=0.6, wag=1.4)
        tub_front(c, 640, 690, 1.0, water=0.7, t=t, bubbles=1.0)
    s.draw = d0
    S.append(s)

    # ---------------- 1. MUD!
    s = Scene("mud", music="theme", trans="bubble", music_gain=0.5)
    s.fx("patter", 0.1)
    s.wait(1.4); s.mark("jump"); s.fx("splash", s.t + 0.5)
    s.wait(1.0)
    s.fx("wag", s.t + 0.2)
    s.say("biscuit", "[laugh] Mud! Mud! I love mud!", key="b1", gap=0.4)
    s.mark("mittens"); s.fx("mrrp", s.t + 0.6)
    s.wait(0.9)
    s.say("mittens", "Biscuit! You're all muddy. It's bath time.", key="m1", gap=0.3)
    s.fx("wahwah", s.t, 0.6)
    s.say("biscuit", "[sigh] No bath! Baths are scary.", key="b2", gap=0.8)

    def d1(c, t, s=s):
        z, cx, cy = 1.25, 600, 460
        if t > s.M("b2"):
            k = ease(ramp(t, s.M("b2"), s.M("b2") + 0.5))
            z, cx, cy = lerp(1.25, 1.9, k), lerp(600, 600, k), lerp(460, 480, k)
        cam(c, z, cx, cy)
        garden(c, t, props=("tree", "box"))
        mud_puddle(c, 600, 668, 170, t)
        jt = s.M("jump")
        bx = kf(t, [(0, -150), (jt, 380), (jt + 0.5, 600)])
        by = GY + 10 + (hop(t, jt, 0.5, 140) if t < jt + 0.5 else 0) - (abs(math.sin(t * 12)) * 14 if t < jt else 0)
        mud = ease(ramp(t, jt + 0.45, jt + 0.6))
        sad = ease(ramp(t, s.M("b2"), s.M("b2") + 0.4))
        draw_biscuit(c, bx, by, 1.0, t, mouth=s.mouth("biscuit", t), face=1 if t < jt + 0.5 else -1, mud=mud,
                     sad=sad, ears=lerp(0.6, -1, sad), wag=lerp(1.6, 0.2, sad))
        splash_fx(c, 600, 668, jt + 0.5, t, 1.3, 0xFF8B5A2B)
        mt = s.M("mittens")
        if t > mt:
            mx = kf(t, [(mt, 1450), (mt + 0.9, 860)])
            draw_mittens(c, mx, GY, 0.95, t, mouth=s.mouth("mittens", t), face=-1, look=(-1, 0))
        c.restore()
    s.draw = d1
    S.append(s)

    # ---------------- 2. BUBBLES ARE FUN (Prickles' spikes pop them)
    s = Scene("plan", music="theme", trans="spin", music_gain=0.5)
    s.wait(0.6); s.mark("blow")
    s.wait(1.4)
    s.say("prickles", "[laugh] Bath time can be fun! Look, bubbles!", key="p1", gap=0.3)
    s.mark("touch"); s.fx("pop", s.t + 0.5); s.fx("pop", s.t + 0.9); s.fx("pop", s.t + 1.2)
    s.wait(1.4)
    s.say("prickles", "Oopsie-prickle! My spikes pop them!", key="p2", gap=0.3)
    s.say("mittens", "Let's do bath time together. One step at a time.", key="m1", gap=0.3)
    s.say("biscuit", "Okay. I'll try.", key="b1", gap=0.4)
    s.say("mittens", "Bath time has five steps. Let's count them!", key="m2", gap=0.2)
    for i, w in enumerate(["One!", "Two!", "Three!", "Four!", "Five!"]):
        s.mark(f"st{i}"); s.fx(f"ding{i + 1}")
        s.say("narr", w, gap=0.4)
    s.wait(0.5)

    def d2(c, t, s=s):
        cam(c, 1.3, 600, 470)
        garden(c, t, props=("tree",))
        draw_biscuit(c, 380, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, mud=1.0,
                     sad=0.6 if t < s.M("b1") else 0, ears=-0.6 if t < s.M("b1") else 0.3, wag=0.4, look=(1, -0.3))
        draw_mittens(c, 580, GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0))
        draw_prickles(c, 860, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.6, -0.6))
        # bubble wand
        c.drawLine(800, 600, 760, 540, stroke(INK, 7)); c.drawLine(800, 600, 760, 540, stroke(0xFFFF9BD5, 4))
        c.drawCircle(752, 528, 14, stroke(0xFFFF9BD5, 5))
        bt = s.M("blow")
        if t > bt:
            for i in range(9):
                st = bt + i * 0.35
                if t < st:
                    continue
                age = t - st
                bx = 740 - age * 60 - hsh(i, 5) * 40
                by = 520 - age * 50 + math.sin(age * 3 + i) * 12
                popped_at = None
                tt = s.M("touch")
                if i < 3:
                    popped_at = tt + 0.5 + [0, 0.4, 0.7][i]
                    k = ramp(t, tt, popped_at)
                    if t > tt:
                        bx = lerp(bx, 830 + i * 14, k)
                        by = lerp(by, 560 - i * 20, k)
                if popped_at and t > popped_at:
                    bubble(c, bx, by, 18, t, pop=min((t - popped_at) / 0.3, 1))
                elif by > 120:
                    bubble(c, bx, by, 14 + hsh(i, 7) * 10, t)
        c.restore()
        for i in range(5):
            st = s.M(f"st{i}")
            if t > st:
                x, y = 360 + i * 140, 120
                k = back_out((t - st) / 0.3)
                circle(c, x, y, 50 * k, STEP_COLS[i], 6)
                text(c, str(i + 1), x, y, 56 * k, 0xFFFFFFFF, ow=6)
                text(c, STEP_NAMES[i], x, y + 74, 26 * k, 0xFFFFFFFF, ow=5)
    s.draw = d2
    S.append(s)

    # ---------------- 3. STEPS 1 + 2: WATER AND BUBBLES (count the pops)
    s = Scene("fill", music="search", trans="boots", music_gain=0.6)
    s.wait(0.4)
    s.say("narr", "Step one. With a grown-up, fill the tub with warm water.", key="s1", gap=0.1)
    s.mark("pour"); s.fx("pour")
    s.wait(2.3)
    s.mark("paw")
    s.fx("wag", s.t + 0.6)
    s.say("biscuit", "Ooh. It's warm!", key="warm", gap=0.3)
    s.mark("done1"); s.fx("ding3")
    s.say("narr", "Step two. Add the bubbles!", key="s2", gap=0.1)
    s.mark("foam"); s.fx("sparkle")
    s.wait(1.4)
    s.mark("done2"); s.fx("ding5")
    s.say("narr", "Let's count the pops!", key="count", gap=0.2)
    for i, w in enumerate(["One!", "Two!", "Three!"]):
        s.mark(f"n{i}"); s.fx("pop"); s.fx(f"ding{i + 1}")
        s.say("narr", w, gap=0.45)
    s.say("prickles", "Pop, pop, pop!", key="oops", gap=0.6)

    def d3(c, t, s=s):
        cam(c, 1.25, 620, 460)
        garden(c, t, props=("tree",))
        water = ease(ramp(t, s.M("pour"), s.M("pour") + 2.3))
        foam = ease(ramp(t, s.M("foam"), s.M("foam") + 1.2))
        tub_back(c, 640, 700, 1.0)
        tub_front(c, 640, 700, 1.0, water=water * 0.75, t=t, bubbles=foam)
        # hose pouring
        if s.M("pour") < t < s.M("pour") + 2.4:
            for k in range(8):
                ph = (t * 3 + k / 8) % 1
                circle(c, 540 + ph * 60, 470 + ph * 120, 8, 0xCC7FD3FF, 0)
            c.drawLine(470, 470, 540, 470, stroke(INK, 14)); c.drawLine(470, 470, 540, 470, stroke(0xFF6CCB5F, 9))
        paw = s.M("paw") < t < s.M("done1") + 0.5
        draw_biscuit(c, 360, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, mud=1.0, tilt=-12 if paw else 0,
                     ears=0.5 if t > s.M("warm") else -0.4, wag=1.2 if t > s.M("warm") else 0.3, look=(1, 0.4))
        draw_mittens(c, 170, GY, 0.9, t, face=1, look=(1, 0))
        draw_prickles(c, 960, GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1, look=(-0.5, -0.8))
        # three foam bubbles drift to Prickles and pop on his spikes
        for i in range(3):
            nt = s.M(f"n{i}")
            st = nt - 0.9
            if st < t < nt + 0.4:
                k = ramp(t, st, nt)
                bx, by = lerp(700 + i * 30, 900, k), lerp(560, 580 - i * 25, k) - math.sin(k * math.pi) * 60
                bubble(c, bx, by, 22, t, pop=0 if t < nt else (t - nt) / 0.3)
        c.restore()
        for i in range(3):
            nt = s.M(f"n{i}")
            if nt < t < s.M("oops_end"):
                text(c, str(i + 1), 520 + i * 120, 190, 90, [0xFF7FD3FF, 0xFFFF9BD5, 0xFFFFD93B][i], scale=back_out((t - nt) / 0.3), ow=10)
        steps_bar(c, t, s, ["done1", "done2", None, None, None])
    s.draw = d3
    S.append(s)

    # ---------------- 4. STEP 3: SCRUB, SCRUB, SCRUB (kids scrub along)
    s = Scene("scrub", music="theme", trans="bubble", music_gain=0.5)
    s.fx("splash_small", 0.3)
    s.wait(0.6)
    s.say("narr", "Step three. Scrub, scrub, scrub! Can you scrub with Biscuit?", key="s3", gap=1.5)
    parts = [("tummy", "body"), ("ears", "ears"), ("paws", "paws"), ("tail", None)]
    for i, (word, part) in enumerate(parts):
        s.say(["biscuit", "mittens"], f"Scrub your {word}!", key=f"sc{i}", gap=0.1)
        s.mark(f"kids{i}"); s.fx("scrub"); s.wait(3.0)
        if i == 0:
            s.say("narr", "Is Biscuit clean yet?", key="ask1", gap=0.1)
            s.mark("no_kids"); s.wait(3.0)
            s.say("narr", "No! Keep scrubbing!", key="no", gap=0.3)
    s.say("narr", "Now is Biscuit clean?", key="ask2", gap=0.1)
    s.mark("yes_kids"); s.wait(3.0)
    s.say("narr", "Yes!", key="yes", gap=0.2)
    s.mark("done3"); s.fx("ding6"); s.fx("sparkle")
    s.say("biscuit", "[laugh] Scrubbing tickles!", key="tickle", gap=0.6)

    def d4(c, t, s=s):
        cam(c, 1.45, 640, 470)
        garden(c, t, props=("tree",))
        tub_back(c, 640, 700, 1.0)
        remaining = [p for i, (w, p) in enumerate(parts) if p and t < s.M(f"kids{i}") + 1.5]
        mud = 1.0
        scrubbing = any(s.M(f"kids{i}") < t < s.M(f"kids{i}") + 3.0 for i in range(len(parts)))
        draw_biscuit(c, 640 + (math.sin(t * 14) * 5 if scrubbing else 0), 596, 1.0, t, mouth=s.mouth("biscuit", t), face=1,
                     mud=mud if remaining else 0, mud_parts=tuple(remaining), ears=0.6, wag=1.0,
                     blink=1.0 if s.M("tickle") < t < s.M("tickle_end") else None)
        tub_front(c, 640, 700, 1.0, water=0.75, t=t, bubbles=1.0)
        draw_mittens(c, 330, GY, 0.9, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0), paw_up=0.5 + 0.5 * math.sin(t * 10) if scrubbing else 0)
        draw_prickles(c, 990, GY, 0.95, t, face=-1, look=(-1, 0))
        if scrubbing:
            for i in range(5):
                bubble(c, 600 + hsh(i, int(t * 3)) * 90, 470 + hsh(i, int(t * 3) + 1) * 60, 10 + 6 * hsh(i, 9), t)
        if t > s.M("done3"):
            sparkles(c, 640, 520, t, 10, 110)
        c.restore()
        for i, (word, _) in enumerate(parts):
            prompt(c, f"SCRUB YOUR {word.upper()}!", t, s.M(f"sc{i}"), s.M(f"kids{i}") + 3.0, y=190, size=64)
        prompt(c, "NO!", t, s.M("no_kids"), s.M("no"), y=190, size=100)
        prompt(c, "YES!", t, s.M("yes_kids"), s.M("yes_end"), y=190, size=100)
        steps_bar(c, t, s, ["_", "_", "done3", None, None])
    s.m["_"] = -1.0
    s.draw = d4
    S.append(s)

    # ---------------- 5. STEPS 4 + 5: RINSE AND DRY (the big shake)
    s = Scene("rinse", music="theme", trans="spin", music_gain=0.5)
    s.wait(0.3)
    s.say("narr", "Step four. Rinse, rinse, rinse!", key="s4", gap=0.1)
    s.mark("rinse"); s.fx("pour")
    s.wait(1.6)
    s.say("biscuit", "[laugh] Splashy!", key="splashy", gap=0.2)
    s.say("prickles", "My turn to help!", key="help", gap=0.1)
    s.mark("oops_spray"); s.fx("splash_small", s.t + 0.2)
    s.wait(0.6)
    s.say("prickles", "[laugh] Oopsie-prickle! I rinsed me!", key="rinsed", gap=0.3)
    s.mark("done4"); s.fx("ding7")
    s.say("narr", "Step five. Dry off with a towel.", key="s5", gap=0.2)
    s.mark("hop_out"); s.fx("boing")
    s.wait(0.8)
    s.mark("shake"); s.fx("shake")
    s.wait(1.2)
    s.say("mittens", "Meow! Now I'm all wet!", key="wet", gap=0.2)
    s.say("prickles", "Hee hee! Splashy shake!", key="laugh", gap=0.3)
    s.mark("towel"); s.fx("cape")
    s.wait(0.8)
    s.mark("done5"); s.fx("ding8"); s.fx("sparkle")
    s.wait(0.8)

    def d5(c, t, s=s):
        cam(c, 1.3, 620, 470)
        garden(c, t, props=("tree",))
        out = t > s.M("hop_out")
        tub_back(c, 720, 700, 1.0)
        if not out:
            draw_biscuit(c, 720, 600, 1.0, t, mouth=s.mouth("biscuit", t), face=-1, ears=0.6, wag=1.0)
        tub_front(c, 720, 700, 1.0, water=0.75, t=t, bubbles=1.0 - ease(ramp(t, s.M("rinse"), s.M("rinse") + 1.4)))
        # watering can rinse
        if s.M("rinse") < t < s.M("rinse") + 1.8:
            for k in range(10):
                ph = (t * 3 + k / 10) % 1
                circle(c, 660 + k * 12, 400 + ph * 150, 6, 0xCC7FD3FF, 0)
        sh = s.M("shake")
        wet_mittens = t > sh + 0.4
        draw_mittens(c, 330, GY, 0.9, t, mouth=s.mouth("mittens", t), face=1, look=(1, 0),
                     lid=0.0 if s.M("wet") < t < s.M("wet_end") else 0.25, tail=2.0 if wet_mittens else 1.0)
        if wet_mittens:
            for i in range(4):
                ph = (t * 1.2 + i / 4) % 1
                circle(c, 300 + i * 20, 520 + ph * 120, 5, 0xCC7FD3FF, 0)
        if out:
            bx = kf(t, [(s.M("hop_out"), 720), (s.M("hop_out") + 0.7, 520)])
            by = GY + hop(t, s.M("hop_out"), 0.7, 120)
            shaking = sh < t < sh + 1.2
            draw_biscuit(c, bx, by, 1.0, t, mouth=s.mouth("biscuit", t), face=-1, ears=0.6, wag=2.0,
                         tilt=math.sin(t * 40) * 12 if shaking else 0, blink=1.0 if shaking else None)
            if shaking:
                for i in range(14):
                    a = hsh(i, int(t * 8)) * math.tau
                    d = 60 + ((t - sh) * 400) % 220
                    circle(c, bx + math.cos(a) * d, 560 + math.sin(a) * d * 0.6, 6, 0xCC7FD3FF, 0)
            if t > s.M("towel"):
                towel(c, bx, GY + 4, 1.0)
                sparkles(c, bx, 520, t, 6, 80)
        draw_prickles(c, 1040, GY, 0.95, t, mouth=s.mouth("prickles", t), face=-1, look=(-1, 0))
        sp = s.M("oops_spray")
        if sp < t < sp + 1.6:
            for k in range(12):
                ph = (t * 2.5 + k / 12) % 1
                circle(c, 1010 + (hsh(k) - 0.5) * 90, 480 + ph * 160, 6, 0xCC7FD3FF, 0)
        c.restore()
        steps_bar(c, t, s, ["_", "_", "_", "done4", "done5"])
    s.m["_"] = -1.0
    s.draw = d5
    S.append(s)

    # ---------------- 6. THE BATH SONG: short sung sing-along, close up in the yard
    import shorts as _SH
    lyr = [(0.0, 4.6, "It's bath time, bath time!"), (4.6, 8.6, "Water, bubbles, scrub, rinse, dry!"),
           (8.6, 13.0, "Scrub your tummy, scrub, scrub, scrub!"), (13.0, 17.4, "Scrub your tummy!"),
           (17.4, 21.5, "All clean and fluffy!"), (21.5, 24.0, "Hooray!")]
    s = Scene("song", music=None, trans="hero")
    s.wait(0.3)
    s.say("narr", "Let's sing the bath song! Scrub along with Biscuit!", key="n1", gap=0.3)
    add_song(s, _SH.bath_excerpt(), "bath", gain=1.0)
    s.say("narr", "Great job, friends!", key="n3", gap=0.2)
    s.fx("sparkle"); s.fx("ding8")
    s.wait(0.6)

    def d_song(c, t, s=s, lyr=lyr):
        st0 = s.M("bath")
        tt = t - st0
        cur = ""
        for (a_, b_, line) in lyr:
            if a_ <= tt < b_:
                cur = line
        # off-screen singer: characters only open their mouths to cheer "Hooray!"
        sing = 0.8 if tt > 21.5 else 0.0
        scrub = "crub" in cur or "rinse" in cur.lower() or "rub" in cur
        beat = hop((tt % 0.536), 0, 0.536, 22) if 0 < tt < 24 else 0
        cam(c, 1.45, 640, 470)
        garden(c, t, props=("tree",))
        tub_back(c, 640, 700, 1.0)
        draw_biscuit(c, 640 + (math.sin(t * 14) * 5 if scrub else 0), 600 + beat * 0.4, 1.0, t, mouth=sing, face=1,
                     ears=0.7, wag=1.6)
        tub_front(c, 640, 700, 1.0, water=0.75, t=t, bubbles=1.0)
        draw_mittens(c, 380, GY + beat * 0.6, 0.9, t, mouth=sing, face=1, paw_up=0.5 + 0.5 * math.sin(t * 10) if scrub else 0.3)
        draw_prickles(c, 900, GY + beat * 0.6, 0.95, t, mouth=sing, face=-1, wiggle=0.4 if scrub else 0)
        for i in range(5):
            ph = (t * 0.3 + i / 5) % 1
            bubble(c, 520 + i * 60, 560 - ph * 300, 10 + 5 * hsh(i), t)
        c.restore()
        # big picture cue for the body part being scrubbed
        cue = None
        for w, col in (("tummy", 0xFFFFC21A), ("ears", 0xFFFF9BD5), ("paws", 0xFF6CCB5F), ("rinse", 0xFF3D8BFF), ("towel", 0xFF8E5CF7)):
            if w in cur.lower():
                cue = (w, col)
        for (a_, b_, line) in lyr:
            if a_ <= tt < b_:
                PE.lyric(c, line, tt, a_, b_, y=120)
        if cue:
            circle(c, 640, 330, 64, cue[1], 6)
            text(c, cue[0].upper(), 640, 330, 44 if len(cue[0]) < 6 else 36, 0xFFFFFFFF, ow=6)
        if t > s.M("n3"):
            sparkles(c, 640, 400, t, 12, 320)
    s.draw = d_song
    S.append(s)

    # ---------------- 7. CLEAN, FLUFFY, CALM
    s = Scene("fluffy", music="rainbow", trans="rainbow", music_gain=0.7)
    s.wait(0.4)
    s.fx("wag", s.t + 0.3)
    s.say("biscuit", "Bath time is fun! I'm all clean and fluffy.", key="b1", gap=0.3)
    s.say("mittens", "Purr-fect.", key="m1", gap=0.3)
    s.say("prickles", "Can I have a bubble bath too?", key="p1", gap=0.2)
    s.mark("pops")
    for i in range(3):
        s.fx("pop", s.t + 0.3 + i * 0.3)
    s.wait(1.2)
    s.say("prickles", "Hee hee! Pop!", key="p2", gap=0.5)
    s.mark("hug"); s.fx("sparkle", s.t + 0.5)
    s.wait(1.0)
    s.say("mittens", "Now it's almost bedtime.", key="b2", gap=0.4)
    s.say("narr", "Bath time is done! Bye-bye, friends!", key="bye", gap=0.2)
    s.say(["biscuit", "mittens", "prickles"], "Bye!", key="all", gap=0.4)
    s.mark("end"); add_song(s, "theme.mp3", "theme")

    def d6(c, t, s=s):
        if t < s.M("end"):
            cam(c, 1.3, 620, 470)
            garden(c, t, props=("tree",))
            hk = ease(ramp(t, s.M("hug"), s.M("hug") + 1.0))
            draw_mittens(c, lerp(330, 450, hk), GY, 0.95, t, mouth=s.mouth("mittens", t), face=1, lid=lerp(0.25, 0.5, hk),
                         paw_up=0.5 + 0.5 * math.sin(t * 6) if t > s.M("bye") else 0)
            draw_prickles(c, lerp(880, 760, hk), GY, 1.0, t, mouth=s.mouth("prickles", t), face=-1)
            draw_biscuit(c, 600, GY, 1.0, t, mouth=s.mouth("biscuit", t), face=1, ears=0.6, wag=lerp(1.4, 0.6, hk),
                         blink=1.0 if s.M("b2") < t < s.M("b2_end") else None)
            towel(c, 600, GY + 4, 1.0)
            sparkles(c, 600, 500, t, 6, 90)
            pt = s.M("pops")
            for i in range(3):
                st = pt + 0.3 * i
                if pt - 0.8 < t < st + 0.4:
                    k = ramp(t, pt - 0.8, st)
                    bubble(c, lerp(700, 860, k), lerp(480, 560, k) - i * 20, 20, t, pop=0 if t < st else (t - st) / 0.3)
            if hk > 0:
                for i in range(4):
                    ph = ((t - s.M("hug")) * 0.6 + i / 4) % 1
                    hx, hy = 540 + i * 45, 470 - ph * 120
                    hp_ = skia.Path()
                    hp_.moveTo(hx, hy + 8)
                    hp_.cubicTo(hx - 12, hy - 2, hx - 6, hy - 12, hx, hy - 5)
                    hp_.cubicTo(hx + 6, hy - 12, hx + 12, hy - 2, hx, hy + 8)
                    c.drawPath(hp_, fill(alpha(0xFFFF6B9A, (1 - ph) * hk)))
            c.restore()
        else:
            theme_card(c, t, s)
    s.draw = d6
    S.append(s)
    return finish(S)
