"""Drawing kit for Pip & the Puddle Patrol: characters, world, effects, transitions.
All coordinates are in a 1280x720 design space."""
import math, os
import skia

W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))
INK = 0xFF2B2340
TITLE_TF = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", "LuckiestGuy.ttf"))
ROUND_TF = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", "Fredoka.ttf"))


# ---------- helpers ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def ramp(t, a, b):
    if b <= a:
        return 1.0 if t >= a else 0.0
    return clamp((t - a) / (b - a))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def back_out(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def lerp(a, b, x):
    return a + (b - a) * x

def kf(t, keys, fn=ease):
    """Keyframes [(time, value), ...] with easing between them."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, fn((t - t0) / (t1 - t0) if t1 > t0 else 1))
    return keys[-1][1]

def hop(t, start, dur, height):
    """Parabolic jump offset (negative = up)."""
    x = (t - start) / dur
    if x < 0 or x > 1:
        return 0.0
    return -4 * height * x * (1 - x)

def hsh(i, k=0):
    v = math.sin(i * 127.1 + k * 311.7) * 43758.5453
    return v - math.floor(v)

def mix(c1, c2, x):
    x = clamp(x)
    a = [(c1 >> s) & 255 for s in (24, 16, 8, 0)]
    b = [(c2 >> s) & 255 for s in (24, 16, 8, 0)]
    r = [int(lerp(p, q, x)) for p, q in zip(a, b)]
    return (r[0] << 24) | (r[1] << 16) | (r[2] << 8) | r[3]

def alpha(c, a):
    return (int(clamp(a) * 255) << 24) | (c & 0xFFFFFF)

def fill(color):
    return skia.Paint(AntiAlias=True, Color=color)

def stroke(color=INK, w=5.0, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Color=color, Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeCap(cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def oval(c, x, y, rx, ry, color, ow=5.0, oc=INK):
    r = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
    c.drawOval(r, fill(color))
    if ow:
        c.drawOval(r, stroke(oc, ow))

def circle(c, x, y, r, color, ow=5.0, oc=INK):
    oval(c, x, y, r, r, color, ow, oc)

def path_draw(c, p, color, ow=5.0, oc=INK):
    c.drawPath(p, fill(color))
    if ow:
        c.drawPath(p, stroke(oc, ow))

def star_path(x, y, r1, r2, n=5, rot=-math.pi / 2):
    p = skia.Path()
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = rot + i * math.pi / n
        (p.moveTo if i == 0 else p.lineTo)(x + r * math.cos(a), y + r * math.sin(a))
    p.close()
    return p

def text(c, s, x, y, size, color=0xFFFFFFFF, tf=None, ow=None, oc=INK, align="center", scale=1.0, rot=0.0):
    font = skia.Font(tf or TITLE_TF, size)
    wdt = font.measureText(s)
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(scale, scale)
    ox = -wdt / 2 if align == "center" else 0
    blob = skia.TextBlob.MakeFromString(s, font)
    if ow is None:
        ow = size * 0.16
    if ow:
        c.drawTextBlob(blob, ox, size * 0.35, stroke(oc, ow))
    c.drawTextBlob(blob, ox, size * 0.35, fill(color))
    c.restore()
    return wdt


# ---------- characters ----------
def blink_amt(t, seed=0.0):
    period = 3.3 + seed
    ph = (t + seed * 1.7) % period
    return 1.0 if ph < 0.13 else 0.0

def eye(c, x, y, rx, ry, look=(0, 0), closed=0.0, lid=0.0, pupil=0.55, shine=True):
    """Cartoon eye. lid = sleepy top lid fraction, closed = blink."""
    ry_eff = ry * (1 - 0.92 * closed)
    oval(c, x, y, rx, max(ry_eff, 1.5), 0xFFFFFFFF, 3.5)
    if closed < 0.6:
        pr = rx * pupil
        px = x + look[0] * rx * 0.35
        py = y + look[1] * ry * 0.3 + ry * 0.1
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - rx, y - ry_eff, x + rx, y + ry_eff))
        circle(c, px, py, pr, INK, 0)
        if shine:
            circle(c, px - pr * 0.35, py - pr * 0.4, pr * 0.35, 0xFFFFFFFF, 0)
        c.restore()
    if lid > 0 and closed < 0.6:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - rx - 3, y - ry - 3, x + rx + 3, y - ry + 2 * ry * lid))
        oval(c, x, y, rx, ry, 0xFF5DBB63, 3.5)
        c.restore()
        c.drawLine(x - rx * 0.95, y - ry + 2 * ry * lid, x + rx * 0.95, y - ry + 2 * ry * lid, stroke(INK, 3.5))


def draw_pip(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, wing=0.0, badge=0.0,
             cape_wind=0.3, squash=0.0, tilt=0.0, blink=None, cape=True, boots=True, worried=0.0, glow=0.0):
    """Pip the duckling. (x, y) = point between his feet."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s * face * (1 + squash * 0.18), s * (1 - squash * 0.18))
    YEL, ORA, RED, BLUE = 0xFFFFD93B, 0xFFFF9A1F, 0xFFE8343B, 0xFF3D8BFF
    # cape behind
    if cape:
        wv = math.sin(t * 7.0) * 10 * (0.4 + cape_wind)
        p = skia.Path()
        p.moveTo(-26, -112)
        p.cubicTo(-60 - 40 * cape_wind, -90, -80 - 60 * cape_wind, -50 + wv, -78 - 70 * cape_wind, -12 + wv * 0.6)
        p.cubicTo(-50 - 40 * cape_wind, -8 + wv, -20, -30, 22, -108)
        p.close()
        path_draw(c, p, BLUE)
    # boots
    if boots:
        for bx in (-22, 22):
            r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(bx - 17, -34, bx + 19, 0), 9, 9)
            c.drawRRect(r, fill(RED))
            c.drawRRect(r, stroke())
            c.drawLine(bx - 15, -24, bx + 17, -24, stroke(0xFFFF8A8A, 4))
    else:
        for bx in (-20, 20):
            oval(c, bx + 6, -4, 18, 7, ORA, 4)
    # body
    oval(c, 0, -72, 56, 50, YEL)
    # belly highlight
    oval(c, 4, -64, 34, 28, 0xFFFFEA85, 0)
    # wing (raise -1..1)
    c.save()
    c.translate(-40, -78)
    c.rotate(-30 - wing * 70)
    oval(c, -6, 14, 16, 28, 0xFFF5C52A, 4.5)
    c.restore()
    c.save()
    c.translate(44, -80)
    c.rotate(20 + wing * 80)
    oval(c, 4, 14, 14, 24, 0xFFF5C52A, 4.5)
    c.restore()
    # cape clasp / badge spot
    if cape:
        if badge <= 0.0:
            circle(c, 0, -104, 13, 0xFF2F6FD6, 4)
            dash = stroke(0xFFFFD45C, 3.5)
            dash.setPathEffect(skia.DashPathEffect.Make([5, 5], t * 10))
            c.drawCircle(0, -104, 8, dash)
        else:
            bs = back_out(badge)
            if glow:
                circle(c, 0, -104, 30 + 6 * math.sin(t * 6), alpha(0xFFFFF3A0, 0.45 * glow), 0)
            path_draw(c, star_path(0, -104, 19 * bs, 8.5 * bs), 0xFFFFC21A, 4)
            circle(c, -4, -108, 3 * bs, 0xFFFFFFFF, 0)
    # head
    hy = -142
    circle(c, 0, hy, 44, YEL)
    # tuft
    tp = skia.Path()
    tp.moveTo(-6, hy - 40)
    tp.cubicTo(-14, hy - 66, 6, hy - 64, 2, hy - 42)
    tp.cubicTo(10, hy - 62, 24, hy - 52, 10, hy - 38)
    path_draw(c, tp, YEL, 4)
    # cheeks
    circle(c, -28, hy + 14, 8, 0x66FF7A9A, 0)
    circle(c, 30, hy + 14, 8, 0x66FF7A9A, 0)
    bl = blink_amt(t, 0.3) if blink is None else blink
    eye(c, -15, hy - 6, 12, 16, look, bl)
    eye(c, 19, hy - 6, 12, 16, look, bl)
    if worried > 0:
        c.drawLine(-25, hy - 28 + 4 * worried, -6, hy - 26 - 2 * worried, stroke(INK, 4))
        c.drawLine(29, hy - 28 + 4 * worried, 10, hy - 26 - 2 * worried, stroke(INK, 4))
    # beak
    m = clamp(mouth)
    lo = skia.Path()
    lo.moveTo(-4, hy + 14)
    lo.cubicTo(8, hy + 16 + 18 * m, 36, hy + 18 + 14 * m, 48, hy + 12 + 6 * m)
    lo.lineTo(30, hy + 12)
    lo.close()
    path_draw(c, lo, 0xFFE07C10, 4)
    if m > 0.1:
        oval(c, 24, hy + 15 + 6 * m, 12, 5 * m, 0xFFB0303A, 0)
    up = skia.Path()
    up.moveTo(-6, hy + 12)
    up.cubicTo(10, hy - 6, 40, hy - 2, 56, hy + 10 - 2 * m)
    up.cubicTo(40, hy + 18 - 2 * m, 12, hy + 18, -6, hy + 12)
    up.close()
    path_draw(c, up, ORA, 4)
    c.restore()


