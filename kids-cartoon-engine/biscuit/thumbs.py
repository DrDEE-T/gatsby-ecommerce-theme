"""YouTube thumbnails: big faces, the key object, 2-3 bold words."""
import sys, os, skia
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUT)
from chars import *

def thumb(path, draw_fn):
    surf = skia.Surface(1280, 720)
    c = surf.getCanvas()
    draw_fn(c)
    surf.makeImageSnapshot().save(path, skia.kPNG)

def ep1(c):
    hero_rays_bg(c, 0xFF6CC8FF, 0xFF8ED8FF)
    draw_biscuit(c, 300, 800, 2.6, 0.0, ears=0.8, look=(1, -0.2), mouth=0.7)
    draw_prickles(c, 900, 700, 2.5, 0.0, face=-1, items=("ball", "duck", "sock", "flower"), look=(-1, 0), sparkle=1.0, mouth=0.6)
    text(c, "WHERE'S THE BALL?", 640, 90, 104, 0xFFFFD93B, ow=16)

def ep2(c):
    hero_rays_bg(c, 0xFF8FD6FF, 0xFFA8E0FF)
    tub_back(c, 640, 860, 2.2)
    draw_biscuit(c, 640, 690, 2.4, 0.0, ears=0.8, mouth=0.8, mud=1.0, mud_parts=("ears",))
    tub_front(c, 640, 860, 2.2, water=0.7, t=0.0, bubbles=1.0)
    for (x, y, r) in ((180, 300, 50), (1100, 260, 60), (1000, 470, 36), (260, 520, 40)):
        bubble(c, x, y, r)
    text(c, "BUBBLE BATH TIME!", 640, 90, 104, 0xFFFFD93B, ow=16)

def ep3(c):
    hero_rays_bg(c, 0xFF26336E, 0xFF2F3E80)
    night_sky(c, 0.0, 1.0)
    dog_bed(c, 470, 820, 2.0)
    draw_biscuit(c, 470, 790, 2.3, 0.0, blink=1.0, ears=-0.3, wag=0.1, sit=1)
    draw_prickles(c, 1000, 760, 2.3, 0.0, face=-1, look=(-1, -0.3), mouth=0.6)
    text(c, "SLEEPY TIME!", 640, 90, 110, 0xFFFFD93B, ow=16)

def comp1(c):
    hero_rays_bg(c, 0xFF6CC8FF, 0xFF8ED8FF)
    draw_mittens(c, 260, 760, 2.0, 0.0, mouth=0.5)
    draw_biscuit(c, 640, 780, 2.4, 0.0, ears=0.8, mouth=0.8, wag=1.4)
    draw_prickles(c, 1050, 760, 2.1, 0.0, face=-1, items=("ball",), mouth=0.6)
    text(c, "3 FUN STORIES!", 640, 90, 110, 0xFFFFD93B, ow=16)

def hero_rays_bg(c, c1, c2):
    import math
    c.drawPaint(fill(c1))
    c.save(); c.translate(640, 400)
    for i in range(16):
        if i % 2 == 0:
            p = skia.Path(); a = i * math.tau / 16
            p.moveTo(0, 0); p.lineTo(math.cos(a) * 1600, math.sin(a) * 1600); p.lineTo(math.cos(a + 0.2) * 1600, math.sin(a + 0.2) * 1600); p.close()
            c.drawPath(p, fill(c2))
    c.restore()

thumb(os.path.join(OUT, "thumb-ep1.png"), ep1)
thumb(os.path.join(OUT, "thumb-ep2.png"), ep2)
thumb(os.path.join(OUT, "thumb-ep3.png"), ep3)
thumb(os.path.join(OUT, "thumb-comp1.png"), comp1)
