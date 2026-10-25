"""Biscuit & Friends characters and garden props, built on the shared Puddle Patrol drawing kit."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pip"))
from draw import *  # noqa: F401,F403
import skia

GOLD, GOLD_D, CREAM = 0xFFF2B45A, 0xFFC98A3A, 0xFFFFE6B8
GREY, GREY_D, WHITE = 0xFFA3ABB7, 0xFF7D8694, 0xFFFFFFFF
BROWN, BROWN_D, TAN = 0xFF7A5232, 0xFF5A3A22, 0xFFEBC79B
RED = 0xFFE8343B


# ---------------------------------------------------------------- Biscuit
def draw_biscuit(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, ears=0.0, wag=1.0,
                 squash=0.0, tilt=0.0, blink=None, sad=0.0, sit=0.0, mud=0.0, mud_parts=("body", "ears", "paws")):
    """Golden puppy. mud: 0 clean .. 1 covered in mud spots (mud_parts picks which spots show). ears: -1 droopy (sad) .. 1 perky. wag: tail wag speed. (x, y) = feet."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s * face * (1 + squash * 0.15), s * (1 - squash * 0.15))
    # tail
    a = math.sin(t * 18 * wag) * 28 * min(wag, 1) - 20 + sad * 40
    c.save()
    c.translate(-44, -62 + sit * 12)
    c.rotate(-60 + a)
    tp = skia.Path()
    tp.moveTo(0, 0)
    tp.cubicTo(-8, -26, 6, -46, 14, -58)
    c.drawPath(tp, stroke(INK, 16))
    c.drawPath(tp, stroke(GOLD, 9))
    c.restore()
    # back legs
    for lx in (-30, 24):
        oval(c, lx, -14, 15, 15, GOLD_D, 4.5)
    # body
    oval(c, 0, -56 + sit * 10, 54, 42 - sit * 6, GOLD)
    oval(c, 10, -48 + sit * 10, 30, 22, CREAM, 0)
    # front legs + paws
    for lx in (-14, 22):
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(lx - 11, -40, lx + 11, -4), 10, 10)
        c.drawRRect(r, fill(GOLD)); c.drawRRect(r, stroke())
        oval(c, lx + 2, -4, 15, 8, CREAM, 4)
    # collar
    hy = -128 + sit * 12
    c.drawLine(-26, hy + 40, 30, hy + 40, stroke(INK, 14))
    c.drawLine(-26, hy + 40, 30, hy + 40, stroke(RED, 9))
    circle(c, 6, hy + 50, 7, 0xFFFFC21A, 3)
    # head
    circle(c, 0, hy, 46, GOLD)
    oval(c, 4, hy + 20, 28, 20, CREAM, 0)
    # floppy ears (in front of the head sides)
    droop = ears
    for sx in (-1, 1):
        c.save()
        c.translate(sx * 40, hy - 26)
        c.rotate(sx * (20 + 15 * min(droop, 0) - 25 * max(droop, 0)) + math.sin(t * 6) * 3)
        ep = skia.Path()
        ep.moveTo(-10, 0)
        ep.cubicTo(-22, 26, -12, 58 - droop * 14, 4, 58 - droop * 14)
        ep.cubicTo(18, 54 - droop * 14, 16, 20, 10, 0)
        ep.close()
        path_draw(c, ep, GOLD_D, 4.5)
        c.restore()
    bl = blink_amt(t, 0.5) if blink is None else blink
    eye(c, -16, hy - 8, 12, 15, look, bl)
    eye(c, 20, hy - 8, 12, 15, look, bl)
    if sad > 0:
        c.drawLine(-26, hy - 26 + 3 * sad, -8, hy - 30 - 2 * sad, stroke(INK, 4))
        c.drawLine(30, hy - 26 + 3 * sad, 12, hy - 30 - 2 * sad, stroke(INK, 4))
    oval(c, 4, hy + 10, 9, 7, INK, 0)
    circle(c, 1, hy + 8, 2.5, 0xAAFFFFFF, 0)
    m = clamp(mouth)
    if m > 0.08:
        oval(c, 4, hy + 26 + 4 * m, 13, 4 + 10 * m, 0xFF8A2B36, 4)
        oval(c, 4, hy + 32 + 6 * m, 8, 3 + 4 * m, 0xFFFF8FA3, 0)
    else:
        mp = skia.Path()
        if sad > 0.5:
            mp.moveTo(-8, hy + 30); mp.quadTo(4, hy + 22, 16, hy + 30)
        else:
            mp.moveTo(-10, hy + 22); mp.quadTo(-3, hy + 30, 4, hy + 22); mp.quadTo(11, hy + 30, 18, hy + 22)
        c.drawPath(mp, stroke(INK, 3.5))
    circle(c, -28, hy + 14, 7, 0x55FF7A9A, 0)
    circle(c, 34, hy + 14, 7, 0x55FF7A9A, 0)
    if mud > 0:
        spots = {"body": [(-24, -66, 15), (18, -76, 12), (-4, -40, 13), (34, -50, 10)],
                 "ears": [(-44, hy + 6, 11), (46, hy + 2, 10), (-8, hy - 32, 12)],
                 "paws": [(-12, -8, 11), (24, -8, 11)]}
        for part in mud_parts:
            for (mx, my, mr) in spots[part]:
                circle(c, mx, my, mr * mud, alpha(0xFF7A5232, 0.92), 0)
                circle(c, mx + mr * 0.6 * mud, my - mr * 0.4 * mud, mr * 0.45 * mud, alpha(0xFF7A5232, 0.92), 0)
    c.restore()