def draw_gus(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, helmet=-1.0, head_turn=0.0,
             blink=None, swim=False, swim_phase=0.0, badge=0.0, sand=0.0, head_out=1.0, bob=0.0):
    """Gus the turtle. helmet: -1 none, 0..1 rising onto head, >=1 on. head_turn: 0 facing side, 1 facing camera."""
    c.save()
    c.translate(x, y + bob)
    c.scale(s * face, s)
    G, GD, SH, SHD = 0xFF8BD17C, 0xFF5DBB63, 0xFF3FA65A, 0xFF2E7D4A
    # legs
    if not swim:
        for lx in (-70, -30, 40, 78):
            oval(c, lx, -12, 20, 16, G, 4.5)
    else:
        for i, lx in enumerate((-80, 80)):
            a = math.sin(swim_phase * math.tau + i * math.pi) * 25
            c.save()
            c.translate(lx, -30)
            c.rotate(a + (30 if lx > 0 else -30))
            oval(c, 0, 18, 14, 30, G, 4.5)
            c.restore()
    # shell
    sp = skia.Path()
    sp.moveTo(-112, -30)
    sp.cubicTo(-112, -150, 112, -150, 112, -30)
    sp.close()
    path_draw(c, sp, SH, 5)
    # plates
    c.save()
    c.clipPath(sp, doAntiAlias=True)
    for (px, py, pr) in ((0, -86, 28), (-56, -64, 24), (56, -64, 24), (-30, -40, 18), (30, -40, 18), (-90, -36, 14), (90, -36, 14)):
        hexp = skia.Path()
        for k in range(6):
            a = math.pi / 6 + k * math.pi / 3
            (hexp.moveTo if k == 0 else hexp.lineTo)(px + pr * math.cos(a), py + pr * math.sin(a))
        hexp.close()
        path_draw(c, hexp, 0xFF56C06E, 3.5, SHD)
    # moss
    for i in range(5):
        circle(c, -70 + i * 34, -120 + (i % 2) * 8, 7, 0xFF9BDB6A, 0)
    c.restore()
    # rim
    rim = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-118, -38, 118, -18), 10, 10)
    c.drawRRect(rim, fill(0xFFE9D27A))
    c.drawRRect(rim, stroke())
    # head + neck
    hx, hy = 122 * head_out, -92
    neck = skia.Path()
    neck.moveTo(60, -48)
    neck.cubicTo(80, -66, 95 * head_out, -96, hx - 14, hy - 18)
    neck.lineTo(hx - 4, hy + 30)
    neck.cubicTo(95 * head_out, -40, 80, -30, 60, -24)
    neck.close()
    path_draw(c, neck, G, 4.5)
    circle(c, hx, hy, 46, G, 5)
    bl = blink_amt(t, 1.1) if blink is None else blink
    ex = 12 * (1 - head_turn)
    eye(c, hx - 14 + ex, hy - 10, 11, 13, look, bl, lid=0.45)
    eye(c, hx + 14 + ex, hy - 10, 11, 13, look, bl, lid=0.45)
    m = clamp(mouth)
    mx = hx + ex
    if m > 0.08:
        oval(c, mx, hy + 16, 12, 4 + 10 * m, 0xFF8A2B36, 4)
    else:
        p = skia.Path()
        p.moveTo(mx - 16, hy + 12)
        p.quadTo(mx, hy + 24, mx + 16, hy + 12)
        c.drawPath(p, stroke(INK, 4))
    circle(c, mx - 26, hy + 8, 6, 0x55FF7A9A, 0)
    circle(c, mx + 26, hy + 8, 6, 0x55FF7A9A, 0)
    # helmet (acorn cap)
    if helmet >= 0:
        hh = ease_out(min(helmet, 1.0))
        cy = hy - 34 - (1 - hh) * 70
        cap = skia.Path()
        cap.moveTo(hx - 36, cy + 8)
        cap.cubicTo(hx - 36, cy - 30, hx + 36, cy - 30, hx + 36, cy + 8)
        cap.close()
        path_draw(c, cap, 0xFFA8692E, 4.5)
        for i in range(-2, 3):
            c.drawLine(hx + i * 13 - 8, cy - 14, hx + i * 13 + 8, cy + 6, stroke(0xFF7A4A1E, 3))
        c.drawRect(skia.Rect.MakeLTRB(hx - 3, cy - 30, hx + 3, cy - 18), fill(0xFF7A4A1E))
    if badge > 0:
        bs = back_out(badge)
        circle(c, 0, -86, 20 * bs, 0xFFFFC21A, 4)
        hp = skia.Path()
        hp.moveTo(0, -78 * 1)
        hp.cubicTo(-14 * bs, -88, -8 * bs, -100, 0, -92)
        hp.cubicTo(8 * bs, -100, 14 * bs, -88, 0, -78)
        path_draw(c, hp, 0xFFE8343B, 2.5)
    if sand > 0:
        sp2 = skia.Path()
        sp2.moveTo(hx - 30, hy - 32)
        sp2.cubicTo(hx - 30, hy - 70 - 30 * sand, hx + 30, hy - 70 - 30 * sand, hx + 30, hy - 32)
        sp2.close()
        path_draw(c, sp2, 0xFFF2CF7A, 4)
        c.drawRect(skia.Rect.MakeLTRB(hx - 6, hy - 92 - 30 * sand, hx + 6, hy - 70 - 30 * sand), fill(0xFFF2CF7A))
    c.restore()


