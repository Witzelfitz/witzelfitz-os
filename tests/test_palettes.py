"""Palette contrast, custom zone persistence and bounded hardware writes."""
import configparser
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

DATA = Path(__file__).resolve().parents[1] / "system_files/usr/share/witzelfitz-desktop"
sys.path.insert(0, str(DATA))
from palettes import keyboard_packets, load_palettes, palette_for_scene, readable_ink, rgb, scheme_text
from appearance import Appearance
from library import SceneLibrary, validate_scene


def luminance(color):
    values = [channel / 255 for channel in rgb(color)]
    values = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(values, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    values = sorted((luminance(first), luminance(second)))
    return (values[1] + 0.05) / (values[0] + 0.05)


class CoordinatedPalettes(unittest.TestCase):
    def test_all_presets_keep_text_links_and_selections_readable(self):
        self.assertEqual(len(load_palettes()), 14)
        for profile in load_palettes():
            with self.subTest(palette=profile["id"]):
                self.assertGreaterEqual(contrast("#edf0f9", profile["alternate"]), 4.5)
                self.assertGreaterEqual(contrast(profile["accent"], profile["surface"]), 4.5)
                config = configparser.ConfigParser(); config.read_string(scheme_text(profile))
                selection = "#" + "".join(f"{int(channel):02x}" for channel in config["Colors:Selection"]["BackgroundNormal"].split(","))
                self.assertGreaterEqual(contrast("#f5f6fc", selection), 4.5)
                self.assertFalse(any(key.startswith("name[") for key in config["General"]))
                for zone in profile["keyboard"]:
                    self.assertGreaterEqual(contrast(readable_ink(zone), zone), 4.5)

    def test_acer_packets_use_correct_zone_masks_and_brightness(self):
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffffff"]
        self.assertEqual(keyboard_packets(colors, 100), [bytes((1, 255, 0, 0)), bytes((2, 0, 255, 0)), bytes((4, 0, 0, 255)), bytes((8, 255, 255, 255))])
        self.assertEqual(keyboard_packets(colors, 0), [bytes((zone, 0, 0, 0)) for zone in (1, 2, 4, 8)])
        for brightness in (-1, 101, True, "65"):
            with self.assertRaises(ValueError): keyboard_packets(colors, brightness)
        with self.assertRaises(ValueError): keyboard_packets(["#ff0000"] * 3)

    def test_appearance_is_written_once_until_palette_or_brightness_changes(self):
        scene = {"id": "tsunade", "palette": "jade", "accent": "#80d8bb"}
        settings = {"syncKeyboard": True, "syncColors": True, "keyboardBrightness": 65}
        with tempfile.TemporaryDirectory() as directory:
            device = Path(directory) / "keyboard"; device.touch()
            appearance = Appearance(DATA, Path(directory), device)
            with patch("appearance.shutil.which", return_value="/usr/bin/plasma-apply-colorscheme"), patch("appearance.subprocess.run") as apply_colors:
                first = appearance.apply(scene, settings)
                self.assertTrue(first["keyboardApplied"]); self.assertTrue(first["colorsApplied"])
                self.assertEqual(device.read_bytes(), b"".join(keyboard_packets(palette_for_scene(scene)["keyboard"], 65)))
                device.write_bytes(b"unchanged")
                appearance.apply(scene, settings)
                self.assertEqual(device.read_bytes(), b"unchanged")
                apply_colors.assert_called_once()
                appearance.apply(scene, dict(settings, keyboardBrightness=30))
                self.assertEqual(device.read_bytes(), b"".join(keyboard_packets(palette_for_scene(scene)["keyboard"], 30)))

    def test_disabled_keyboard_sync_does_not_touch_existing_color(self):
        with tempfile.TemporaryDirectory() as directory:
            device = Path(directory) / "keyboard"; device.write_bytes(b"existing")
            appearance = Appearance(DATA, Path(directory), device)
            state = appearance.apply({"accent": "#eaa0c7", "palette": "sakura"},
                {"syncKeyboard": False, "syncColors": False, "keyboardBrightness": 65})
            self.assertFalse(state["keyboardApplied"]); self.assertFalse(state["colorsApplied"])
            self.assertEqual(device.read_bytes(), b"existing")

    def test_custom_zones_survive_catalog_save_and_palette_defaults_stay_linked(self):
        with tempfile.TemporaryDirectory() as directory:
            library = SceneLibrary(DATA, Path(directory) / "config", Path(directory) / "share")
            current = next(scene for scene in library.catalog() if scene["id"] == "ocean")
            library.save(current)
            raw = json.loads(library.registry.read_text())["scenes"][0]
            self.assertNotIn("keyboard", raw)  # Unedited colors follow future palette updates.
            zones = ["#111111", "#222222", "#333333", "#444444"]
            library.save(dict(current, keyboard=zones, keyboardCustom=True))
            updated = next(scene for scene in library.catalog() if scene["id"] == "ocean")
            self.assertEqual(updated["keyboard"], zones)
            self.assertTrue(updated["keyboardCustom"])
            with self.assertRaises(ValueError): validate_scene(dict(current, keyboard=["unsafe"] * 4, keyboardCustom=True))


if __name__ == "__main__":
    unittest.main()
