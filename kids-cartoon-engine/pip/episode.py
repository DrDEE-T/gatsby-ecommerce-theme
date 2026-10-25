"""Pip & the Puddle Patrol, Episode 1: The Lost Ladybug. Scene timing + drawing."""
import math
from draw import *
from audio import speak, envelope, fit_length, SR, FPS


class Scene:
    def __init__(self, name, music=None, trans="splash", rain=None, music_gain=1.0):
        self.name, self.music, self.trans, self.rain, self.music_gain = name, music, trans, rain, music_gain
        self.t = 0.0
        self.lines, self.sfx, self.m = [], [], {}
        self.duck_zero = []  # (start, end) windows where music drops out

    def say(self, who, text, key=None, gap=0.3, at=None):
        whos = who if isinstance(who, (list, tuple)) else [who]
        start = self.t if at is None else at
        dmax = 0.0
        target = None
        for w in whos:
            y = speak(w, text)
            if len(whos) > 1:
                if target is None:
                    target = len(y)
                else:
                    y = fit_length(y, target)
            d = len(y) / SR
            dmax = max(dmax, d)
            self.lines.append(dict(who=w, start=start, end=start + d, y=y, env=envelope(y),
                                   gain=1.0 if len(whos) == 1 else 0.62))
        if key:
            self.m[key] = start
            self.m[key + "_end"] = start + dmax
        self.t = max(self.t, start + dmax + gap)
        return start

    def fx(self, name, at=None, gain=1.0):
        self.sfx.append((self.t if at is None else at, name, gain))

    def wait(self, d):
        self.t += d

    def mark(self, k):
        self.m[k] = self.t
        return self.t

    def M(self, k, default=1e9):
        return self.m.get(k, default)

    def mouth(self, who, t):
        for L in self.lines:
            if L["who"] == who and L["start"] <= t < L["end"]:
                i = int((t - L["start"]) * FPS)
                return float(L["env"][min(i, len(L["env"]) - 1)])
        return 0.0

    @property
    def dur(self):
        return self.t


def cam(c, z, cx, cy):
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


def world(c, t, weather=0.0, sunv=1.0, play=True, bushx=None, rain_amt=0.0, clouds_on=True):
    sky(c, weather)
    sun(c, 1110, 110, t, sunv)
    if clouds_on:
        clouds(c, t, weather)
    hills(c, weather)
    ground(c, weather)
    if play:
        slide(c, 170)
        swings(c, 1050, t=t, swing=0.4)
    if bushx is not None:
        bush(c, bushx)


def prompt(c, s, t, t0, t1, y=110, size=74, color=0xFFFFD93B):
    """Big bouncy 'your turn' words for kids to shout."""
    if not (t0 <= t < t1):
        return
    k = (t - t0)
    sc = back_out(k / 0.3) * (1 + 0.06 * math.sin(k * 10))
    fade = 1 - ramp(t, t1 - 0.2, t1)
    c.saveLayerAlpha(None, int(255 * fade))
    text(c, s, W / 2, y, size, color, scale=sc)
    # little "your turn" ear/hand icon
    icon_bubble(c, W / 2 - text_w(s, size) / 2 - 70, y, 40, t, "point", min(1, k / 0.3))
    c.restore()


def text_w(s, size):
    return skia.Font(TITLE_TF, size).measureText(s)


def lyric(c, s, t, t0, t1, y=650):
    if not (t0 <= t < t1):
        return
    words = s.split()
    font = skia.Font(TITLE_TF, 52)
    total = font.measureText(s)
    x = W / 2 - total / 2
    frac = clamp((t - t0) / max(t1 - t0 - 0.3, 0.1))
    idx = min(int(frac * len(words)), len(words) - 1)
    pos = []
    for w in words:
        ww = font.measureText(w)
        pos.append((x, ww))
        x += ww + font.measureText(" ")
    bg = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(W / 2 - total / 2 - 30, y - 42, W / 2 + total / 2 + 30, y + 44), 40, 40)
    c.drawRRect(bg, fill(0xCC2B2340))
    for i, (wx, ww) in enumerate(pos):
        col = 0xFFFFD93B if i == idx else 0xFFFFFFFF
        text(c, words[i], wx, y, 52, col, align="left", ow=0)
    bx, bw = pos[idx]
    ph = (frac * len(words)) % 1
    by = y - 62 - abs(math.sin(ph * math.pi)) * 26
    dp = skia.Path()
    dp.moveTo(bx + bw / 2, by - 16)
    dp.cubicTo(bx + bw / 2 + 14, by, bx + bw / 2 + 12, by + 14, bx + bw / 2, by + 14)
    dp.cubicTo(bx + bw / 2 - 12, by + 14, bx + bw / 2 - 14, by, bx + bw / 2, by - 16)
    path_draw(c, dp, 0xFF5BBDFF, 3)


def hero_rays(c, t, col1=0xFF3D8BFF, col2=0xFF5FA2FF):
    c.drawPaint(fill(col1))
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(t * 10)
    for i in range(16):
        p = skia.Path()
        a0 = i * math.tau / 16
        p.moveTo(0, 0)
        p.lineTo(math.cos(a0) * 1600, math.sin(a0) * 1600)
        p.lineTo(math.cos(a0 + 0.2) * 1600, math.sin(a0 + 0.2) * 1600)
        p.close()
        if i % 2 == 0:
            c.drawPath(p, fill(col2))
    c.restore()