def draw_bitsy(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, goggles_on=1.0, squash=0.0,
               blink=None, badge=0.0, stretch=0.0, tilt=0.0):
    """Bitsy the frog. goggles_on: 0 = up on forehead, 1 = over eyes."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s * face * (1 + squash * 0.2), s * (1 - squash * 0.2 + stretch * 0.2))
    G, GL, GD = 0xFF8EE04E, 0xFFC8F59A, 0xFF5FB52E
    # back legs
    for sx in (-1, 1):
        oval(c, sx * 42, -22, 26, 20, GD, 4.5)
        oval(c, sx * 56, -4, 22, 7, G, 4)
    # body
    oval(c, 0, -52, 52, 44, G)
    oval(c, 0, -40, 32, 24, GL, 0)
    # front feet
    for sx in (-1, 1):
        oval(c, sx * 18, -6, 12, 7, G, 4)
    # eye bumps
    bl = blink_amt(t, 2.2) if blink is None else blink
    for sx in (-1, 1):
        circle(c, sx * 26, -92, 22, G, 5)
        eye(c, sx * 26, -94, 14, 15, look, bl)
    # goggles
    gy = lerp(-132, -94, goggles_on)
    c.drawLine(-48, gy, 48, gy, stroke(0xFFFF6B3D, 7))
    for sx in (-1, 1):
        lens = skia.Paint(AntiAlias=True, Color=0x667FE0FF)
        c.drawCircle(sx * 26, gy, 18, lens)
        c.drawCircle(sx * 26, gy, 18, stroke(0xFFFF8A00, 6))
        c.drawCircle(sx * 26, gy, 18, stroke(INK, 2.5))
        c.drawLine(sx * 26 - 8, gy - 8, sx * 26 - 2, gy - 12, stroke(0xCCFFFFFF, 3))
    if badge > 0:
        bs = back_out(badge)
        bolt = skia.Path()
        bolt.moveTo(4 * bs, gy - 14 * bs)
        bolt.lineTo(-8 * bs, gy + 2 * bs)
        bolt.lineTo(0, gy + 2 * bs)
        bolt.lineTo(-4 * bs, gy + 14 * bs)
        bolt.lineTo(8 * bs, gy - 2 * bs)
        bolt.lineTo(0, gy - 2 * bs)
        bolt.close()
        circle(c, 0, gy, 14 * bs, 0xFFFFC21A, 3.5)
        path_draw(c, bolt, 0xFFFFFFFF, 2)
    # mouth
    m = clamp(mouth)
    if m > 0.08:
        mp = skia.Path()
        mp.moveTo(-30, -64)
        mp.quadTo(0, -60 + 30 * m, 30, -64)
        mp.close()
        path_draw(c, mp, 0xFF8A2B36, 4)
        oval(c, 0, -64 + 10 * m, 10, 4 * m, 0xFFFF8FA3, 0)
    else:
        mp = skia.Path()
        mp.moveTo(-32, -66)
        mp.quadTo(0, -46, 32, -66)
        c.drawPath(mp, stroke(INK, 4.5))
    circle(c, -38, -60, 7, 0x55FF7A9A, 0)
    circle(c, 38, -60, 7, 0x55FF7A9A, 0)
    c.restore()


def draw_bug(c, x, y, s=1.0, t=0.0, mouth=0.0, flying=0.0, face=1, look=(0, 0), mama=False, blink=None, rot=0.0):
    """Dot (or Mama Bug). (x, y) is the center of the shell."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s * face, s)
    R = 22
    if flying > 0:
        fl = math.sin(t * 60) * 0.5 + 0.5
        for sx in (-1, 1):
            c.save()
            c.rotate(sx * (20 + 25 * fl))
            oval(c, sx * 16, -22, 12, 22, alpha(0xFFE6F7FF, 0.75 * flying), 2.5, alpha(INK, 0.6 * flying))
            c.restore()
    # legs
    for i in (-1, 0, 1):
        c.drawLine(i * 10, R - 4, i * 13, R + 6, stroke(INK, 3))
    # head
    circle(c, R * 0.95, -2, 12, INK, 0)
    bl = blink_amt(t, 0.7) if blink is None else blink
    eye(c, R * 0.95 + 1, -6, 5, 6, look, bl, pupil=0.6, shine=False)
    eye(c, R * 0.95 + 10, -6, 5, 6, look, bl, pupil=0.6, shine=False)
    if mama:
        for k in range(3):
            c.drawLine(R * 0.95 - 2 + k * 4, -12, R * 0.95 - 4 + k * 5, -17, stroke(INK, 2))
    m = clamp(mouth)
    if m > 0.1:
        oval(c, R * 0.95 + 6, 4, 4, 1.5 + 3 * m, 0xFFFF8FA3, 0)
    else:
        mp = skia.Path()
        mp.moveTo(R * 0.95 + 1, 3)
        mp.quadTo(R * 0.95 + 6, 7, R * 0.95 + 11, 3)
        c.drawPath(mp, stroke(0xFFFFFFFF, 2))
    # antennae
    for dx in (-3, 6):
        ap = skia.Path()
        ap.moveTo(R * 0.95 + dx, -12)
        ap.quadTo(R * 0.95 + dx + 4, -26, R * 0.95 + dx + 10, -26)
        c.drawPath(ap, stroke(INK, 2.5))
        circle(c, R * 0.95 + dx + 10, -26, 2.5, INK, 0)
    # shell
    circle(c, 0, 0, R, 0xFFE8343B, 4)
    c.drawLine(0, -R, 0, R, stroke(INK, 3))
    for (sx, sy, sr) in ((-11, -9, 5), (10, -10, 5), (-12, 8, 4.5), (11, 8, 4.5), (0, 15, 3.5)):
        circle(c, sx, sy, sr, INK, 0)
    circle(c, -8, -14, 3, 0x88FFFFFF, 0)
    if mama:
        for sx in (-1, 1):
            bp = skia.Path()
            bp.moveTo(R * 0.95, -14)
            bp.lineTo(R * 0.95 + sx * 12, -24)
            bp.lineTo(R * 0.95 + sx * 12, -6)
            bp.close()
            path_draw(c, bp, 0xFFFF7AB6, 2)
        circle(c, R * 0.95, -14, 3, 0xFFFF7AB6, 2)
    c.restore()