# ---------------------------------------------------------------- bath props
def mud_puddle(c, x, y, rx=150, t=0.0):
    oval(c, x, y, rx, rx * 0.26, 0xFF8B5A2B, 4, 0xFF5A3A1A)
    oval(c, x - rx * 0.3, y - rx * 0.05, rx * 0.25, rx * 0.06, 0x55FFFFFF, 0)
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        circle(c, x - rx * 0.5 + i * rx * 0.5, y - 2, 4 + 6 * ph, alpha(0xFF6B4423, 1 - ph), 0)


def tub_back(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    oval(c, 0, -110, 170, 34, 0xFFB8C4D0, 5)
    oval(c, 0, -110, 154, 26, 0xFF8FA0B2, 0)
    c.restore()


def tub_front(c, x, y, s=1.0, water=0.0, t=0.0, bubbles=0.0):
    """Front of a tin bath tub. water 0..1 fills it; bubbles 0..1 piles foam on top."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if water > 0:
        wy = -12 - 92 * water
        wp = skia.Path()
        wp.moveTo(-156, wy)
        for i in range(0, 313, 26):
            wp.lineTo(-156 + i, wy + math.sin(i * 0.05 + t * 3) * 4)
        wp.lineTo(156, -110); wp.lineTo(-156, -110); wp.close()
        c.drawOval(skia.Rect.MakeLTRB(-154, wy - 22, 154, wy + 22), fill(alpha(0xFF7FD3FF, 0.85)))
    body = skia.Path()
    body.moveTo(-170, -110); body.cubicTo(-168, -20, -140, 0, -120, 0); body.lineTo(120, 0); body.cubicTo(140, 0, 168, -20, 170, -110)
    body.cubicTo(120, -84, -120, -84, -170, -110); body.close()
    path_draw(c, body, 0xFFC9D3DD, 5)
    for k in (-1, 1):
        c.drawLine(k * 120, -70, k * 120, -20, stroke(0xFFA9B6C4, 6))
    for k in (-1, 1):
        oval(c, k * 182, -100, 18, 12, 0xFFC9D3DD, 4)
        for fx in (-1, 1):
            oval(c, k * 110 + fx * 18, 4, 14, 8, 0xFFA9B6C4, 3.5)
    if bubbles > 0:
        for i in range(16):
            bx = -150 + hsh(i, 2) * 300
            by = -112 - hsh(i, 3) * 40 * bubbles
            r = (14 + hsh(i, 4) * 16) * bubbles
            circle(c, bx, by, r, 0xEEFFFFFF, 3, 0xFFB8D8F0)
            circle(c, bx - r * 0.35, by - r * 0.35, r * 0.2, 0xFFFFFFFF, 0)
    c.restore()


def bubble(c, x, y, r, t=0.0, pop=0.0):
    """Floating soap bubble. pop 0..1 bursts it into a ring of droplets."""
    if pop <= 0:
        p = skia.Paint(AntiAlias=True, Color=0x44A8E6FF)
        c.drawCircle(x, y, r, p)
        c.drawCircle(x, y, r, stroke(0xCC8FD3FF, 3))
        c.drawArc(skia.Rect.MakeLTRB(x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7), 200, 70, False, stroke(0xEEFFFFFF, 3))
        c.drawCircle(x + r * 0.35, y + r * 0.3, r * 0.08, fill(0xCCFF9BD5))
    elif pop < 1:
        for k in range(8):
            a = k * math.tau / 8
            d = r * (1 + pop * 1.2)
            circle(c, x + math.cos(a) * d, y + math.sin(a) * d, 4 * (1 - pop), 0xCC8FD3FF, 0)


def towel(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    tp = skia.Path()
    tp.moveTo(-70, -130); tp.cubicTo(-90, -60, -80, -10, -60, 0); tp.lineTo(60, 0); tp.cubicTo(80, -10, 90, -60, 70, -130)
    tp.cubicTo(30, -110, -30, -110, -70, -130); tp.close()
    path_draw(c, tp, 0xFFFF9BD5)
    for k in range(3):
        c.drawLine(-64 + k * 4, -40 + k * 14, 64 - k * 4, -40 + k * 14, stroke(0xFFFFFFFF, 5))
    c.restore()


# ---------------------------------------------------------------- Mittens
def cat_eye(c, x, y, r, look=(0, 0), closed=0.0, lid=0.25):
    ry = r * 1.15 * (1 - 0.92 * closed)
    oval(c, x, y, r, max(ry, 1.5), WHITE, 3.5)
    if closed < 0.6:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - r, y - ry, x + r, y + ry))
        px, py = x + look[0] * r * 0.3, y + look[1] * r * 0.25
        oval(c, px, py, r * 0.62, r * 0.75, 0xFF6CCB5F, 0)
        oval(c, px, py, r * 0.2, r * 0.6, INK, 0)
        circle(c, px - r * 0.2, py - r * 0.3, r * 0.16, WHITE, 0)
        c.restore()
        if lid > 0:
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - r - 3, y - ry - 3, x + r + 3, y - ry + 2 * ry * lid))
            oval(c, x, y, r, ry, GREY, 3.5)
            c.restore()


def draw_mittens(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, blink=None, stretch=0.0, lid=0.25,
                 tail=1.0, paw_up=0.0):
    """Grey cat sitting. (x, y) = feet."""
    c.save()
    c.translate(x, y)
    c.scale(s * face * (1 + stretch * 0.2), s * (1 - stretch * 0.15))
    # tail
    sw = math.sin(t * 2.2) * 18 * tail
    tp = skia.Path()
    tp.moveTo(-30, -16)
    tp.cubicTo(-90, -10, -80 + sw, -80, -60 + sw, -110)
    c.drawPath(tp, stroke(INK, 18))
    c.drawPath(tp, stroke(GREY, 11))
    c.drawCircle(-60 + sw, -110, 6, fill(WHITE))
    # body
    bp = skia.Path()
    bp.moveTo(-40, 0)
    bp.cubicTo(-48, -60, -30, -96, 0, -96)
    bp.cubicTo(30, -96, 48, -60, 40, 0)
    bp.close()
    path_draw(c, bp, GREY)
    oval(c, 0, -46, 22, 34, WHITE, 0)
    # paws
    oval(c, -16, -6 - paw_up * 30, 13, 9, WHITE, 4)
    oval(c, 16, -6, 13, 9, WHITE, 4)
    # head
    hy = -128
    for sx in (-1, 1):
        ep = skia.Path()
        ep.moveTo(sx * 14, hy - 34)
        ep.lineTo(sx * 34, hy - 70)
        ep.lineTo(sx * 42, hy - 18)
        ep.close()
        path_draw(c, ep, GREY, 4.5)
        ip = skia.Path()
        ip.moveTo(sx * 22, hy - 36)
        ip.lineTo(sx * 33, hy - 58)
        ip.lineTo(sx * 37, hy - 28)
        ip.close()
        c.drawPath(ip, fill(0xFFFFA3C0))
    oval(c, 0, hy, 46, 40, GREY)
    oval(c, 0, hy + 16, 22, 14, WHITE, 0)
    bl = blink_amt(t, 1.4) if blink is None else blink
    cat_eye(c, -17, hy - 6, 11, look, bl, lid)
    cat_eye(c, 17, hy - 6, 11, look, bl, lid)
    np_ = skia.Path()
    np_.moveTo(-6, hy + 8); np_.lineTo(6, hy + 8); np_.lineTo(0, hy + 15); np_.close()
    path_draw(c, np_, 0xFFFF7AA2, 2.5)
    m = clamp(mouth)
    if m > 0.08:
        oval(c, 0, hy + 22 + 3 * m, 8, 3 + 7 * m, 0xFF8A2B36, 3.5)
    else:
        mp = skia.Path()
        mp.moveTo(-9, hy + 18); mp.quadTo(-4, hy + 24, 0, hy + 16); mp.quadTo(4, hy + 24, 9, hy + 18)
        c.drawPath(mp, stroke(INK, 3))
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            c.drawLine(sx * 22, hy + 14 + k * 5, sx * 52, hy + 10 + k * 9, stroke(INK, 2))
    c.restore()


# ---------------------------------------------------------------- Prickles
STUCK_POS = {"flower": (-24, -118), "duck": (-74, -62), "sock": (-60, -100), "ball": (-50, -26), "leaf": (-20, -118)}


def stuck_item(c, kind, x, y, sc=1.0, rot=0.0, t=0.0, sparkle=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    if kind == "ball":
        if sparkle > 0:
            circle(c, 0, 0, 26 + 4 * math.sin(t * 8), alpha(0xFFFFF3A0, 0.6 * sparkle), 0)
        circle(c, 0, 0, 18, RED, 4)
        c.drawArc(skia.Rect.MakeLTRB(-12, -12, 12, 12), 200, 60, False, stroke(0xCCFFFFFF, 4))
    elif kind == "flower":
        for k in range(5):
            a = k * math.tau / 5
            circle(c, math.cos(a) * 11, math.sin(a) * 11, 9, 0xFFFF7AB6, 3)
        circle(c, 0, 0, 7, 0xFFFFD93B, 3)
    elif kind == "duck":
        oval(c, 0, 4, 18, 13, 0xFFFFD93B, 3.5)
        circle(c, 10, -10, 10, 0xFFFFD93B, 3.5)
        tri = skia.Path(); tri.moveTo(18, -10); tri.lineTo(28, -7); tri.lineTo(18, -4); tri.close()
        path_draw(c, tri, 0xFFFF9A1F, 2.5)
        circle(c, 12, -13, 2.5, INK, 0)
    elif kind == "sock":
        sp = skia.Path()
        sp.moveTo(-8, -22); sp.lineTo(8, -22); sp.lineTo(8, 6); sp.cubicTo(8, 16, 24, 14, 24, 22)
        sp.lineTo(-4, 22); sp.cubicTo(-10, 22, -8, 10, -8, 6); sp.close()
        path_draw(c, sp, WHITE, 3.5)
        c.save(); c.clipPath(sp, doAntiAlias=True)
        for k in range(4):
            c.drawLine(-12, -18 + k * 10, 26, -18 + k * 10, stroke(0xFF3D8BFF, 4))
        c.restore()
        c.drawPath(sp, stroke(INK, 3.5))
    elif kind == "leaf":
        lp = skia.Path(); lp.moveTo(-18, 0); lp.cubicTo(-6, -14, 10, -14, 20, 0); lp.cubicTo(10, 12, -6, 12, -18, 0); lp.close()
        path_draw(c, lp, 0xFF7ED957, 3)
    c.restore()


def spike_path(rx, ry, cx, cy, n=26, depth=16, start=100, end=440):
    p = skia.Path()
    for i in range(n * 2 + 1):
        a = math.radians(start + (end - start) * i / (n * 2))
        r = 1.0 if i % 2 == 0 else 1.0 + depth / rx
        px, py = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    p.close()
    return p


def draw_prickles(c, x, y, s=1.0, t=0.0, mouth=0.0, look=(0, 0), face=1, items=(), blink=None,
                  roll=None, wiggle=0.0, tilt=0.0, squash=0.0, sparkle=0.0, item_off=None):
    """Round hedgehog. face=1 looks right (back spikes on the left). items = things stuck on his back.
    roll: None, or an angle to draw him curled up as a rolling spiky ball. item_off: {kind: (dx, dy, rot, scale)}."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt + math.sin(t * 20) * 8 * wiggle)
    c.scale(s * face * (1 + squash * 0.15), s * (1 - squash * 0.15))
    if roll is not None:
        c.save(); c.translate(0, -48); c.rotate(roll)
        sp = spike_path(44, 44, 0, 0, 22, 14, 0, 360)
        path_draw(c, sp, BROWN_D, 4)
        circle(c, 0, 0, 40, BROWN, 0)
        for k in range(6):
            a = k * math.tau / 6
            c.drawLine(math.cos(a) * 10, math.sin(a) * 10, math.cos(a) * 34, math.sin(a) * 34, stroke(BROWN_D, 4))
        for kind in items:
            px, py = STUCK_POS[kind]
            stuck_item(c, kind, px * 0.5 + 6, py * 0.5 + 28, 0.8, t=t, sparkle=sparkle)
        c.restore()
        c.restore()
        return
    # feet
    for fx in (-16, 22):
        oval(c, fx, -6, 14, 8, TAN, 4)
    # spiky back (left side when facing right)
    sp = spike_path(60, 52, -6, -58, 24, 18, 95, 300)
    path_draw(c, sp, BROWN_D, 4.5)
    oval(c, -4, -58, 58, 50, BROWN)
    for k in range(7):
        a = math.radians(110 + k * 26)
        c.drawLine(-6 + math.cos(a) * 20, -58 + math.sin(a) * 18, -6 + math.cos(a) * 50, -58 + math.sin(a) * 44, stroke(BROWN_D, 4))
    # face + belly (front)
    fp = skia.Path()
    fp.moveTo(8, -104)
    fp.cubicTo(60, -104, 76, -60, 70, -40)
    fp.cubicTo(62, -10, 20, -4, 6, -10)
    fp.cubicTo(18, -40, 12, -80, 8, -104)
    fp.close()
    path_draw(c, fp, TAN, 4.5)
    # snout
    sn = skia.Path()
    sn.moveTo(56, -78); sn.cubicTo(78, -76, 92, -66, 94, -60); sn.cubicTo(84, -54, 66, -54, 56, -58); sn.close()
    path_draw(c, sn, TAN, 4)
    circle(c, 94, -61, 7, INK, 0)
    # eyes + glasses
    bl = blink_amt(t, 2.6) if blink is None else blink
    eye(c, 36, -80, 9, 11, look, bl)
    eye(c, 60, -82, 8, 10, look, bl)
    c.drawCircle(36, -80, 15, stroke(INK, 4))
    c.drawCircle(61, -82, 13, stroke(INK, 4))
    c.drawLine(51, -82, 48, -82, stroke(INK, 4))
    c.drawLine(21, -82, 6, -88, stroke(INK, 3.5))
    # mouth
    m = clamp(mouth)
    if m > 0.08:
        oval(c, 70, -46 + 3 * m, 10, 3 + 8 * m, 0xFF8A2B36, 3.5)
    else:
        mp = skia.Path(); mp.moveTo(58, -48); mp.quadTo(70, -38, 82, -50)
        c.drawPath(mp, stroke(INK, 3.5))
    circle(c, 30, -58, 7, 0x66FF7A9A, 0)
    # arms
    oval(c, 40, -30, 9, 13, TAN, 3.5)
    # things stuck on his back
    item_off = item_off or {}
    for kind in items:
        px, py = STUCK_POS[kind]
        dx, dy, rot, sc = item_off.get(kind, (0, 0, 0, 1))
        stuck_item(c, kind, px + dx, py + dy, sc, rot, t, sparkle if kind == "ball" else 0)
    c.restore()


# ---------------------------------------------------------------- garden
def fence(c, y=GROUND_Y):
    for i in range(-6, 30):
        x = i * 60
        p = skia.Path()
        p.moveTo(x + 4, y); p.lineTo(x + 4, y - 120); p.lineTo(x + 28, y - 140); p.lineTo(x + 52, y - 120); p.lineTo(x + 52, y); p.close()
        path_draw(c, p, 0xFFE9C38A, 4, 0xFF9A6B3A)
    for yy in (y - 95, y - 40):
        c.drawRect(skia.Rect.MakeLTRB(-400, yy - 8, 1700, yy + 8), fill(0xFFD9AE6E))
        c.drawRect(skia.Rect.MakeLTRB(-400, yy - 8, 1700, yy + 8), stroke(0xFF9A6B3A, 3))


def tree(c, x, y=GROUND_Y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    tr = skia.Path()
    tr.moveTo(-30, 0); tr.cubicTo(-22, -100, -28, -200, -18, -260); tr.lineTo(18, -260); tr.cubicTo(24, -200, 20, -100, 32, 0); tr.close()
    path_draw(c, tr, 0xFF9A6338)
    c.drawLine(10, -200, 70, -250, stroke(INK, 18)); c.drawLine(10, -200, 70, -250, stroke(0xFF9A6338, 11))
    for (bx, by, r) in ((-80, -300, 80), (0, -360, 100), (90, -300, 80), (-40, -250, 70), (50, -250, 70)):
        circle(c, bx, by, r + 3, INK, 0)
    for (bx, by, r) in ((-80, -300, 80), (0, -360, 100), (90, -300, 80), (-40, -250, 70), (50, -250, 70)):
        circle(c, bx, by, r, 0xFF4FB84F, 0)
    for i in range(6):
        circle(c, -90 + i * 36, -320 + (i % 2) * 50, 7, 0xFFE8343B, 2.5)
    c.restore()


def nest(c, x, y, s=1.0, t=0.0, birds=3, sleepy=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    for i in range(birds):
        bx = -26 + i * 26
        circle(c, bx, -14, 14, [0xFF7FD3FF, 0xFFFFD93B, 0xFFFF9BD5][i % 3], 3.5)
        c.drawArc(skia.Rect.MakeLTRB(bx - 7, -20, bx - 1, -14), 0, 180, False, stroke(INK, 2.5))
        c.drawArc(skia.Rect.MakeLTRB(bx + 1, -20, bx + 7, -14), 0, 180, False, stroke(INK, 2.5))
        tri = skia.Path(); tri.moveTo(bx - 3, -10); tri.lineTo(bx + 3, -10); tri.lineTo(bx, -5); tri.close()
        path_draw(c, tri, 0xFFFF9A1F, 1.5)
    np_ = skia.Path()
    np_.moveTo(-50, -8); np_.cubicTo(-46, 22, 46, 22, 50, -8); np_.close()
    path_draw(c, np_, 0xFFB07A44, 4)
    for k in range(6):
        c.drawLine(-44 + k * 16, -4, -36 + k * 16, 12, stroke(0xFF7A4A1E, 3))
    c.restore()
    if sleepy:
        for i in range(3):
            ph = (t * 0.5 + i / 3) % 1
            text(c, "z", x + 40 + ph * 30, y - 40 - ph * 50, 18 + 10 * ph, alpha(0xFFFFFFFF, 1 - ph), tf=ROUND_TF, ow=3)


def toybox(c, x, y=GROUND_Y + 30, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-80, -90, 80, 0), 10, 10)
    c.drawRRect(r, fill(0xFFE8343B)); c.drawRRect(r, stroke())
    lid = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-88, -104, 88, -86), 8, 8)
    c.drawRRect(lid, fill(0xFFFFD93B)); c.drawRRect(lid, stroke())
    path_draw(c, star_path(0, -46, 22, 10), 0xFFFFD93B, 3.5)
    c.restore()