# ===================================================================== scenes
def build():
    S = []

    # ---------------- 1. COLD OPEN
    s = Scene("cold_open", music=None, trans=None)
    s.fx("pop", 0.15)
    s.wait(1.3); s.mark("cut")
    s.fx("whistle"); s.fx("cape", s.t + 0.6); s.fx("chirp", s.t)
    s.wait(2.1); s.mark("splash"); s.fx("splash")
    s.wait(0.8)
    s.say("pip", "Quack quack QUACK!", key="call", gap=0.1)
    s.fx("hero", s.M("call_end") - 0.15)
    s.wait(0.9)
    s.mark("bitsy"); s.fx("zoom")
    s.wait(0.4)
    s.say("bitsy", "Is it hero time? Is it hero time? Is it HERO TIME?", key="b1")
    s.mark("gus"); s.wait(0.6)
    s.say("gus", "It's... hero... time.", key="g1", gap=0.5)

    def d1(c, t, s=s):
        if t < s.M("cut"):
            c.drawPaint(fill(0xFF101830))
            y = kf(t, [(0.0, -40), (1.1, 360)], ease_out)
            dp = skia.Path()
            dp.moveTo(640, y - 34); dp.cubicTo(668, y, 664, y + 30, 640, y + 30); dp.cubicTo(616, y + 30, 612, y, 640, y - 34)
            path_draw(c, dp, 0xFF5BBDFF, 4, 0xFFFFFFFF)
            return
        z = 1.0
        cx, cy = W / 2, H / 2
        if t > s.M("gus"):
            k = ease(ramp(t, s.M("gus"), s.M("gus") + 0.6))
            z = lerp(1, 2.3, k)
            cx, cy = lerp(W / 2, 1160, k), lerp(H / 2, 520, k)
        cam(c, z, cx, cy)
        world(c, t)
        puddle(c, 640, 640, 230, 52)
        # gus far back right
        draw_gus(c, 1080, 600, 0.62, t, mouth=s.mouth("gus", t), face=1,
                 blink=1.0 if s.M("gus") + 0.7 < t < s.M("gus") + 1.2 else None, head_turn=0.6)
        # bitsy zoom in
        bt = s.M("bitsy")
        if t > bt:
            bx = kf(t, [(bt, -150), (bt + 0.4, 860)], ease_out)
            if t < bt + 0.5:
                speed_lines(c, bx - 60, 590, -1, 6, 200)
            draw_bitsy(c, bx, 650 + hop(t, bt + 0.4, 0.4, 40) + hop(t, bt + 1.2, 0.35, 30), 0.95, t,
                       mouth=s.mouth("bitsy", t), face=-1, goggles_on=0.0)
        # pip
        sp = s.M("splash")
        if t < sp:
            k = ramp(t, s.M("cut"), sp)
            px = lerp(-120, 640, k)
            py = 640 - math.sin(k * math.pi) * 330 - (1 - k) * 60
            draw_pip(c, px, py, 1.15, t * 0.5, wing=1.0, cape_wind=1.0, tilt=lerp(-20, 15, k))
        else:
            rise = ease_out(ramp(t, sp + 0.15, sp + 0.6))
            py = lerp(760, 650, rise)
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 0, W, 650))
            pose = 1.0 if t > s.M("call") else 0.3
            draw_pip(c, 600, py, 1.15, t, mouth=s.mouth("pip", t), wing=pose, squash=0.3 * math.sin(clamp(t - sp - 0.6) * 12) * (1 - clamp(t - sp - 0.6)))
            c.restore()
            splash_fx(c, 640, 640, sp, t, 1.4)
            if s.M("call") < t < s.M("call_end") + 0.8:
                sparkles(c, 600, 480, t, 10, 140)
        c.restore()
    s.draw = d1
    # cold open cut: the episode now opens on the title card

    # ---------------- 2. THEME SONG
    s = Scene("theme", music="theme", trans="hero", music_gain=1.4)
    s.t = 0.0
    s.mark("title"); s.fx("whoomp")
    for i in range(5):
        s.fx("pop", s.t + 1.0 + i * 0.3)
    s.wait(4.2)

    def d2(c, t, s=s):
        if t < s.M("title"):
            world(c, t)
            for i, px in enumerate((300, 640, 980)):
                puddle(c, px, 650, 120, 30)
            # pip puddle-hop on every beat
            beat = t - 0.5
            i = int(max(beat, 0)) % 3
            pos = [300, 640, 980]
            if t < 8.5:
                k = (max(beat, 0)) % 1
                x0, x1 = pos[i], pos[(i + 1) % 3]
                if (i + 1) % 3 == 0:
                    x0, x1 = pos[i], pos[i]
                px = lerp(x0, x1, k)
                draw_pip(c, px, 650 + hop(k, 0, 1, 120), 0.9, t, mouth=s.mouth("pip", t), wing=0.8, cape_wind=0.8)
                splash_fx(c, pos[i], 650, int(max(beat, 0)) + 0.5, t, 0.7)
            else:
                pose = 1.0 if 8.2 < t < 11 else 0.4
                draw_pip(c, 520, 650 + hop(t % 1, 0, 1, 30), 1.0, t, mouth=s.mouth("pip", t), wing=pose)
            # bitsy in circles
            a = t * 2.2
            bx = 900 + math.cos(a) * 140 if t < 8.5 else 760
            draw_bitsy(c, bx, 640 + hop(t % 0.5, 0, 0.5, 50), 0.8, t, mouth=s.mouth("bitsy", t),
                       face=-1 if math.sin(a) > 0 else 1, goggles_on=0.0)
            if t < 8.5:
                speed_lines(c, bx + (60 if math.sin(a) > 0 else -60), 600, 1 if math.sin(a) > 0 else -1, 4, 80, 0.6)
            # gus walks one step the whole song
            gx = kf(t, [(0, -120), (15.0, 330)], lambda x: x)
            draw_gus(c, gx, 650, 0.75, t, mouth=s.mouth("gus", t), swim=False, head_turn=0.4 if 6.5 < t < 8 else 0)
            if 14.0 < t:
                burst(c, 640, 150, 120 * back_out((t - 14) / 0.4), t, 0xFFFFD93B)
                text(c, "QUACK!", 640, 150, 70, 0xFFE8343B, scale=back_out((t - 14) / 0.4))
            for k in ("l1", "l2", "l3", "l4", "l5", "l6"):
                L = [x for x in s.lines if x["start"] == s.M(k)][0]
                txt = {"l1": "Splish! Splash! Who's that coming?", "l2": "Pip and Gus and Bitsy running!",
                       "l3": "Wait for me!", "l4": "Brave and strong and fast, hooray!",
                       "l5": "Puddle Patrol will save the day!", "l6": "Quack-quack-QUACK!"}[k]
                nxt = {"l1": "l2", "l2": "l3", "l3": "l4", "l4": "l5", "l5": "l6", "l6": None}[k]
                end = s.M(nxt) if nxt else s.M("title")
                if k != "l6":
                    lyric(c, txt, t, s.M(k), end)
        else:
            tt = t - s.M("title")
            hero_rays(c, t, 0xFF6CC8FF, 0xFF8ED8FF)
            sc = back_out(tt / 0.5)
            c.save(); c.translate(640, 330); c.scale(sc, sc)
            draw_bug(c, 0, 0, 7.5, t, blink=0.0, look=(0, 0))
            c.restore()
            text(c, "EPISODE 1", 640, 560, 48, 0xFFFFFFFF, scale=back_out((tt - 0.3) / 0.4))
            text(c, "THE LOST LADYBUG", 640, 630, 76, 0xFFFFD93B, scale=back_out((tt - 0.5) / 0.4))
            text(c, "PIP & THE PUDDLE PATROL", 640, 75, 66, 0xFFFFFFFF, scale=back_out(tt / 0.4))
    s.draw = d2
    S.append(s)

    # ---------------- 3. HERO IN TRAINING
    s = Scene("training", music="theme", trans="hero", music_gain=0.5)
    s.fx("chirp", 0.2)
    for i in range(4):
        s.fx("squelch", 0.3 + i * 0.42)
    s.wait(2.0)
    s.say("pip", "Hi friends! I'm Pip, and I'm a hero in training!", key="hi")
    s.mark("badge"); s.fx("wahwah", s.t + 0.2, 0.7)
    s.wait(0.6)
    s.say("pip", "But I don't have a hero badge yet. Real heroes get badges when they help someone.", key="nob")
    s.fx("cape")
    s.say("pip", "Someday, I'll be a real hero!", key="someday", gap=0.5)
    s.mark("cloud"); s.fx("whoomp")
    s.wait(1.4); s.mark("drop"); s.fx("ding7")
    s.wait(1.0); s.fx("gasp"); s.wait(0.4)
    s.say("pip", "Rain! Let's count the raindrops!", key="count", gap=0.4)
    s.mark("c0")
    for i, w in enumerate(["One!", "Two!", "Three!", "Four!", "Five!"]):
        s.mark(f"n{i}")
        s.fx(f"ding{i + 1}")
        s.say("narr", w, gap=0.55)
    s.mark("many")
    s.wait(0.6)
    s.say("pip", "Too many to count!", key="toomany", gap=0.8)

    def d3(c, t, s=s):
        wthr = 0.55 * ease(ramp(t, s.M("cloud"), s.M("cloud") + 1.2)) + 0.45 * ease(ramp(t, s.M("many"), s.M("many") + 1.5))
        sunv = 1 - ease(ramp(t, s.M("cloud"), s.M("cloud") + 1.2))
        z, cx, cy = 1.0, W / 2, H / 2
        if s.M("badge") < t < s.M("nob_end"):
            k = ease(ramp(t, s.M("badge"), s.M("badge") + 0.5)) * (1 - ease(ramp(t, s.M("nob_end") - 0.4, s.M("nob_end"))))
            z, cx, cy = lerp(1, 2.2, k), lerp(W / 2, 640, k), lerp(H / 2, 520, k)
        if s.M("drop") - 0.3 < t < s.M("count_end"):
            k = ease(ramp(t, s.M("drop") - 0.3, s.M("drop"))) * (1 - ease(ramp(t, s.M("count_end") - 0.3, s.M("count_end"))))
            z, cx, cy = lerp(1, 2.4, k), lerp(W / 2, 650, k), lerp(H / 2, 470, k)
        cam(c, z, cx, cy)
        world(c, t, wthr, sunv)
        sandbox(c, 900)
        # pip walks in
        px = kf(t, [(0, -100), (1.9, 640)], lambda x: x)
        walking = t < 1.9
        bob = -abs(math.sin(t * 7.5)) * 10 if walking else 0
        wing = 0.0
        if s.M("hi") < t < s.M("hi_end"):
            wing = 0.6 + 0.3 * math.sin(t * 8)
        if s.M("someday") < t < s.M("someday_end") + 0.5:
            wing = 1.0
        look = (0, 0)
        if s.M("drop") < t < s.M("count"):
            look = (-0.2, -1.0)
        if t > s.M("c0"):
            look = (0.3, -1.0)
        worried = 1.0 if s.M("nob") < t < s.M("nob_end") else 0.0
        draw_pip(c, px, 650 + bob, 1.0, t, mouth=s.mouth("pip", t), wing=wing, look=look, worried=worried,
                 cape_wind=0.3 + (0.6 if s.M("someday") < t < s.M("someday_end") else 0))
        if s.M("badge") < t < s.M("nob_end"):
            pulse = 0.5 + 0.5 * math.sin(t * 6)
            c.drawCircle(640, 546, 22 + 4 * pulse, stroke(0xFFFFE15A, 4))
        # the first drop on his beak
        dt = s.M("drop")
        if dt - 1.0 < t < dt + 0.4:
            yy = kf(t, [(dt - 1.0, 200), (dt, 505)], lambda x: x * x)
            dp = skia.Path()
            dp.moveTo(690, yy - 18); dp.cubicTo(704, yy, 702, yy + 14, 690, yy + 14); dp.cubicTo(678, yy + 14, 676, yy, 690, yy - 18)
            path_draw(c, dp, 0xFF5BBDFF, 3)
        c.restore()
        # counting drops + numbers
        cols = [0xFF3D8BFF, 0xFFE8343B, 0xFFFFC21A, 0xFF6CCB5F, 0xFF8E5CF7]
        for i in range(5):
            nt = s.M(f"n{i}")
            if nt - 0.6 < t < s.M("many") + 0.3:
                x = 260 + i * 190
                yy = kf(t, [(nt - 0.6, -40), (nt, 330)], lambda x: x * x)
                if t < nt:
                    dp = skia.Path()
                    dp.moveTo(x, yy - 40); dp.cubicTo(x + 32, yy, x + 28, yy + 34, x, yy + 34); dp.cubicTo(x - 28, yy + 34, x - 32, yy, x, yy - 40)
                    path_draw(c, dp, 0xFF5BBDFF, 5)
                else:
                    sc = back_out((t - nt) / 0.3)
                    circle(c, x, 330, 70 * sc, 0xFFFFFFFF, 6)
                    text(c, str(i + 1), x, 330, 100, cols[i], scale=sc, ow=10)
        if t > s.M("many"):
            k = ramp(t, s.M("many"), s.M("many") + 1.0)
            c.save(); c.translate(0, 0)
            for i in range(5):
                x = 260 + i * 190
                c.save(); c.translate(x, 330); c.rotate(k * 720 * (1 if i % 2 else -1)); c.scale(1 - k, 1 - k)
                text(c, str(i + 1), 0, 0, 100, cols[i], ow=10)
                c.restore()
            c.restore()
        rain(c, t, 0.3 * ramp(t, s.M("cloud") + 1.0, s.M("cloud") + 2) + 0.7 * ramp(t, s.M("many"), s.M("many") + 1))
    s.draw = d3
    S.append(s)

    # ---------------- 4. FLOOD + CALL FOR HELP
    s = Scene("flood", music="search", trans="drop", rain="heavy", music_gain=0.6)
    s.fx("whoomp", 0.1)
    s.wait(3.0)
    s.mark("bitsy"); s.fx("zoom")
    s.wait(0.5)
    s.say("bitsy", "Whoa! The whole playground is a puddle!", key="b1", gap=0.2)
    s.mark("gus"); s.fx("creak")
    s.wait(0.8)
    s.say("gus", "Lovely... weather.", key="g1", gap=0.6)
    s.mark("freeze")
    s.say("dot", "Help! Help, please!", key="help", gap=0.5)
    s.fx("gasp")
    s.wait(0.3)
    s.say("pip", "Someone needs help! This is a job for...", key="job", gap=0.2)
    s.mark("kids"); s.wait(2.3)
    s.say(["pip", "bitsy", "gus"], "Quack quack QUACK! Puddle Patrol to the rescue!", key="call", gap=0.3)
    s.fx("hero", s.M("call_end") - 0.4)
    s.wait(0.6)
    s.duck_zero.append((s.M("freeze"), s.M("call")))

    def d4(c, t, s=s):
        lvl = kf(t, [(0, 760), (3.0, 590)])
        cam(c, 1.2, 640, 450)
        world(c, t, 1.0, 0.0)
        # gus floating
        gt = s.M("gus")
        gx = kf(t, [(gt, 1450), (gt + 1.5, 930)])
        frozen = s.M("freeze") < t < s.M("job")
        draw_gus(c, gx, lvl + 40 + math.sin(t * 2) * 4, 0.7, t, mouth=s.mouth("gus", t), face=-1, swim=True,
                 swim_phase=t * 0.4, look=(0.6, -0.4) if frozen else (0, 0))
        water(c, lvl, t)
        # sandbox boat with pip
        bob = math.sin(t * 2.2) * 5
        sandbox(c, 560, lvl + 12, 1.0, bob)
        look = (0, 0)
        if frozen:
            look = (0.8, -0.3)
        if s.M("kids") < t < s.M("call"):
            look = (0, 0.3)
        wing = 1.0 if t > s.M("call") else (0.5 if s.M("job") < t else 0)
        draw_pip(c, 560, lvl - 28 + bob, 0.95, t, mouth=s.mouth("pip", t), look=look, wing=wing, cape_wind=0.7)
        # bitsy surfing in
        bt = s.M("bitsy")
        bx = kf(t, [(bt, -200), (bt + 0.6, 300)], ease_out)
        lilypad(c, bx, lvl + 4, 0.9)
        draw_bitsy(c, bx, lvl + 2 + math.sin(t * 3) * 3, 0.8, t, mouth=s.mouth("bitsy", t), face=1, goggles_on=0.0,
                   look=(0.8, -0.3) if frozen else (0, 0))
        if bt < t < bt + 0.7:
            speed_lines(c, bx - 80, lvl - 40, -1, 4, 160)
        c.restore()
        if s.M("freeze") < t < s.M("job"):
            for (x, y) in ((560, 280), (300, 420), (gx + 60, 400)):
                text(c, "!", x, y, 60, 0xFFFFD93B, scale=back_out((t - s.M("freeze")) / 0.3))
            # tiny voice from off screen right
            sparkles(c, 1240, 470, t, 5, 40, 0xFFFF6B6B, 3)
        prompt(c, "QUACK-QUACK-QUACK!", t, s.M("kids"), s.M("call") + 0.2)
        if t > s.M("call"):
            burst(c, 640, 120, 110 * back_out((t - s.M("call")) / 0.4), t)
            text(c, "TO THE RESCUE!", 640, 120, 60, 0xFFE8343B, scale=back_out((t - s.M("call")) / 0.4))
        rain(c, t, 1.0)
    s.draw = d4
    S.append(s)

    # ---------------- 5. SUIT UP + HERO PROMISE
    s = Scene("suitup", music="hero", trans="hero", music_gain=0.8)
    shots = []
    s.mark("boots"); s.fx("squelch", s.t + 0.5); s.fx("squelch", s.t + 0.9); s.fx("sparkle", s.t + 1.0)
    s.wait(1.6); s.mark("cape"); s.fx("cape", s.t + 0.2); s.fx("cape", s.t + 0.8)
    s.wait(1.6); s.mark("gog"); s.fx("pop", s.t + 0.5); s.fx("sparkle", s.t + 0.55)
    s.wait(0.6)
    s.say("bitsy", "Goggles, go!", key="gg", gap=0.2)
    s.mark("stretch")
    for i in range(3):
        s.fx("boing", s.t + i * 0.35)
    s.wait(1.3); s.mark("helm"); s.fx("creak", s.t + 0.2)
    s.wait(2.0); s.mark("pose"); s.fx("tada")
    s.wait(1.8)
    s.say("pip", "Every hero says the Hero Promise! Say it with us!", key="promise", gap=0.5)
    for k, line in (("look", "We look!"), ("brave", "We're brave!"), ("help", "We help!")):
        s.mark(k + "_show"); s.wait(0.5)
        s.say(["pip", "bitsy", "gus"], line, key=k, gap=0.15)
        s.fx("ding5")
        s.wait(1.2)

    def d5(c, t, s=s):
        if t < s.M("pose"):
            hero_rays(c, t)
            if t < s.M("cape"):
                k = t - s.M("boots")
                cam(c, 2.6, 640, 610)
                yb = kf(k, [(0, -260), (0.5, 0)], lambda x: x * x)
                draw_pip(c, 640, 680, 1.0, t, cape=False, boots=False)
                c.save(); c.translate(0, yb)
                for bx in (-22, 22):
                    r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(640 + bx - 17, 646, 640 + bx + 19, 680), 9, 9)
                    c.drawRRect(r, fill(0xFFE8343B)); c.drawRRect(r, stroke())
                c.restore()
                if k > 0.5:
                    splash_fx(c, 640, 680, s.M("boots") + 0.5, t, 0.4)
                c.restore()
            elif t < s.M("gog"):
                k = t - s.M("cape")
                cam(c, 1.8, 640, 520)
                draw_pip(c, 640, 680, 1.0, t, cape_wind=lerp(0, 1.3, ease(k / 0.6)), wing=0.8)
                c.restore()
                speed_lines(c, 300, 360, -1, 8, 260, 0.6)
            elif t < s.M("stretch"):
                k = t - s.M("gog")
                cam(c, 2.3, 640, 500)
                draw_bitsy(c, 640, 640, 1.2, t, mouth=s.mouth("bitsy", t), goggles_on=ease(ramp(k, 0.35, 0.5)))
                c.restore()
                if k > 0.5:
                    sparkles(c, 640, 250, t, 8, 200)
            elif t < s.M("helm"):
                k = t - s.M("stretch")
                cam(c, 1.6, 640, 520)
                sq = math.sin(k * 18) * (1 - k / 1.3)
                draw_bitsy(c, 640, 660 + hop(k % 0.35, 0, 0.35, 60), 1.1, t, squash=sq, stretch=max(0, -sq))
                c.restore()
            else:
                k = t - s.M("helm")
                cam(c, 1.7, 700, 500)
                draw_gus(c, 600, 660, 1.0, t, helmet=lerp(0.0, 0.25, k / 2.0), head_turn=0.7)
                c.restore()
        else:
            hero_rays(c, t, 0xFF3D8BFF, 0xFF64A8FF)
            tp = s.M("pose")
            together = 1.0 if t > s.M("help_show") else 0.0
            jn = ease(ramp(t, s.M("help_show"), s.M("help_show") + 0.4))
            look_pose = s.M("look_show") < t < s.M("brave_show")
            brave_pose = s.M("brave_show") < t < s.M("help_show")
            draw_gus(c, lerp(360, 440, jn), 640, 0.95, t, mouth=s.mouth("gus", t), helmet=0.25, head_turn=0.7)
            draw_pip(c, 640, 650, 1.1, t, mouth=s.mouth("pip", t),
                     wing=1.0 if look_pose or brave_pose else (0.7 if jn else 0.5), cape_wind=0.9,
                     look=(0, -0.2) if look_pose else (0, 0))
            draw_bitsy(c, lerp(920, 840, jn), 650, 1.0, t, mouth=s.mouth("bitsy", t), goggles_on=1.0,
                       squash=0.3 * math.sin(t * 10) if brave_pose else 0)
            if t < s.M("promise"):
                sc = back_out((t - tp) / 0.4)
                burst(c, 640, 150, 260 * sc, t * 0.3)
                text(c, "PUDDLE PATROL!", 640, 150, 92, 0xFFE8343B, scale=sc, rot=-4, ow=14)
            for i, k in enumerate(("look", "brave", "help")):
                st = s.M(k + "_show")
                if t > st:
                    icon_bubble(c, 360 + i * 280, 150, 70, t, k, ramp(t, st, st + 0.3))
                    lbl = {"look": "WE LOOK!", "brave": "WE'RE BRAVE!", "help": "WE HELP!"}[k]
                    text(c, lbl, 360 + i * 280, 260, 40, 0xFFFFD93B, scale=back_out((t - st) / 0.3))
    s.draw = d5
    S.append(s)

    # ---------------- 6. SEARCH
    s = Scene("search", music="search", trans="boots", rain="light", music_gain=0.8)
    s.wait(0.5)
    s.say("pip", "We look! Is she on the slide?", key="q", gap=0.2)
    s.mark("zoom")
    for i in range(5):
        s.fx("zoom", s.t + i * 0.42, 0.7)
    s.say("bitsy", "Not here, not here, not here, NOT HERE!", key="b1", gap=0.3)
    s.mark("turn"); s.fx("creak")
    s.say("gus", "Let... me... look...", key="g1", gap=0.6)
    s.say("gus", "...nope.", key="g2", gap=0.4)
    s.mark("pan"); s.fx("buzz", s.t + 0.8)
    s.wait(1.5)
    s.say("narr", "Do YOU see something red? Point to it!", key="ask", gap=0.1)
    s.mark("kids"); s.wait(2.4)
    s.fx("gasp")
    s.wait(0.3)
    s.say("pip", "You found her! Thank you, friend!", key="found", gap=0.6)

    def d6(c, t, s=s):
        lvl = 590
        k = ease(ramp(t, s.M("pan"), s.M("pan") + 1.4))
        cx = lerp(560, 860, k)
        z = lerp(1.2, 1.35, k)
        cam(c, z, cx, 450 + 30 * k)
        world(c, t, 0.85, 0.0, play=False)
        slide(c, 170)
        swings(c, 1050, t=t, swing=0.4)
        # bitsy zooming up and down the slide
        zt = s.M("zoom")
        gx = 520
        draw_gus(c, gx, lvl + 40 + math.sin(t * 2) * 4, 0.7, t, mouth=s.mouth("gus", t), face=1, swim=True,
                 swim_phase=t * 0.3, head_turn=ease(ramp(t, s.M("turn"), s.M("g1_end"))))
        water(c, lvl, t)
        # dot far away on a leaf
        leaf(c, 1180, lvl + 6, 0.35, math.sin(t * 2) * 5)
        draw_bug(c, 1180, lvl - 8, 0.35, t, flying=0)
        bob = math.sin(t * 2.2) * 5
        sandbox(c, 330, lvl + 12, 0.9, bob)
        draw_pip(c, 330, lvl - 26 + bob, 0.85, t, mouth=s.mouth("pip", t), wing=0.9 if s.M("q") < t < s.M("q_end") else 0.2,
                 look=(1, 0) if t > s.M("found") else (0, 0))
        if zt < t < zt + 2.1:
            ph = ((t - zt) / 0.42) % 1
            tri = 1 - abs(ph * 2 - 1)
            bx = lerp(150, 340, tri)
            by = lerp(300, 560, tri)
            draw_bitsy(c, bx, by, 0.55, t, face=1 if ph > 0.5 else -1, goggles_on=1.0, tilt=30 if ph > 0.5 else -30)
            speed_lines(c, bx, by - 30, 1 if ph < 0.5 else -1, 4, 70)
        else:
            lilypad(c, 160, lvl + 4, 0.8)
            draw_bitsy(c, 160, lvl + 2, 0.7, t, mouth=s.mouth("bitsy", t), goggles_on=1.0)
        if s.M("kids") + 1.0 < t < s.M("found_end"):
            c.drawCircle(1180, lvl - 8, 34 + 6 * math.sin(t * 8), stroke(0xFFFFD93B, 5))
        c.restore()
        if s.M("ask") < t < s.M("found"):
            icon_bubble(c, 1150, 140, 60, t, "point", ramp(t, s.M("ask"), s.M("ask") + 0.3))
        prompt(c, "POINT TO IT!", t, s.M("kids"), s.M("found"), y=100)
        rain(c, t, 0.4)
    s.draw = d6
    S.append(s)

    # ---------------- 7. THE PROBLEM
    s = Scene("problem", music="tension", trans="spin", rain="light", music_gain=0.7)
    s.wait(0.4)
    s.say("dot", "Help! My wings are too wet to fly!", key="d1", gap=0.3)
    s.mark("wide"); s.fx("swirl", s.t, 0.8)
    s.wait(1.0)
    s.say("bitsy", "Uh oh! The leaf is going to the swirly puddle!", key="b1")
    s.say("dot", "Whoa! It's getting spinny!", key="d2", gap=0.3)
    s.fx("cape")
    s.say("pip", "Don't worry, Dot! The Puddle Patrol is coming!", key="p1")
    s.say("pip", "Every hero has a super power. Let's use ours! Bitsy, you're fast!", key="p2", gap=0.2)
    s.fx("zoom", s.M("p2_end") - 0.6)
    s.say("pip", "Gus, you're strong!", key="p3", gap=0.5)
    s.fx("creak", s.M("p3_end") - 0.4)
    s.mark("little")
    s.say("pip", "And I'm... little.", key="p4", gap=0.6)
    s.mark("pat"); s.fx("creak")
    s.wait(0.6)
    s.say("gus", "Little... can... be... brave.", key="g1", gap=0.7)
    s.fx("sparkle", s.M("g1_end") - 0.3)
    s.duck_zero.append((s.M("little"), s.M("g1_end")))

    def d7(c, t, s=s):
        lvl = 600
        leafx = kf(t, [(0, 760), (s.dur, 900)], lambda x: x)
        z, cx, cy = 1.0, W / 2, H / 2
        if t < s.M("wide"):
            z, cx, cy = 3.0, leafx, 575
        elif t < s.M("wide") + 0.8:
            k = ease(ramp(t, s.M("wide"), s.M("wide") + 0.8))
            z, cx, cy = lerp(3.0, 1.15, k), lerp(leafx, 660, k), lerp(575, 470, k)
        else:
            z, cx, cy = 1.15, 660, 470
        if s.M("little") < t < s.M("g1_end"):
            k = ease(ramp(t, s.M("little"), s.M("little") + 0.5))
            z, cx, cy = lerp(1.15, 1.9, k), lerp(660, 330, k), lerp(470, 470, k)
        cam(c, z, cx, cy)
        world(c, t, 0.85, 0.0, play=False)
        swings(c, 1120, t=t, swing=0.3)
        gx = 470 if t < s.M("pat") else kf(t, [(s.M("pat"), 470), (s.M("pat") + 0.6, 420)])
        draw_gus(c, gx, lvl + 40 + math.sin(t * 2) * 4, 0.7, t, mouth=s.mouth("gus", t), face=-1 if t > s.M("pat") else 1,
                 swim=True, swim_phase=t * 0.3,
                 badge=0)
        water(c, lvl, t)
        swirl(c, 1060, lvl + 30, t, 1.1)
        rot = math.sin(t * 2) * 6 + (t - s.M("d2")) * 8 * (t > s.M("d2"))
        leaf(c, leafx, lvl + 4, 0.75, rot)
        draw_bug(c, leafx, lvl - 22, 0.9, t, mouth=s.mouth("dot", t), look=(-0.5, 0))
        if t < s.M("wide") + 2:
            for i in range(3):
                ph = (t * 1.5 + i / 3) % 1
                circle(c, leafx - 14 + i * 14, lvl - 4 + ph * 30, 3, 0xFF8ED8FF, 1.5)
        bob = math.sin(t * 2.2) * 5
        sandbox(c, 290, lvl + 12, 0.9, bob)
        little = s.M("p4") < t < s.M("g1")
        draw_pip(c, 290, lvl - 26 + bob, 0.85 * (0.9 if little else 1), t, mouth=s.mouth("pip", t),
                 wing=0.9 if s.M("p1") < t < s.M("p3_end") else 0.1, worried=1.0 if little else 0,
                 look=(0, 0.6) if little else (0.6, 0), cape_wind=0.8 if s.M("p1") < t < s.M("p1_end") else 0.3)
        lilypad(c, 120, lvl + 4, 0.8)
        draw_bitsy(c, 120, lvl + 2, 0.7, t, mouth=s.mouth("bitsy", t), goggles_on=1.0, look=(1, 0))
        # power icons
        if s.M("p2_end") - 0.8 < t < s.M("little"):
            sc = back_out((t - (s.M("p2_end") - 0.8)) / 0.3)
            circle(c, 120, 420, 40 * sc, 0xFFFFC21A, 5)
            text(c, "FAST!", 120, 360, 36, 0xFFFFD93B, scale=sc)
        if s.M("p3_end") - 0.6 < t < s.M("little"):
            sc = back_out((t - (s.M("p3_end") - 0.6)) / 0.3)
            text(c, "STRONG!", 470, 400, 36, 0xFF6CCB5F, scale=sc)
        if t > s.M("g1_end") - 0.6:
            sparkles(c, 290, 440, t, 8, 70)
        c.restore()
        rain(c, t, 0.4)
    s.draw = d7
    S.append(s)

    # ---------------- 8. BITSY'S SPEED  9. GUS'S STRENGTH  (one continuous rescue scene)
    s = Scene("rescue1", music="rescue", trans="hero", rain="light", music_gain=0.7)
    s.wait(0.3)
    s.fx("pop"); s.fx("sparkle")
    s.say("bitsy", "Speed power, activate!", key="act", gap=0.2)
    s.mark("hops")
    for i in range(6):
        s.fx("boing", s.t + i * 0.32, 0.8)
        s.fx("splash_small", s.t + i * 0.32 + 0.25, 0.4)
    s.wait(0.6)
    s.say("narr", "Cheer for Bitsy! Go, Bitsy, go!", key="cheer", gap=0.1)
    s.mark("kids1"); s.fx("cheer", s.t + 0.4, 0.5); s.wait(1.8)
    s.fx("ding6")
    s.say("bitsy", "I'm here! I'm here! You're not alone, Dot!", key="here", gap=0.3)
    s.mark("pull")
    s.wait(1.2)
    s.say("bitsy", "I'm fast, but I'm too small to pull it! Gus! GUS!", key="gus", gap=0.4)
    s.mark("helm"); s.fx("creak"); s.fx("pop", s.t + 0.9); s.fx("sparkle", s.t + 0.95)
    s.wait(1.3)
    s.say("gus", "Strength... power... on.", key="on", gap=0.4)
    s.say("pip", "Help Gus swim! Say it with us!", key="swim", gap=0.4)
    s.mark("chant")
    for rep in range(2):
        for w in ("Slow!", "and", "STEADY!"):
            s.fx("creak", s.t, 0.8)
            st = s.say(["pip", "bitsy"], w, gap=0.0)
            s.t = st + 1.0
    s.mark("block"); s.fx("bonk"); s.fx("ding8", s.t + 0.1)
    s.wait(0.5)
    s.say("gus", "Got... you.", key="got", gap=0.3)
    s.mark("tip")
    s.say("dot", "Eep! It's wobbly! I'm slipping!", key="slip", gap=0.2)
    s.say("gus", "Can't... let go... Pip!", key="pip", gap=0.5)

    def d8(c, t, s=s):
        lvl = 600
        # leaf drifts toward swirl until gus blocks it
        blocked = t > s.M("block")
        leafx = kf(t, [(0, 900), (s.M("block"), 960)], lambda x: x)
        rot = math.sin(t * 2) * 6
        if t > s.M("tip"):
            rot = 14 + math.sin(t * 6) * 5
        cam(c, 1.22, 680, 470)
        world(c, t, 0.85, 0.0, play=False)
        swings(c, 1120, t=t, swing=0.3)
        # gus swims from left to block position (right of leaf)
        gx = kf(t, [(s.M("chant"), 470), (s.M("block"), 1080)])
        draw_gus(c, gx, lvl + 40 + math.sin(t * 2) * 4, 0.7, t, mouth=s.mouth("gus", t), face=-1 if blocked else 1, swim=True,
                 swim_phase=(t - s.M("chant")) * (1.0 if s.M("chant") < t < s.M("block") else 0.2),
                 helmet=lerp(0.25, 1.0, ease(ramp(t, s.M("helm"), s.M("helm") + 0.9))))
        water(c, lvl, t)
        swirl(c, 1180, lvl + 30, t, 1.0)
        leaf(c, leafx, lvl + 4, 0.75, rot)
        dx = 0
        if t > s.M("tip"):
            dx = 30 * ease(ramp(t, s.M("tip"), s.M("tip") + 1.0))
        draw_bug(c, leafx + dx, lvl - 22 + dx * 0.3, 0.9, t, mouth=s.mouth("dot", t), look=(-1, 0))
        # pads + bitsy hopping
        pads = [120 + i * 125 for i in range(6)] + [leafx - 120]
        for i, px in enumerate(pads[1:]):
            lilypad(c, px, lvl + 4, 0.55)
        lilypad(c, 120, lvl + 4, 0.8)
        ht = s.M("hops")
        if t < ht:
            bx, by = 120, lvl + 2
        else:
            k = (t - ht) / 0.32
            i = min(int(k), len(pads) - 2)
            f = clamp(k - i)
            if k >= len(pads) - 1:
                i, f = len(pads) - 2, 1.0
            bx = lerp(pads[i], pads[i + 1], f)
            by = lvl + 2 + hop(f, 0, 1, 90) * (1 if k < len(pads) - 1 else 0)
            if k < len(pads) - 1:
                speed_lines(c, bx - 50, by - 40, -1, 4, 80)
        pulling = s.M("pull") < t < s.M("helm")
        draw_bitsy(c, bx + (math.sin(t * 40) * 3 if pulling else 0), by, 0.65, t, mouth=s.mouth("bitsy", t), goggles_on=1.0,
                   squash=0.2 if pulling else 0, face=1)
        if t < s.M("act_end"):
            sparkles(c, 120, lvl - 80, t, 6, 60)
        bob = math.sin(t * 2.2) * 5
        sandbox(c, 290 if t < s.M("hops") else 230, lvl + 12, 0.9, bob)
        draw_pip(c, 290 if t < s.M("hops") else 230, lvl - 26 + bob, 0.85, t, mouth=s.mouth("pip", t), wing=0.6 if t > s.M("swim") else 0.2,
                 look=(1, 0))
        if blocked and t < s.M("block") + 0.6:
            text(c, "BONK!", gx - 40, lvl - 140, 44, 0xFFFFD93B, scale=back_out((t - s.M("block")) / 0.3))
        c.restore()
        prompt(c, "GO BITSY GO!", t, s.M("cheer"), s.M("here"), y=100)
        if s.M("chant") < t < s.M("block"):
            k = int((t - s.M("chant")) / 1.0) % 3
            word = ["SLOW...", "AND...", "STEADY!"][k]
            text(c, word, W / 2, 110, 80, [0xFF6CCB5F, 0xFFFFD93B, 0xFF3D8BFF][k], scale=back_out(((t - s.M("chant")) % 1.0) / 0.3))
        rain(c, t, 0.35)
    s.draw = d8
    S.append(s)

    # ---------------- 10. PIP'S BRAVERY
    s = Scene("brave", music="brave", trans="hero", rain="light", music_gain=1.0)
    s.fx("heartbeat", 0.2); s.fx("heartbeat", 1.2); s.fx("heartbeat", 2.2)
    s.wait(0.8)
    s.say("pip", "It's so far. And I'm so little.", key="far", gap=0.6)
    s.say("pip", "Friends... will you help me be brave?", key="ask", gap=0.3)
    s.say("narr", "Let's cheer for Pip! Say: you can do it, Pip!", key="cheer", gap=0.1)
    s.mark("kids1"); s.fx("cheer", s.t + 0.5, 0.45); s.wait(2.4)
    s.mark("breath"); s.fx("sparkle"); s.fx("whoomp", s.t, 0.4)
    s.wait(1.4)
    s.say("pip", "Heroes are brave!", key="brave", gap=0.3)
    s.mark("kids2"); s.wait(1.9)
    s.say("pip", "Quack quack QUACK!", key="call", gap=0.0)
    s.fx("hero", s.M("call_end") - 0.2)
    s.mark("jump"); s.fx("cape", s.t + 0.1); s.fx("whistle", s.t + 0.1); s.fx("choir", s.t + 0.3)
    s.wait(3.6); s.mark("land"); s.fx("splash_small"); s.fx("ding8", s.t + 0.25); s.fx("sparkle", s.t + 0.3)
    s.wait(0.6)
    s.say("pip", "I've got you, Dot!", key="got", gap=0.3)
    s.say("dot", "You saved me!", key="saved", gap=0.8)

    def d10(c, t, s=s):
        lvl = 600
        leafx = 960
        jt, ld = s.M("jump"), s.M("land")
        z, cx, cy = 1.0, W / 2, H / 2
        if t < s.M("breath") + 1.4:
            z, cx, cy = 2.0, 330, 450
        elif t < jt:
            k = ease(ramp(t, s.M("brave"), s.M("brave") + 0.6))
            z, cx, cy = lerp(2.0, 1.6, k), 330, 450
        elif t < ld:
            k = ramp(t, jt, ld)
            z = lerp(1.6, 1.15, ease(min(1, k * 2))) if k < 0.85 else lerp(1.15, 1.8, ease((k - 0.85) / 0.15))
            cx = lerp(330, leafx, ease(k))
            cy = lerp(450, 420, k)
        else:
            z, cx, cy = 1.8, leafx, 440
        cam(c, z, cx, cy)
        world(c, t, 0.85, 0.0, play=False)
        draw_gus(c, 1080, lvl + 40 + math.sin(t * 2) * 4, 0.7, t, mouth=s.mouth("gus", t), face=-1, swim=True,
                 swim_phase=t * 0.2, helmet=1.0)
        water(c, lvl, t)
        swirl(c, 1180, lvl + 30, t, 1.0)
        rot = 14 + math.sin(t * 6) * 5 if t < ld else math.sin(t * 2) * 4
        leaf(c, leafx, lvl + 4, 0.75, rot)
        bob = math.sin(t * 2.2) * 5
        sandbox(c, 330, lvl + 12, 0.9, bob)
        # bitsy on pad near leaf
        lilypad(c, leafx - 120, lvl + 4, 0.55)
        draw_bitsy(c, leafx - 120, lvl + 2, 0.6, t, goggles_on=1.0, look=(-1, 0) if t < jt else (1, 0))
        brave_up = ease(ramp(t, s.M("breath"), s.M("breath") + 1.0))
        if t < jt:
            little = t < s.M("breath")
            draw_pip(c, 330, lvl - 26 + bob, 0.85 * (0.92 + 0.12 * brave_up), t, mouth=s.mouth("pip", t),
                     worried=1.0 if little else 0, look=(0, 0.2) if s.M("ask") < t < s.M("kids1") + 2 else (1, 0),
                     wing=1.0 * brave_up, cape_wind=0.3 + brave_up * 0.8, glow=brave_up, badge=0)
            if t > s.M("breath"):
                c.drawCircle(330, lvl - 26 + bob - 104 * 0.97, 18 + 6 * math.sin(t * 7), stroke(alpha(0xFFFFE15A, brave_up), 4))
        elif t < ld:
            k = ramp(t, jt, ld)
            px = lerp(330, leafx, k)
            py = lerp(lvl - 26, lvl - 10, k) - math.sin(k * math.pi) * 260
            for i in range(5):
                kk = k - i * 0.04
                if kk > 0:
                    ox = lerp(330, leafx, kk)
                    oy = lerp(lvl - 26, lvl - 10, kk) - math.sin(kk * math.pi) * 260
                    circle(c, ox - 30, oy - 80, 12 - i * 2, alpha(0xFFFFF3A0, 0.5 - i * 0.08), 0)
            draw_pip(c, px, py, 0.9, t * 0.35, wing=1.0, cape_wind=1.4, tilt=lerp(-15, 15, k))
            sparkles(c, px, py - 90, t, 10, 120)
        else:
            draw_pip(c, leafx - 20, lvl - 10, 0.9, t, mouth=s.mouth("pip", t), wing=0.3, look=(1, 0.3), cape_wind=0.5)
        # dot
        if t < ld:
            dx = 30
            draw_bug(c, leafx + dx, lvl - 22 + 9, 0.9, t, mouth=s.mouth("dot", t), look=(-1, 0))
        else:
            draw_bug(c, leafx + 26, lvl - 92, 0.8, t, mouth=s.mouth("dot", t), look=(-1, 0), face=-1)
            if t < ld + 1.0:
                sparkles(c, leafx, lvl - 90, t, 8, 80)
        c.restore()
        prompt(c, "YOU CAN DO IT, PIP!", t, s.M("cheer"), s.M("breath") + 0.2, y=100, size=66)
        prompt(c, "QUACK-QUACK-QUACK!", t, s.M("kids2"), s.M("call_end"), y=100)
        rain(c, t, 0.3)
    s.draw = d10
    S.append(s)

    # ---------------- 11. RIDE HOME + REUNION
    s = Scene("reunion", music="rescue", trans="splash", rain="light", music_gain=0.6)
    s.fx("boing", 0.3); s.fx("squelch", 0.7); s.fx("pop", 1.0)
    s.wait(1.2)
    s.mark("ride"); s.fx("creak")
    s.say("gus", "All... aboard... the hero... boat.", key="g1", gap=0.4)
    s.fx("buzz")
    s.say("mama", "Dot! Dot!", key="m1", gap=0.3)
    s.mark("shore"); s.fx("bonk")
    s.wait(0.5)
    s.mark("fly"); s.fx("buzz"); s.fx("sparkle", s.t + 0.6)
    s.wait(1.4)
    s.say("mama", "My little Dot! You're safe!", key="m2")
    s.say("dot", "The Puddle Patrol rescued me, Mama! They're real heroes!", key="d1", gap=0.4)
    s.mark("sun"); s.fx("pop"); s.fx("sparkle", s.t + 0.1)
    s.wait(1.0)
    s.mark("kids"); s.wait(1.9)
    s.say(["pip", "bitsy", "gus"], "Quack quack QUACK!", key="call", gap=0.2)
    s.fx("hero", s.M("call_end") - 0.3); s.fx("tada", s.M("call_end") + 0.4)
    s.wait(1.8)

    def d11(c, t, s=s):
        lvl = 600 + 40 * ease(ramp(t, s.M("sun"), s.M("sun") + 2))
        wthr = 0.85 * (1 - ease(ramp(t, s.M("sun"), s.M("sun") + 1.0)))
        sunv = ease(ramp(t, s.M("sun"), s.M("sun") + 1.0))
        gx = kf(t, [(s.M("ride"), 500), (s.M("shore"), 900)])
        cam(c, 1.15, lerp(600, 760, ease(ramp(t, s.M("ride"), s.M("shore")))), 450)
        world(c, t, wthr, sunv, play=False, bushx=1150)
        if t > s.M("sun"):
            rainbow(c, 640, 640, 560, ease(ramp(t, s.M("sun"), s.M("sun") + 1.5)), 0.6)
            bush(c, 1150)
        gy = lvl + 40 + math.sin(t * 2) * 4
        draw_gus(c, gx, gy, 0.75, t, mouth=s.mouth("gus", t), face=1, swim=True,
                 swim_phase=t * (0.6 if s.M("ride") < t < s.M("shore") else 0.1), helmet=1.0)
        # riders on the shell
        top = gy - 108 * 0.75
        k0 = ease(ramp(t, 0.1, 1.0))
        draw_bitsy(c, gx - 40, top + 6 + hop(t, 0.1, 0.5, 60), 0.5, t, mouth=s.mouth("bitsy", t), goggles_on=1.0)
        cheer_w = 1.0 if t > s.M("kids") else 0.4
        draw_pip(c, gx + 20, top + 8, 0.62, t, mouth=s.mouth("pip", t), wing=cheer_w, cape_wind=0.6)
        water(c, lvl, t)
        # dot + mama
        mx, my = 1150, 340
        ft = s.M("fly")
        if t < ft:
            draw_bug(c, gx + 60, top - 20, 0.7, t, mouth=s.mouth("dot", t))
        else:
            k = ease(ramp(t, ft, ft + 1.2))
            a = (t - ft) * 4
            r = 50 * (1 - k * 0.4)
            dx = lerp(gx + 60, mx + math.cos(a) * r, k)
            dy = lerp(top - 20, my + math.sin(a) * r * 0.6, k)
            draw_bug(c, dx, dy, 0.8, t, mouth=s.mouth("dot", t), flying=1.0, face=1 if math.cos(a) > 0 else -1)
            for i in range(4):
                ph = ((t - ft) * 0.7 + i / 4) % 1
                hp_ = skia.Path()
                hx, hy = mx - 40 + i * 30, my - 40 - ph * 100
                hp_.moveTo(hx, hy + 8)
                hp_.cubicTo(hx - 12, hy - 2, hx - 6, hy - 12, hx, hy - 5)
                hp_.cubicTo(hx + 6, hy - 12, hx + 12, hy - 2, hx, hy + 8)
                c.drawPath(hp_, fill(alpha(0xFFFF6B9A, 1 - ph)))
        mama_fly = 1.0 if t > ft else 0.4
        draw_bug(c, mx + (math.cos((t - ft) * 4 + math.pi) * 40 if t > ft else 0), my + (math.sin((t - ft) * 4 + math.pi) * 24 if t > ft else math.sin(t * 5) * 6),
                 1.3, t, mouth=s.mouth("mama", t), mama=True, flying=mama_fly, face=-1)
        if t > s.M("sun"):
            sparkles(c, 640, 300, t, 10, 300, 0xFFFFF07A, 5)
        c.restore()
        prompt(c, "QUACK-QUACK-QUACK!", t, s.M("kids"), s.M("call_end") + 0.4)
        rain(c, t, 0.35 * (1 - ramp(t, s.M("sun"), s.M("sun") + 0.6)))
    s.draw = d11
    S.append(s)

    # ---------------- 12. HERO BADGES
    s = Scene("badges", music="rainbow", trans="rainbow", music_gain=0.8)
    s.fx("buzz", 0.3)
    s.wait(1.0)
    s.say("mama", "Heroes who help get hero badges!", key="m1", gap=0.4)
    s.mark("b_bitsy"); s.fx("badge")
    s.say("mama", "Bitsy, for being fast!", key="m2", gap=0.2)
    for i in range(3):
        s.fx("boing", s.t + 0.1 + i * 0.3, 0.8)
    s.say("bitsy", "A badge! A badge! A BADGE!", key="b1", gap=0.4)
    s.mark("b_gus"); s.fx("badge")
    s.say("mama", "Gus, for being strong!", key="m3", gap=1.2)
    s.say("gus", "...Neat.", key="g1", gap=0.5)
    s.mark("roll"); s.fx("drumroll")
    s.wait(1.7)
    s.mark("b_pip"); s.fx("badge"); s.fx("choir", s.t + 0.1, 0.8)
    s.say("mama", "And Pip, for being brave!", key="m4", gap=0.3)
    s.fx("gasp")
    s.wait(0.5)
    s.mark("jump"); s.fx("cape", s.t + 1.0)
    s.say("pip", "I'm not a hero in training anymore. I'm a REAL hero!", key="p1", gap=0.4)
    s.say("pip", "And YOU helped too! You found Dot, you cheered for Bitsy, you helped Gus swim, and you helped me be brave!", key="p2", gap=0.3)
    s.mark("you"); s.fx("badge"); s.fx("sparkle", s.t + 0.3)
    s.wait(0.5)
    s.say("narr", "That means YOU are a Puddle Patrol hero too!", key="n1", gap=0.5)
    s.say("pip", "Remember the Hero Promise!", key="p3", gap=0.3)
    for k, line in (("look", "We look!"), ("brave", "We're brave!"), ("help", "We help!")):
        s.mark(k + "_show")
        s.say(["pip", "bitsy", "gus"], line, key=k, gap=0.1)
        s.fx("ding5")
        s.wait(0.5)
    s.say("gus", "Every... hero... has a... super... power.", key="g2", gap=0.2)
    s.say("bitsy", "Even little ones!", key="b2", gap=0.8)

    def d12(c, t, s=s):
        z, cx, cy = 1.0, W / 2, H / 2
        if s.M("roll") < t < s.M("p1"):
            k = ease(ramp(t, s.M("roll"), s.M("roll") + 0.8))
            z, cx, cy = lerp(1, 2.6, k), lerp(W / 2, 640, k), lerp(H / 2, 470, k)
        if s.M("you") < t < s.M("n1_end"):
            z = 1.0
        cam(c, z, cx, cy)
        world(c, t, 0.0, 1.0, play=True)
        rainbow(c, 640, 600, 620, 1.0, 0.55)
        for (px, r) in ((330, 120), (900, 90)):
            puddle(c, px, 680, r, 26)
        jp = s.M("jump")
        draw_gus(c, 360, 650, 0.85, t, mouth=s.mouth("gus", t), helmet=1.0, head_turn=0.8,
                 badge=ramp(t, s.M("b_gus") + 0.3, s.M("b_gus") + 0.7))
        draw_bitsy(c, 900, 650 + (hop((t - s.M("b1")) % 0.6, 0, 0.6, 50) if s.M("b1") < t < s.M("b1_end") else 0), 0.9, t,
                   mouth=s.mouth("bitsy", t), goggles_on=0.0, badge=ramp(t, s.M("b_bitsy") + 0.3, s.M("b_bitsy") + 0.7))
        pb = ramp(t, s.M("b_pip") + 0.3, s.M("b_pip") + 0.7)
        pj = hop(t, jp + 1.0, 0.7, 120)
        promise_pose = s.M("look_show") < t < s.M("help_end")
        draw_pip(c, 640, 660 + pj, 1.05, t, mouth=s.mouth("pip", t), badge=pb, glow=pb,
                 wing=1.0 if (jp + 0.9 < t < jp + 2.4 or promise_pose) else 0.3,
                 look=(0, -0.6) if s.M("m4") < t < s.M("p1") else (0, 0), cape_wind=0.6 + (0.8 if pj < 0 else 0))
        # mama delivers badges
        targets = [(900, 520, "b_bitsy"), (360, 520, "b_gus"), (640, 470, "b_pip")]
        mx, my = 1100, 260
        for (tx, ty, k) in targets:
            if t > s.M(k) - 0.5:
                kk = ease(ramp(t, s.M(k) - 0.5, s.M(k)))
                mx, my = lerp(mx, tx + 90, kk), lerp(my, ty - 120, kk)
        if t > s.M("you"):
            kk = ease(ramp(t, s.M("you"), s.M("you") + 0.8))
            mx, my = lerp(mx, 1100, kk), lerp(my, 220, kk)
        draw_bug(c, mx, my + math.sin(t * 5) * 6, 1.2, t, mouth=s.mouth("mama", t), mama=True, flying=1.0, face=-1)
        if pb > 0:
            sparkles(c, 640, 550, t, 8, 70)
        c.restore()
        if s.M("p1") < t < s.M("p1_end"):
            text(c, "REAL HERO!", W / 2, 110, 86, 0xFFFFC21A, scale=back_out((t - s.M("p1") - 1.6) / 0.4) if t > s.M("p1") + 1.6 else 0.0001)
        # viewer badge
        yt = s.M("you")
        if yt < t < s.M("n1_end") + 0.4:
            k = back_out((t - yt) / 0.6)
            fade = 1 - ramp(t, s.M("n1_end"), s.M("n1_end") + 0.4)
            c.saveLayerAlpha(None, int(255 * fade))
            c.drawPaint(fill(alpha(0xFF2B2340, 0.45)))
            c.save(); c.translate(W / 2, H / 2); c.scale(k, k); c.rotate(math.sin(t * 3) * 5)
            burst(c, 0, 0, 260, t * 0.4, 0xFFFFE15A)
            path_draw(c, star_path(0, -10, 190, 85), 0xFFFFC21A, 8)
            text(c, "YOU!", 0, -10, 80, 0xFFFFFFFF)
            c.restore()
            text(c, "PUDDLE PATROL HERO", W / 2, 640, 60, 0xFFFFFFFF, scale=k)
            sparkles(c, W / 2, H / 2, t, 16, 330)
            c.restore()
        for i, k in enumerate(("look", "brave", "help")):
            st = s.M(k + "_show")
            if st < t < s.M("g2"):
                icon_bubble(c, 360 + i * 280, 130, 64, t, k, ramp(t, st, st + 0.3))
                lbl = {"look": "WE LOOK!", "brave": "WE'RE BRAVE!", "help": "WE HELP!"}[k]
                text(c, lbl, 360 + i * 280, 235, 38, 0xFFE8343B, scale=back_out((t - st) / 0.3))
    s.draw = d12
    S.append(s)

    # ---------------- 13. SIGN-OFF
    s = Scene("signoff", music="rainbow", trans="bubble", music_gain=0.7)
    s.wait(0.6); s.mark("drop"); s.fx("ding7", s.t + 0.6)
    s.wait(1.2); s.mark("leap"); s.fx("cape"); s.fx("splash", s.t + 0.7)
    s.wait(0.8)
    s.say("pip", "See you next splash, heroes!", key="p1", gap=0.3)
    s.say("gus", "Bye... bye...", key="g1", gap=0.2)
    s.mark("zip"); s.fx("zoom")
    s.say("bitsy", "Bye bye bye bye bye!", key="b1", gap=0.2)
    s.fx("buzz")
    s.say("dot", "Thank you, heroes!", key="d1", gap=1.0)

    def d13(c, t, s=s):
        world(c, t, 0.0, 1.0, play=True)
        rainbow(c, 640, 600, 620, 1.0, 0.55)
        puddle(c, 640, 670, 200, 46)
        draw_gus(c, 300, 650, 0.85, t, mouth=s.mouth("gus", t), helmet=1.0, head_turn=0.9, badge=1.0)
        # bitsy zips across waving
        zt = s.M("zip")
        if t < zt:
            draw_bitsy(c, 980, 650, 0.85, t, goggles_on=0.0, badge=1.0)
        else:
            bx = kf(t, [(zt, 980), (zt + 1.6, 1500)], lambda x: x)
            draw_bitsy(c, bx, 650 + hop((t - zt) % 0.3, 0, 0.3, 40), 0.85, t, mouth=s.mouth("bitsy", t), goggles_on=1.0, badge=1.0)
            speed_lines(c, bx - 60, 600, -1, 5, 120)
        lp_ = s.M("leap")
        if t < lp_:
            dt = s.M("drop")
            if dt < t < dt + 0.7:
                yy = kf(t, [(dt, 100), (dt + 0.6, 470)], lambda x: x * x)
                dp = skia.Path()
                dp.moveTo(640, yy - 18); dp.cubicTo(654, yy, 652, yy + 14, 640, yy + 14); dp.cubicTo(628, yy + 14, 626, yy, 640, yy - 18)
                path_draw(c, dp, 0xFF5BBDFF, 3)
            draw_pip(c, 640, 560, 1.0, t, badge=1.0, look=(0, -1) if t > s.M("drop") else (0, 0))
            c.drawRect(skia.Rect.MakeLTRB(0, 0, 0, 0), fill(0))
        else:
            k = ramp(t, lp_, lp_ + 0.7)
            if t < lp_ + 0.7:
                draw_pip(c, 640, lerp(560, 670, k) - math.sin(k * math.pi) * 160, 1.0, t, badge=1.0, wing=1.0, cape_wind=1.2)
            else:
                c.save(); c.clipRect(skia.Rect.MakeLTRB(0, 0, W, 670))
                draw_pip(c, 640, lerp(740, 680, ease_out(ramp(t, lp_ + 0.8, lp_ + 1.2))), 1.0, t, mouth=s.mouth("pip", t), badge=1.0, wing=1.0)
                c.restore()
            splash_fx(c, 640, 670, lp_ + 0.7, t, 1.4)
        # bugs loop through the rainbow
        if t > s.M("b1"):
            k = ramp(t, s.M("b1"), s.dur)
            a = k * math.pi
            x = 640 - math.cos(a) * 520
            y = 600 - math.sin(a) * 520
            draw_bug(c, x, y, 1.0, t, mouth=s.mouth("dot", t), flying=1.0)
            draw_bug(c, x - 60, y + 30, 1.3, t, mama=True, flying=1.0)
    s.draw = d13
    S.append(s)

    # ---------------- 14. OUTRO SONG + TEASE
    s = Scene("outro", music="theme", trans="rainbow", music_gain=1.2)
    lines = [("narr", "The rain is gone, and Dot is safe!"), ("narr", "Being brave helps everyone!"),
             ("pip", "Fast or strong or small, hooray!"), (["pip", "bitsy"], "Every hero saves the day!"),
             (["pip", "bitsy"], "Quack quack QUACK!")]
    s.wait(0.4)
    for i, (w, l) in enumerate(lines):
        s.say(w, l, key=f"o{i}", gap=0.6)
    s.fx("hero", s.M("o4_end") - 0.2)
    s.wait(1.2)
    s.mark("tease"); s.fx("squelch", s.t + 0.3); s.fx("squelch", s.t + 0.8); s.fx("squelch", s.t + 1.3); s.fx("pop", s.t + 1.8)
    s.wait(2.0); s.fx("gasp")
    s.say("pip", "Who left these muddy footprints?", key="t1", gap=0.2)
    s.say("narr", "Next time, on Puddle Patrol!", key="t2", gap=0.4)
    s.mark("logo"); s.fx("pop"); s.fx("tada", s.t + 0.2)
    s.wait(3.5)

    def d14(c, t, s=s):
        if t < s.M("tease"):
            hero_rays(c, t, 0xFF6CC8FF, 0xFF8ED8FF)
            rainbow(c, 640, 760, 600, 1.0, 0.8)
            for i, (fn, x) in enumerate(((draw_gus, 330), (draw_pip, 640), (draw_bitsy, 950))):
                bounce = hop((t + i * 0.25) % 1.0, 0, 1.0, 40)
                if fn is draw_gus:
                    fn(c, x, 640 + bounce * 0.4, 0.85, t, helmet=1.0, badge=1.0, head_turn=0.9)
                elif fn is draw_pip:
                    fn(c, x, 650 + bounce, 1.05, t, mouth=s.mouth("pip", t), badge=1.0, wing=0.5 + 0.5 * math.sin(t * 4), cape_wind=0.8)
                else:
                    fn(c, x, 650 + bounce, 0.95, t, mouth=s.mouth("bitsy", t), badge=1.0, goggles_on=0.0)
            txts = [l for _, l in lines]
            for i in range(4):
                st = s.M(f"o{i}")
                lyric(c, txts[i], t, st, s.M(f"o{i + 1}"), y=110)
            if t > s.M("o4"):
                sc = back_out((t - s.M("o4")) / 0.4)
                burst(c, 640, 130, 130 * sc, t)
                text(c, "QUACK!", 640, 130, 74, 0xFFE8343B, scale=sc)
        else:
            tt = t - s.M("tease")
            c.drawPaint(fill(0xFFFFF4D6))
            for i in range(6):
                st = 0.3 + i * 0.25
                if tt > st:
                    x = 140 + i * 190
                    y = 470 + (i % 2) * 60
                    sc = back_out((tt - st) / 0.25)
                    c.save(); c.translate(x, y); c.rotate(-10); c.scale(sc, sc)
                    oval(c, 0, 0, 30, 46, 0xFF8B5A2B, 0)
                    for k in range(3):
                        circle(c, -20 + k * 20, -60, 10, 0xFF8B5A2B, 0)
                    c.restore()
            if tt > 1.8:
                k = back_out((tt - 1.8) / 0.4)
                c.save(); c.clipRect(skia.Rect.MakeLTRB(0, 0, W, H))
                draw_pip(c, lerp(1500, 1060, k), 760, 1.4, t, mouth=s.mouth("pip", t), badge=1.0, look=(-1, 0), face=-1, tilt=-12)
                c.restore()
            if t > s.M("t2"):
                text(c, "NEXT TIME...", 500, 170, 70, 0xFF3D8BFF, scale=back_out((t - s.M("t2")) / 0.4))
            if t > s.M("logo"):
                k = back_out((t - s.M("logo")) / 0.5)
                c.drawPaint(fill(alpha(0xFF3D8BFF, min(1, (t - s.M("logo")) * 3))))
                hero_rays(c, t, 0xFF3D8BFF, 0xFF64A8FF) if t > s.M("logo") + 0.34 else None
                text(c, "PIP & THE", 640, 230, 70, 0xFFFFFFFF, scale=k)
                text(c, "PUDDLE PATROL", 640, 330, 110, 0xFFFFD93B, scale=k, ow=16)
                draw_pip(c, 640, 640, 1.1 * k, t, badge=1.0, wing=1.0, cape_wind=1.0)
                text(c, "SEE YOU NEXT SPLASH!", 640, 680, 40, 0xFFFFFFFF, scale=k)
    s.draw = d14
    S.append(s)
    return S