# ---------- world ----------
def sky(c, weather=0.0, night=0.0):
    top = mix(0xFF6CC8FF, 0xFF8796AA, weather)
    bot = mix(0xFFD6F3FF, 0xFFC4D0DB, weather)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [top, bot])
    c.drawPaint(skia.Paint(Shader=sh))

def sun(c, x, y, t, vis=1.0, r=56):
    if vis <= 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(t * 12)
    for i in range(12):
        a = i * math.tau / 12
        c.drawLine(math.cos(a) * (r + 12), math.sin(a) * (r + 12), math.cos(a) * (r + 34), math.sin(a) * (r + 34),
                   stroke(alpha(0xFFFFC93C, vis), 9))
    c.restore()
    circle(c, x, y, r, alpha(0xFFFFE15A, vis), 5, alpha(0xFFF2A81D, vis))
    if vis > 0.5:
        eye(c, x - 18, y - 6, 6, 8, (0, 0), blink_amt(t, 4))
        eye(c, x + 18, y - 6, 6, 8, (0, 0), blink_amt(t, 4))
        mp = skia.Path()
        mp.moveTo(x - 16, y + 14)
        mp.quadTo(x, y + 28, x + 16, y + 14)
        c.drawPath(mp, stroke(INK, 4))

def cloud(c, x, y, s=1.0, color=0xFFFFFFFF):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    parts = ((-60, 10, 38), (-20, -14, 50), (34, -6, 44), (70, 14, 32), (0, 20, 40))
    for (cx, cy, r) in parts:
        c.drawCircle(cx, cy, r + 2.5, fill(alpha(INK, 0.22)))
    for (cx, cy, r) in parts:
        c.drawCircle(cx, cy, r, fill(color))
    c.restore()