def bucket(c, x, y=GROUND_Y + 30, s=1.0, tip=0.0):
    c.save(); c.translate(x, y); c.rotate(tip * 100); c.scale(s, s)
    p = skia.Path(); p.moveTo(-44, -80); p.lineTo(44, -80); p.lineTo(34, 0); p.lineTo(-34, 0); p.close()
    path_draw(c, p, 0xFF3D8BFF)
    oval(c, 0, -80, 44, 10, 0xFF2F6FD6, 4)
    c.drawArc(skia.Rect.MakeLTRB(-40, -120, 40, -40), 180, 180, False, stroke(INK, 4))
    c.restore()


def flowerpot(c, x, y=GROUND_Y + 30, s=1.0, wobble=0.0):
    c.save(); c.translate(x, y); c.rotate(wobble); c.scale(s, s)
    for k, (dx, col) in enumerate(((-20, 0xFFFF7AB6), (0, 0xFFFFD93B), (22, 0xFF8E5CF7))):
        c.drawLine(dx * 0.5, -60, dx, -110 - k * 8, stroke(0xFF3FA65A, 5))
        for j in range(5):
            a = j * math.tau / 5
            circle(c, dx + math.cos(a) * 9, -110 - k * 8 + math.sin(a) * 9, 8, col, 2.5)
        circle(c, dx, -110 - k * 8, 6, 0xFFFFFFFF, 2.5)
    p = skia.Path(); p.moveTo(-40, -62); p.lineTo(40, -62); p.lineTo(30, 0); p.lineTo(-30, 0); p.close()
    path_draw(c, p, 0xFFE07A4A)
    c.drawRect(skia.Rect.MakeLTRB(-44, -70, 44, -56), fill(0xFFC9653A)); c.drawRect(skia.Rect.MakeLTRB(-44, -70, 44, -56), stroke())
    c.restore()


