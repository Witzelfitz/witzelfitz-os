"""Scene catalog shared by the desktop service and the native scene manager."""
import json
import os
from pathlib import Path
import re
import tempfile
from palettes import IDENTIFIER as PALETTE_IDENTIFIER, keyboard_colors, palette_for_scene

EFFECTS = {"none": "Still", "rain": "Regen & Papier", "ocean": "Meerreflexionen",
           "threads": "Nen-Fäden", "petals": "Rosenblätter", "fireflies": "Pyreflies",
           "steam": "Onsen-Dampf"}
IDENTIFIER = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".desktop-", text=True)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def validate_scene(value):
    if not isinstance(value, dict):
        raise ValueError("Ungültige Szene.")
    result = {}
    for key in ("id", "name", "character", "series", "file", "accent", "effect"):
        item = value.get(key)
        if not isinstance(item, str) or not item.strip() or len(item) > 160:
            raise ValueError(f"Ungültiges Szenenfeld: {key}")
        result[key] = item.strip()
    if not IDENTIFIER.fullmatch(result["id"]):
        raise ValueError("Ungültige Szenen-ID.")
    if Path(result["file"]).name != result["file"] or not result["file"].endswith(".png"):
        raise ValueError("Ungültiger Bilddateiname.")
    if not COLOR.fullmatch(result["accent"]) or result["effect"] not in EFFECTS:
        raise ValueError("Ungültige Farbe oder Animation.")
    palette = value.get("palette", "")
    if not isinstance(palette, str) or (palette and not PALETTE_IDENTIFIER.fullmatch(palette)):
        raise ValueError("Ungültige Palette.")
    if palette:
        result["palette"] = palette
    if "keyboard" in value and value.get("keyboardCustom", True):
        result["keyboard"] = list(keyboard_colors(value["keyboard"]))
    return result


class SceneLibrary:
    def __init__(self, data, config, share):
        self.data = Path(data)
        self.registry = Path(config) / "witzelfitz/scenes.json"
        self.wallpapers = Path(share) / "witzelfitz-desktop-custom/wallpapers"
        self.private = Path(share) / "witzelfitz-desktop-private"

    def bundled(self):
        return [validate_scene(value) for value in json.loads((self.data / "scenes.json").read_text())]

    def defaults(self):
        """Private packs live outside the OS and cannot replace public scene IDs."""
        values = {scene["id"]: (scene, self.data / "wallpapers") for scene in self.bundled()}
        try:
            private = json.loads((self.private / "scenes.json").read_text())
            if not isinstance(private, list):
                return values
        except (OSError, ValueError):
            return values
        for raw in private:
            try:
                scene = validate_scene(raw)
                if scene["id"] not in values and not scene["id"].startswith("user-"):
                    values[scene["id"]] = (scene, self.private / "wallpapers")
            except ValueError:
                continue
        return values

    def preferences(self):
        try:
            value = json.loads(self.registry.read_text())
            if isinstance(value, dict) and isinstance(value.get("scenes"), list) and isinstance(value.get("hidden"), list):
                return value
        except (OSError, ValueError):
            pass
        return {"version": 1, "scenes": [], "hidden": []}

    def catalog(self, include_hidden=False):
        defaults = self.defaults()
        bundled = {key: scene for key, (scene, folder) in defaults.items()}
        values = {key: dict(scene) for key, scene in bundled.items()}
        prefs = self.preferences()
        for raw in prefs["scenes"]:
            try:
                scene = validate_scene(raw)
                ident = scene["id"]
                if ident in bundled:
                    scene["file"] = bundled[ident]["file"]
                elif not ident.startswith("user-") or scene["file"] != ident + ".png":
                    continue
                values[ident] = scene
            except ValueError:
                continue
        result = []
        for ident, scene in values.items():
            custom = ident not in bundled
            folder = self.wallpapers if custom else defaults[ident][1]
            path = folder / scene["file"]
            # Metadata never permits escaping the managed wallpaper directory, even via symlinks.
            if path.resolve().parent != folder.resolve() or not path.is_file():
                continue
            hidden = ident in prefs["hidden"]
            if hidden and not include_hidden:
                continue
            profile = palette_for_scene(scene, self.data)
            result.append(dict(scene, custom=custom, hidden=hidden, image=path.as_uri(),
                surface=profile["surface"], alternate=profile["alternate"],
                keyboard=profile["keyboard"], keyboardCustom=bool(scene.get("keyboard")),
                paletteName=profile["name"], scheme=profile["scheme"]))
        return result

    def save(self, value, hidden=False):
        scene = validate_scene(value)
        bundled = {key: scene for key, (scene, folder) in self.defaults().items()}
        ident = scene["id"]
        if ident in bundled:
            scene["file"] = bundled[ident]["file"]
        elif not ident.startswith("user-") or scene["file"] != ident + ".png":
            raise ValueError("Eigene Szenen benötigen eine eigene Bilddatei.")
        prefs = self.preferences()
        hidden_ids = [item for item in prefs["hidden"] if isinstance(item, str) and item != ident]
        if hidden:
            if not any(item["id"] != ident for item in self.catalog()):
                raise ValueError("Mindestens eine Szene muss sichtbar bleiben.")
            hidden_ids.append(ident)
        overrides = [item for item in prefs["scenes"] if isinstance(item, dict) and item.get("id") != ident]
        atomic_json(self.registry, {"version": 1, "scenes": overrides + [scene], "hidden": hidden_ids})

    def reset_or_remove(self, ident):
        current = next((item for item in self.catalog(True) if item["id"] == ident), None)
        if current is None:
            raise ValueError("Szene nicht gefunden.")
        if current["custom"] and not any(item["id"] != ident for item in self.catalog()):
            raise ValueError("Mindestens eine Szene muss sichtbar bleiben.")
        prefs = self.preferences()
        atomic_json(self.registry, {"version": 1,
            "scenes": [item for item in prefs["scenes"] if isinstance(item, dict) and item.get("id") != ident],
            "hidden": [item for item in prefs["hidden"] if isinstance(item, str) and item != ident]})
        if current["custom"]:
            (self.wallpapers / current["file"]).unlink(missing_ok=True)