def clouds(c, t, weather=0.0, n=4, y0=120):
    col = mix(0xFFFFFFFF, 0xFF9AA6B5, weather)
    for i in range(n + int(weather * 3)):
        x = ((hsh(i, 1) * 1600 + t * (12 + hsh(i, 2) * 14)) % 1700) - 220
        y = y0 + hsh(i, 3) * 110 - weather * 30
        cloud(c, x, y, 0.8 + hsh(i, 4) * 0.6 + weather * 0.3, col)

def hills(c, weather=0.0):
    p = skia.Path()
    p.moveTo(-700, 500)
    p.cubicTo(-400, 420, -200, 430, 0, 520)
    p.cubicTo(200, 400, 420, 430, 640, 500)
    p.cubicTo(860, 420, 1080, 410, 1280, 490)
    p.cubicTo(1500, 420, 1700, 440, 2000, 500)
    p.lineTo(2000, 1300)
    p.lineTo(-700, 1300)
    p.close()
    c.drawPath(p, fill(mix(0xFF9EDB7E, 0xFF86B07A, weather)))

GROUND_Y = 560

def ground(c, weather=0.0, y=GROUND_Y):
    g = mix(0xFF6CCB5F, 0xFF5AA055, weather)
    c.drawRect(skia.Rect.MakeLTRB(-700, y, W + 700, H + 600), fill(g))
    c.drawLine(-700, y, W + 700, y, stroke(mix(0xFF4FA845, 0xFF467F42, weather), 6))
    for i in range(40):
        gx = hsh(i, 9) * W
        gy = y + 20 + hsh(i, 8) * 140
        p = skia.Path()
        p.moveTo(gx - 6, gy)
        p.lineTo(gx, gy - 12)
        p.lineTo(gx + 6, gy)
        c.drawPath(p, stroke(mix(0xFF56B64B, 0xFF4A8A46, weather), 3))

def slide(c, x, y=GROUND_Y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    # ladder
    for lx in (-80, -40):
        c.drawLine(lx, 0, lx, -230, stroke(INK, 14))
        c.drawLine(lx, 0, lx, -230, stroke(0xFF4A90E2, 8))
    for k in range(6):
        c.drawLine(-80, -30 - k * 36, -40, -30 - k * 36, stroke(0xFF4A90E2, 7))
    plat = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-92, -246, -20, -226), 6, 6)
    c.drawRRect(plat, fill(0xFFFFD93B)); c.drawRRect(plat, stroke())
    sp = skia.Path()
    sp.moveTo(-30, -240)
    sp.cubicTo(40, -230, 80, -40, 170, -20)
    sp.lineTo(170, 4)
    sp.cubicTo(70, -10, 30, -210, -30, -212)
    sp.close()
    path_draw(c, sp, 0xFFE8343B)
    c.restore()