def tall_grass(c, x0, x1, y=GROUND_Y + 60, t=0.0, h=120):
    for i in range(int((x1 - x0) / 14)):
        gx = x0 + i * 14 + hsh(i, 3) * 6
        sw = math.sin(t * 2 + i * 0.7) * 8
        hh = h * (0.7 + 0.3 * hsh(i, 4))
        p = skia.Path()
        p.moveTo(gx - 7, y); p.quadTo(gx + sw * 0.5, y - hh * 0.6, gx + sw, y - hh); p.quadTo(gx + 4, y - hh * 0.5, gx + 7, y); p.close()
        path_draw(c, p, [0xFF4FB84F, 0xFF6CCB5F, 0xFF3FA65A][i % 3], 3, 0xFF2E7D3A)


def garden(c, t, props=("box", "bucket", "pot", "tree"), bucket_tip=0.0, pot_wobble=0.0, grass=False):
    sky(c, 0.0)
    sun(c, 1120, 100, t, 1.0)
    clouds(c, t, 0.0, 3, 110)
    hills(c, 0.0)
    fence(c, 520)
    ground(c, 0.0, 520)
    if "tree" in props:
        tree(c, 1110, 560, 1.0)
    if "box" in props:
        toybox(c, 250, 600)
    if "bucket" in props:
        bucket(c, 560, 600, 1.0, bucket_tip)
    if "pot" in props:
        flowerpot(c, 800, 600, 1.0, pot_wobble)
    if grass:
        tall_grass(c, 820, 1060, 640, t)
