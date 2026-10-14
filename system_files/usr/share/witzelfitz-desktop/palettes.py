"""Coordinated dark desktop palettes and four-zone Acer keyboard colors."""
import configparser
import io
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")
IDENTIFIER = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")


def rgb(color):
    if not isinstance(color, str) or not HEX.fullmatch(color):
        raise ValueError("Ungültige RGB-Farbe.")
    return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))


def hex_color(values):
    return "#" + "".join(f"{max(0, min(255, round(value))):02x}" for value in values)


def mix(first, second, amount):
    return hex_color(a * (1 - amount) + b * amount for a, b in zip(rgb(first), rgb(second)))


def readable_ink(color):
    def luminance(value):
        channels = [channel / 255 for channel in rgb(value)]
        channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(channels, (0.2126, 0.7152, 0.0722)))
    background = luminance(color)
    def contrast(ink):
        values = sorted((background, luminance(ink)))
        return (values[1] + 0.05) / (values[0] + 0.05)
    preferred = max(("#101524", "#f5f6fc"), key=contrast)
    return preferred if contrast(preferred) >= 4.5 else max(("#000000", "#ffffff"), key=contrast)


def load_palettes(data=None):
    path = Path(data or ROOT) / "palettes.json"
    if not path.is_file() and data is not None:
        path = ROOT / "palettes.json"
    values = json.loads(path.read_text())
    seen = set()
    for value in values:
        ident = value.get("id")
        if not isinstance(ident, str) or not IDENTIFIER.fullmatch(ident) or ident in seen:
            raise ValueError("Ungültige oder doppelte Paletten-ID.")
        seen.add(ident)
        if not isinstance(value.get("name"), str) or not value["name"].strip():
            raise ValueError("Palettenname fehlt.")
        for key in ("accent", "surface", "alternate"):
            rgb(value.get(key))
        keyboard_colors(value.get("keyboard"))
        value["scheme"] = "Witzelfitz-" + ident
    return values


def keyboard_colors(value):
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("Vier Tastaturfarben werden benötigt.")
    for color in value:
        rgb(color)
    return value


def palette_for_scene(scene, data=None):
    presets = {value["id"]: value for value in load_palettes(data)}
    profile = presets.get(scene.get("palette"))
    if profile and profile["accent"].lower() == scene["accent"].lower():
        profile = dict(profile)
    else:
        accent = scene["accent"]
        profile = {"id": "", "name": "Individuell", "accent": accent,
                   "surface": "#141c2e", "alternate": "#1b2439", "scheme": "Witzelfitz-Custom",
                   "keyboard": [mix(accent, "#101524", 0.38), mix(accent, "#101524", 0.15),
                                accent, mix(accent, "#dae5ff", 0.2)]}
    if scene.get("keyboard"):
        profile["keyboard"] = keyboard_colors(scene["keyboard"])
    return profile


def keyboard_packets(colors, brightness=65):
    keyboard_colors(colors)
    if type(brightness) is not int or not 0 <= brightness <= 100:
        raise ValueError("Helligkeit muss zwischen 0 und 100 liegen.")
    return [bytes((1 << zone, *(round(channel * brightness / 100) for channel in rgb(color))))
            for zone, color in enumerate(colors)]


def scheme_text(profile, template=None):
    source = Path(template or ROOT / "WitzelfitzNight.colors").read_text()
    header = source.split("[", 1)[0]
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(source)
    triplet = lambda color: ",".join(map(str, rgb(color)))
    for section in config.sections():
        if not section.startswith("Colors:"):
            continue
        config[section]["BackgroundNormal"] = triplet(profile["surface"])
        config[section]["BackgroundAlternate"] = triplet(profile["alternate"])
        for key in ("DecorationFocus", "DecorationHover", "ForegroundActive", "ForegroundLink"):
            config[section][key] = triplet(profile["accent"])
        if section == "Colors:Selection":
            config[section]["BackgroundNormal"] = triplet(mix(profile["accent"], profile["surface"], 0.55))
            config[section]["ForegroundNormal"] = "245,246,252"
    for key in list(config["General"]):
        if key.startswith("Name["):
            del config["General"][key]
    config["General"]["Name"] = "Witzelfitz · " + profile["name"]
    config["General"]["ColorScheme"] = profile["scheme"]
    config["WM"]["activeBackground"] = triplet(profile["alternate"])
    config["WM"]["inactiveBackground"] = triplet(profile["surface"])
    output = io.StringIO(); config.write(output, space_around_delimiters=False)
    return header + output.getvalue()