def swings(c, x, y=GROUND_Y, t=0.0, swing=0.0, s=1.0, seat_items=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-130, 130):
        c.drawLine(lx, 0, lx * 0.8, -260, stroke(INK, 16))
        c.drawLine(lx, 0, lx * 0.8, -260, stroke(0xFFFFC21A, 10))
    c.drawLine(-120, -260, 120, -260, stroke(INK, 18))
    c.drawLine(-120, -260, 120, -260, stroke(0xFFFFC21A, 12))
    seats = []
    for i, sx in enumerate((-55, 55)):
        a = math.sin(t * 2 + i) * swing * 18
        c.save()
        c.translate(sx, -258)
        c.rotate(a)
        c.drawLine(-20, 0, -20, 190, stroke(INK, 4))
        c.drawLine(20, 0, 20, 190, stroke(INK, 4))
        seat = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-30, 186, 30, 200), 5, 5)
        c.drawRRect(seat, fill(0xFF3D8BFF)); c.drawRRect(seat, stroke(INK, 4))
        c.restore()
    c.restore()

def sandbox(c, x, y=GROUND_Y + 40, s=1.0, bob=0.0):
    c.save(); c.translate(x, y + bob); c.scale(s, s)
    box = skia.Path()
    box.moveTo(-120, -40); box.lineTo(120, -40); box.lineTo(100, 10); box.lineTo(-100, 10); box.close()
    path_draw(c, box, 0xFF3D8BFF)
    sand = skia.Path()
    sand.moveTo(-112, -40); sand.cubicTo(-60, -66, 40, -70, 112, -40); sand.close()
    path_draw(c, sand, 0xFFF2CF7A, 4)
    c.restore()

