#!/usr/bin/env python3
"""Erzeugt die Grafiken der Bootanimation (Plymouth-Theme «witzelfitz»).

Ausgabe nach output/plymouth-preview/; öffentliche Build-Dateien bleiben erhalten.
Mit --preview DATEI entsteht zusätzlich eine animierte WebP-Vorschau,
die den Ablauf aus witzelfitz.script nachstellt.

    python3 tools/make-plymouth-theme.py [--scene aurora] [--preview /tmp/boot.webp]
"""

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "system_files/usr/share/witzelfitz-desktop"
THEME = ROOT / "system_files/usr/share/plymouth/themes/witzelfitz"
FONT = "/usr/share/fonts/adwaita-sans-fonts/AdwaitaSans-Regular.ttf"
W, H = 1920, 1080

# Diese Werte müssen zu witzelfitz.script passen.
TITLE_X, TITLE_Y = 0.075, 0.40
DOTS_GAP = 26
RAIN_COUNT = 36


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([32, weight])  # optische Grösse, Gewicht
    return f


def background(scene):
    img = Image.open(DESKTOP / "wallpapers" / scene["file"]).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    # Links abdunkeln, damit der Schriftzug lesbar bleibt
    shade = Image.new("L", (W, H))
    px = shade.load()
    for x in range(W):
        a = int(170 * max(0.0, 1 - x / (W * 0.62)) ** 1.6)
        for y in range(H):
            px[x, y] = a
    img = Image.composite(Image.new("RGB", (W, H), (6, 5, 14)), img, shade)
    # Leichte Vignette oben und unten
    vig = Image.new("L", (W, H))
    d = ImageDraw.Draw(vig)
    for i in range(140):
        a = int(110 * (1 - i / 140) ** 2)
        d.line([(0, i), (W, i)], fill=a)
        d.line([(0, H - 1 - i), (W, H - 1 - i)], fill=a)
    return Image.composite(Image.new("RGB", (W, H), (4, 3, 10)), img, vig)


def title(accent):
    big = font(132, 600)
    small = font(132, 300)
    parts = [("Witzel", big, (244, 241, 255)), (" OS", small, accent)]
    widths = [p[1].getlength(p[0]) for p in parts]
    pad = 60
    img = Image.new("RGBA", (int(sum(widths)) + 2 * pad, 132 + 2 * pad))
    d = ImageDraw.Draw(img)
    x = pad
    for (text, f, color), w in zip(parts, widths):
        d.text((x, pad - 10), text, font=f, fill=color + (255,))
        x += w
    glow = Image.new("RGBA", img.size, accent + (0,))
    glow.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(22)))
    return img, glow


def dot(accent):
    img = Image.new("RGBA", (40, 40))
    ImageDraw.Draw(img).ellipse((13, 13, 27, 27), fill=accent + (255,))
    halo = img.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(halo, img)


def drop():
    img = Image.new("RGBA", (12, 70))
    d = ImageDraw.Draw(img)
    for i in range(60):
        a = int(200 * math.sin(math.pi * i / 60))
        d.point((7 - i * 0.08, 5 + i), fill=(205, 200, 255, a))
    return img


def preview(path, bg, ttl, glw, dt, drp):
    """Stellt den Ablauf aus witzelfitz.script als WebP nach (halbe Grösse)."""
    rnd = random.Random(7)
    rain = [[rnd.random() * W, rnd.random() * H, 900 + rnd.random() * 700,
             0.15 + rnd.random() * 0.35] for _ in range(RAIN_COUNT)]
    tx, ty = int(W * TITLE_X) - 60, int(H * TITLE_Y) - 60
    frames = []
    for n in range(80):
        t = n / 20
        f = bg.convert("RGBA")
        for r in rain:
            y = (r[1] + r[2] * t) % (H + 80) - 80
            x = r[0] - (y - r[1]) * 0.08
            layer = drp.copy()
            layer.putalpha(layer.getchannel("A").point(lambda a, o=r[3]: int(a * o)))
            f.alpha_composite(layer, (int(x) % W, int(y)))
        reveal = min(1.0, t / 1.1)
        ease = 1 - (1 - reveal) ** 3
        oy = int(24 * (1 - ease))
        g = glw.copy()
        go = (0.35 + 0.25 * math.sin(t * 2.4)) * ease
        g.putalpha(g.getchannel("A").point(lambda a, o=go: int(a * o)))
        f.alpha_composite(g, (tx, ty + oy))
        tt = ttl.copy()
        tt.putalpha(tt.getchannel("A").point(lambda a, o=ease: int(a * o)))
        f.alpha_composite(tt, (tx, ty + oy))
        for i in range(3):
            o = (0.25 + 0.75 * max(0.0, math.sin(t * 4 - i * 0.9))) * ease
            dd = dt.copy()
            dd.putalpha(dd.getchannel("A").point(lambda a, o=o: int(a * o)))
            f.alpha_composite(dd, (int(W * TITLE_X) - 14 + i * DOTS_GAP,
                                   ty + ttl.height - 30))
        frames.append(f.convert("RGB").resize((W // 2, H // 2), Image.LANCZOS))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=50, loop=0)


def main():
    global DESKTOP, THEME
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="aurora")
    ap.add_argument("--data-dir", type=Path, default=DESKTOP)
    ap.add_argument("--output-dir", type=Path, default=ROOT / "output/plymouth-preview")
    ap.add_argument("--preview")
    args = ap.parse_args()

    DESKTOP, THEME = args.data_dir, args.output_dir
    scenes = json.loads((DESKTOP / "scenes.json").read_text())
    scene = next(s for s in scenes if s["id"] == args.scene)
    accent = hex_rgb(scene["accent"])

    THEME.mkdir(parents=True, exist_ok=True)
    bg = background(scene)
    ttl, glw = title(accent)
    dt, drp = dot(accent), drop()
    bg.save(THEME / "background.png", optimize=True)
    ttl.save(THEME / "title.png", optimize=True)
    glw.save(THEME / "glow.png", optimize=True)
    dt.save(THEME / "dot.png", optimize=True)
    drp.save(THEME / "drop.png", optimize=True)
    if args.preview:
        preview(args.preview, bg, ttl, glw, dt, drp)


if __name__ == "__main__":
    main()
