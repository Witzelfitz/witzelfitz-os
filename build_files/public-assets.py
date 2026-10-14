#!/usr/bin/env python3
"""Generate original abstract backgrounds without private files or dependencies."""
import argparse
import json
import math
from pathlib import Path
import struct
import zlib

WIDTH, HEIGHT = 1280, 720
SCENES = [
    dict(id="aurora", name="Aurora", character="Aurora", series="WITZEL OS",
         file="aurora.png", accent="#b3a2ef", effect="fireflies", palette="moonlit"),
    dict(id="ocean", name="Ocean", character="Ocean", series="WITZEL OS",
         file="ocean.png", accent="#80d8bb", effect="ocean", palette="jade"),
    dict(id="ember", name="Ember", character="Ember", series="WITZEL OS",
         file="ember.png", accent="#f1b879", effect="none", palette="sunset"),
]


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def artwork(accent):
    color = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))
    pixels = bytearray()
    for y in range(HEIGHT):
        pixels.append(0)
        py = y / HEIGHT
        for x in range(WIDTH):
            px = x / WIDTH
            distance = math.hypot((px - .78) * 1.4, py - .45)
            glow = math.exp(-distance * distance * 5)
            ribbon = math.exp(-((py - .55 - .12 * math.sin(px * 7)) / .055) ** 2)
            strength = (.16 * glow + .19 * ribbon * px ** 2)
            pixels.extend(min(255, int(base + c * strength)) for base, c in zip((7, 11, 22), color))
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(pixels, 9)) + chunk(b'IEND', b'')


def assets(root):
    data = root / "usr/share/witzelfitz-desktop"
    result = {data / "scenes.json": (json.dumps(SCENES, ensure_ascii=False, indent=2) + "\n").encode()}
    for scene in SCENES:
        result[data / "wallpapers" / scene["file"]] = artwork(scene["accent"])
    result[root / "usr/share/plymouth/themes/witzelfitz/background.png"] = result[data / "wallpapers/aurora.png"]
    return result


def generate(root, check=False):
    expected = assets(root)
    folder = root / "usr/share/witzelfitz-desktop/wallpapers"
    allowed = {scene["file"] for scene in SCENES}
    extras = {p.name for p in folder.iterdir()} - allowed if folder.exists() else set()
    if extras:
        raise ValueError("Private/unexpected assets in public wallpaper folder: " + ", ".join(sorted(extras)))
    for path, content in expected.items():
        if check:
            if not path.is_file() or path.is_symlink() or path.read_bytes() != content:
                raise ValueError(f"Public asset differs from generated original: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print("Public scene catalog and four original backgrounds verified." if check else "Public backgrounds generated.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(args.root, args.check)


if __name__ == "__main__":
    main()