def bush(c, x, y=GROUND_Y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for (bx, by, r) in ((-70, -60, 60), (0, -110, 80), (70, -60, 60), (-30, -50, 60), (40, -40, 55)):
        circle(c, bx, by, r, 0xFF3FAE4A, 5)
    for (bx, by, r) in ((-70, -60, 56), (0, -110, 76), (70, -60, 56), (-30, -50, 56), (40, -40, 51)):
        c.drawCircle(bx, by, r, fill(0xFF3FAE4A))
    for i in range(7):
        circle(c, -80 + i * 27, -70 - (i % 3) * 30, 8, 0xFFFF7AB6, 3)
    c.restore()

def water(c, level, t, color=0xFF4FB3FF, a=0.88, amp=8.0, front=False):
    """Flood water surface at y=level."""
    p = skia.Path()
    p.moveTo(-700, H + 600)
    for i in range(-700, W + 741, 40):
        p.lineTo(i, level + math.sin(i * 0.018 + t * 2.4) * amp + math.sin(i * 0.05 - t * 3.1) * amp * 0.4)
    p.lineTo(W + 740, H + 600)
    p.close()
    c.drawPath(p, fill(alpha(color, a)))
    hl = skia.Path()
    for i in range(-700, W + 741, 40):
        yy = level + math.sin(i * 0.018 + t * 2.4) * amp + math.sin(i * 0.05 - t * 3.1) * amp * 0.4
        (hl.moveTo if i == -700 else hl.lineTo)(i, yy)
    c.drawPath(hl, stroke(alpha(0xFFFFFFFF, 0.8), 5))
    for i in range(10):
        sx = (hsh(i, 5) * W + t * 30 * (hsh(i, 6) - 0.5)) % W
        sy = level + 30 + hsh(i, 7) * (H - level)
        c.drawLine(sx - 20, sy, sx + 20, sy, stroke(alpha(0xFFFFFFFF, 0.35), 4))

def puddle(c, x, y, rx, ry=None, t=0.0):
    ry = ry or rx * 0.28
    oval(c, x, y, rx, ry, 0xFF5BBDFF, 4, 0xFF3A8FD0)
    oval(c, x - rx * 0.25, y - ry * 0.2, rx * 0.35, ry * 0.25, 0x99FFFFFF, 0)

def rain(c, t, amount=1.0, n=140):
    if amount <= 0:
        return
    k = int(n * amount)
    p = stroke(alpha(0xFFFFFFFF, 0.75), 3.5)
    for i in range(k):
        sp = 700 + hsh(i, 2) * 300
        x = (hsh(i, 1) * (W + 200) - 100 + t * 60) % (W + 100)
        y = (hsh(i, 3) * H + t * sp) % (H + 60) - 30
        c.drawLine(x, y, x - 8, y + 26, p)

def lilypad(c, x, y, s=1.0, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s * 0.45)
    p = skia.Path()
    p.moveTo(0, 0)
    p.arcTo(skia.Rect.MakeLTRB(-60, -60, 60, 60), -60, 320, False)
    p.close()
    path_draw(c, p, 0xFF3FB34F, 6)
    c.drawLine(0, 0, -40, 20, stroke(0xFF2E8A3C, 5))
    c.drawLine(0, 0, 30, 36, stroke(0xFF2E8A3C, 5))
    c.restore()

def leaf(c, x, y, s=1.0, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path()
    p.moveTo(-80, 0)
    p.cubicTo(-40, -36, 50, -34, 86, 0)
    p.cubicTo(50, 26, -40, 24, -80, 0)
    p.close()
    path_draw(c, p, 0xFF7ED957)
    c.drawLine(-76, 0, 80, 0, stroke(0xFF4FA845, 4))
    for k in range(-2, 3):
        c.drawLine(k * 28, 0, k * 28 + 16, -14, stroke(0xFF4FA845, 3))
        c.drawLine(k * 28, 0, k * 28 + 16, 12, stroke(0xFF4FA845, 3))
    c.drawLine(80, 0, 100, -10, stroke(0xFF4FA845, 6))
    c.restore()

def swirl(c, x, y, t, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s * 0.4); c.rotate(t * 140)
    cols = [0xFF7FE0FF, 0xFFB28CFF, 0xFFFF9BD5, 0xFF7FE0FF, 0xFFFFFFFF]
    for k in range(5):
        p = skia.Path()
        for i in range(60):
            a = i * 0.12 + k * math.tau / 5
            r = 8 + i * 1.8
            (p.moveTo if i == 0 else p.lineTo)(math.cos(a) * r, math.sin(a) * r)
        c.drawPath(p, stroke(alpha(cols[k], 0.9), 9))
    c.restore()
    for i in range(6):
        a = t * 2 + i
        circle(c, x + math.cos(a) * 90 * s, y + math.sin(a) * 30 * s - 10, 6 + 3 * hsh(i), 0xAAFFFFFF, 2, 0x88FFFFFF)

def rainbow(c, x, y, r, prog=1.0, a=0.9):
    cols = [0xFFE8343B, 0xFFFF9A1F, 0xFFFFD93B, 0xFF6CCB5F, 0xFF3D8BFF, 0xFF8E5CF7]
    for i, col in enumerate(cols):
        rr = r - i * 22
        p = stroke(alpha(col, a), 24, skia.Paint.kButt_Cap)
        c.drawArc(skia.Rect.MakeLTRB(x - rr, y - rr, x + rr, y + rr), 180, 180 * clamp(prog), False, p)

def splash_fx(c, x, y, t0, t, size=1.0, color=0xFF8ED8FF):
    """Droplets flying out from a splash that started at t0."""
    dt = t - t0
    if dt < 0 or dt > 1.1:
        return
    for i in range(16):
        ang = math.pi + (i / 15) * math.pi
        sp = (220 + hsh(i, 3) * 260) * size
        dx = math.cos(ang) * sp * dt
        dy = math.sin(ang) * sp * dt * 1.4 + 520 * dt * dt
        r = (9 + hsh(i, 4) * 9) * size * (1 - dt / 1.1)
        circle(c, x + dx, y + dy, r, color, 3, 0xFF3A8FD0)
    ring = ease_out(dt / 0.8)
    if dt < 0.8:
        oval(c, x, y, 40 * size + 160 * size * ring, (12 + 40 * ring) * size, 0, 0)
        c.drawOval(skia.Rect.MakeLTRB(x - (40 + 160 * ring) * size, y - (12 + 40 * ring) * size,
                                      x + (40 + 160 * ring) * size, y + (12 + 40 * ring) * size),
                   stroke(alpha(0xFFFFFFFF, 1 - ring), 6))

def sparkles(c, x, y, t, n=8, rad=80, color=0xFFFFF07A, seed=0):
    for i in range(n):
        ph = (t * 1.3 + hsh(i, seed)) % 1.0
        a = hsh(i, seed + 1) * math.tau + t * 0.6
        r = rad * (0.4 + 0.6 * hsh(i, seed + 2))
        sz = 10 * math.sin(ph * math.pi)
        if sz > 0.5:
            path_draw(c, star_path(x + math.cos(a) * r, y + math.sin(a) * r, sz, sz * 0.4, 4, 0), color, 2, 0xFFE0A800)

def speed_lines(c, x, y, dirx=-1, n=6, length=120, a=0.8):
    for i in range(n):
        yy = y - 60 + i * 24
        L = length * (0.6 + 0.4 * hsh(i))
        c.drawLine(x, yy, x + dirx * L, yy, stroke(alpha(0xFFFFFFFF, a), 5))

def pop_text(c, s, x, y, size, t, t0, color=0xFFFFFFFF, oc=INK, dur=None, rot=0.0):
    if t < t0 or (dur is not None and t > t0 + dur):
        return
    sc = back_out((t - t0) / 0.35)
    fade = 1.0
    if dur is not None:
        fade = 1 - ramp(t, t0 + dur - 0.25, t0 + dur)
    if fade <= 0:
        return
    c.saveLayerAlpha(None, int(255 * fade))
    text(c, s, x, y, size, color, oc=oc, scale=sc, rot=rot)
    c.restore()

def burst(c, x, y, r, t, color=0xFFFFD93B):
    p = star_path(x, y, r, r * 0.72, 14, t * 0.4)
    path_draw(c, p, color, 6)

def vignette_focus(c, x, y, r, a=0.6):
    """Darken everything except a circle (spotlight) for hide-and-seek moments."""
    p = skia.Path()
    p.addRect(skia.Rect.MakeWH(W, H))
    p.addCircle(x, y, r)
    p.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(p, fill(alpha(0xFF101830, a)))


# ---------- icons for interactive moments ----------
def icon_bubble(c, x, y, r, t, kind, active=1.0):
    sc = back_out(active)
    if sc <= 0.01:
        return
    c.save(); c.translate(x, y); c.scale(sc, sc)
    circle(c, 0, 0, r, 0xFFFFFFFF, 6)
    if kind == "look":
        oval(c, 0, 0, r * 0.62, r * 0.38, 0xFFFFFFFF, 5)
        circle(c, 0, 0, r * 0.26, 0xFF3D8BFF, 4)
        circle(c, 0, 0, r * 0.12, INK, 0)
    elif kind == "brave":
        path_draw(c, star_path(0, 0, r * 0.7, r * 0.3), 0xFFFFC21A, 5)
    elif kind == "help":
        hp = skia.Path()
        hp.moveTo(0, r * 0.5)
        hp.cubicTo(-r * 0.9, -r * 0.1, -r * 0.4, -r * 0.75, 0, -r * 0.3)
        hp.cubicTo(r * 0.4, -r * 0.75, r * 0.9, -r * 0.1, 0, r * 0.5)
        path_draw(c, hp, 0xFFE8343B, 5)
    elif kind == "point":
        hp = skia.Path()
        hp.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-r * 0.35, -r * 0.1, r * 0.35, r * 0.55), 12, 12))
        c.drawPath(hp, fill(0xFFFFD9A8)); c.drawPath(hp, stroke())
        fp = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-r * 0.12, -r * 0.62, r * 0.12, 0), 10, 10)
        c.drawRRect(fp, fill(0xFFFFD9A8)); c.drawRRect(fp, stroke())
    c.restore()


