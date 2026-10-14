#!/usr/bin/env python3
"""Install a wallpaper pack into the user profile; never copy it into an OS build."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "system_files/usr/share/witzelfitz-desktop"))
from library import atomic_json, validate_scene


def install(source, destination):
    scenes = [validate_scene(s) for s in json.loads((source / "scenes.json").read_text())]
    if not scenes or len({s["id"] for s in scenes}) != len(scenes):
        raise ValueError("Pack must contain unique scene IDs.")
    files = []
    for scene in scenes:
        path = source / "wallpapers" / scene["file"]
        if not path.is_file() or path.resolve().parent != (source / "wallpapers").resolve():
            raise ValueError(f"Invalid or missing private image: {path}")
        target = destination / "wallpapers" / scene["file"]
        if target.exists() and target.read_bytes() != path.read_bytes():
            raise ValueError(f"Existing private image differs; back it up first: {target}")
        files.append((path, target))
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    (destination / "wallpapers").mkdir(mode=0o700, exist_ok=True)
    for path, target in files:
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
    existing = []
    if (destination / "scenes.json").exists():
        existing = json.loads((destination / "scenes.json").read_text())
    values = {s["id"]: s for s in existing}
    values.update({s["id"]: s for s in scenes})
    atomic_json(destination / "scenes.json", list(values.values()))
    print(f"{len(scenes)} private scenes installed in {destination}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory containing scenes.json and wallpapers/")
    args = parser.parse_args()
    share = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    install(args.source.resolve(), share / "witzelfitz-desktop-private")


if __name__ == "__main__":
    main()