# ---------- transitions: cover(amount 0..1) ----------
def cover(c, kind, a, t):
    a = clamp(a)
    if a <= 0:
        return
    if kind == "splash":
        col = 0xFF4FB3FF
        p = skia.Path()
        R = ease(a) * 900
        for i in range(48):
            ang = i * math.tau / 48
            rr = R * (1 + 0.12 * math.sin(i * 2.7 + t * 6))
            (p.moveTo if i == 0 else p.lineTo)(W / 2 + math.cos(ang) * rr, H / 2 + math.sin(ang) * rr)
        p.close()
        c.drawPath(p, fill(col))
        for i in range(10):
            bx = hsh(i, 1) * W
            by = H / 2 + math.sin(i) * 200
            circle(c, bx, by, 30 * a + 40 * hsh(i, 2) * a, 0xFF8ED8FF, 0)
    elif kind == "drop":
        r = (1 - ease(a)) * 820
        p = skia.Path()
        p.addRect(skia.Rect.MakeWH(W, H))
        p.addCircle(W / 2, H / 2, max(r, 0.1))
        p.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(p, fill(0xFF2F6FD6))
        if r > 2:
            c.drawCircle(W / 2, H / 2, r, stroke(0xFF8ED8FF, 14))
    elif kind == "hero":
        x = lerp(-300, W + 500, ease(a))
        p = skia.Path()
        p.moveTo(-200, 0); p.lineTo(x, 0)
        p.cubicTo(x - 80, H * 0.3, x + 60, H * 0.6, x - 160, H)
        p.lineTo(-200, H); p.close()
        c.drawPath(p, fill(0xFF3D8BFF))
        c.drawPath(p, stroke(0xFF2F6FD6, 18))
        for i in range(7):
            yy = H * (i + 0.5) / 7
            xx = x - 40 - 60 * math.sin(yy / H * math.pi) + 30 * math.sin(i)
            path_draw(c, star_path(xx, yy, 26, 11, 5, t * 3 + i), 0xFFFFD93B, 4)
    elif kind == "boots":
        x = lerp(-100, W + 200, ease(a))
        c.drawRect(skia.Rect.MakeLTRB(0, 0, max(x - 60, 0), H), fill(0xFFFFD93B))
        for i in range(6):
            bx = x - 60 - i * 40 - (i % 2) * 20
            by = 90 + i * 110 + (i % 2) * 30
            for k in range(0, 3):
                fy = by + k * 0
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(bx - 26 + 80, by - 40, bx + 26 + 80, by + 40), 22, 22)
            c.drawRRect(rr, fill(0xFFE8343B)); c.drawRRect(rr, stroke(INK, 5))
    elif kind == "bubble":
        for i in range(36):
            bx = (i % 9) * 160 + (i // 9 % 2) * 80
            by = (i // 9) * 200 + 60 - ease(a) * 120
            r = ease(clamp(a * 1.6 - hsh(i) * 0.6)) * 170
            if r > 1:
                circle(c, bx, by, r, 0xFF9FE3FF, 5, 0xFF63BDEB)
                circle(c, bx - r * 0.35, by - r * 0.35, r * 0.15, 0xCCFFFFFF, 0)
    elif kind == "spin":
        c.save(); c.translate(W / 2, H / 2); c.rotate(a * 540)
        s = ease(a) * 16
        lilypad(c, 0, 0, s, 0)
        c.restore()
        if a > 0.85:
            c.drawPaint(fill(alpha(0xFF3FB34F, (a - 0.85) / 0.15)))
    elif kind == "rainbow":
        cols = [0xFFE8343B, 0xFFFF9A1F, 0xFFFFD93B, 0xFF6CCB5F, 0xFF3D8BFF, 0xFF8E5CF7]
        for i, col in enumerate(cols):
            x = lerp(-W, 0, ease(clamp(a * 1.4 - i * 0.07)))
            c.drawRect(skia.Rect.MakeLTRB(0, i * H / 6, x + W, (i + 1) * H / 6), fill(col))
    elif kind == "fade":
        c.drawPaint(fill(alpha(0xFFFFFFFF, a)))
    elif kind == "black":
        c.drawPaint(fill(alpha(0xFF000000, a)))
