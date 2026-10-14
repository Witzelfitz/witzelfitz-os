"""Custom scenes, update persistence, import isolation and metadata validation."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("scenes_manager", str(ROOT / "system_files/usr/bin/witzelfitz-scenes"))
spec = importlib.util.spec_from_loader(loader.name, loader)
manager = importlib.util.module_from_spec(spec)
loader.exec_module(manager)
from library import SceneLibrary, atomic_json
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication


class SceneCatalog(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = self.root / "data"
        (self.data / "wallpapers").mkdir(parents=True)
        self.base = {"id": "konan", "name": "Paper Rain", "character": "Konan",
                     "series": "NARUTO", "file": "konan.png", "accent": "#b3a2ef", "effect": "rain"}
        self.write_bundled()
        self.image = QImage(160, 90, QImage.Format_RGB32); self.image.fill(0xff665599)
        self.image.save(str(self.data / "wallpapers/konan.png"))
        self.library = SceneLibrary(self.data, self.root / "config", self.root / "share")

    def write_bundled(self):
        (self.data / "scenes.json").write_text(json.dumps([self.base]))

    def test_import_makes_private_copy_and_remove_preserves_original(self):
        original = self.root / "A name with spaces.png"; self.image.save(str(original))
        ident = manager.import_image(self.library, original)
        scene = next(value for value in self.library.catalog() if value["id"] == ident)
        self.assertTrue(scene["custom"])
        self.assertEqual(scene["effect"], "none")
        copy = self.library.wallpapers / scene["file"]
        self.assertEqual(original.read_bytes(), copy.read_bytes())
        self.library.reset_or_remove(ident)
        self.assertFalse(copy.exists())
        self.assertTrue(original.exists())

    def test_local_overrides_survive_bundled_metadata_update_and_reset(self):
        self.library.save(dict(self.base, name="Mein Konan", accent="#112233"))
        self.base["name"] = "New OS default"; self.write_bundled()
        scene = self.library.catalog()[0]
        self.assertEqual((scene["name"], scene["accent"]), ("Mein Konan", "#112233"))
        self.library.reset_or_remove("konan")
        self.assertEqual(self.library.catalog()[0]["name"], "New OS default")

    def test_last_visible_scene_cannot_be_hidden(self):
        with self.assertRaisesRegex(ValueError, "sichtbar"):
            self.library.save(self.base, hidden=True)
        self.assertEqual(len(self.library.catalog()), 1)

    def test_private_pack_survives_os_update_and_keeps_personal_overrides(self):
        folder = self.library.private / "wallpapers"
        folder.mkdir(parents=True)
        self.image.save(str(folder / "private.png"))
        scene = dict(self.base, id="private", file="private.png", name="Private default")
        atomic_json(self.library.private / "scenes.json", [scene])
        current = next(s for s in self.library.catalog() if s["id"] == "private")
        self.assertFalse(current["custom"])
        self.library.save(dict(current, name="Personal name"))
        self.base["name"] = "OS update"; self.write_bundled()
        current = next(s for s in self.library.catalog() if s["id"] == "private")
        self.assertEqual(current["name"], "Personal name")
        self.library.reset_or_remove("private")
        self.assertEqual(next(s for s in self.library.catalog() if s["id"] == "private")["name"], "Private default")
        self.assertTrue((folder / "private.png").is_file())

    def test_private_pack_cannot_replace_public_ids_or_escape_image_folder(self):
        folder = self.library.private / "wallpapers"
        folder.mkdir(parents=True)
        original = self.root / "outside.png"; self.image.save(str(original))
        (folder / "private.png").symlink_to(original)
        atomic_json(self.library.private / "scenes.json", [
            dict(self.base, name="Override public"),
            dict(self.base, id="private", file="private.png"),
            dict(self.base, id="escape", file="../outside.png"),
            dict(self.base, id="user-imposter", file="user-imposter.png"),
        ])
        self.assertEqual([s["id"] for s in self.library.catalog()], ["konan"])
        self.assertEqual(self.library.catalog()[0]["name"], self.base["name"])
        for value in ({}, None, [None, 42, "bad"]):
            atomic_json(self.library.private / "scenes.json", value)
            self.assertEqual([s["id"] for s in self.library.catalog()], ["konan"])

    def test_traversal_metadata_and_external_symlinks_are_rejected(self):
        original = self.root / "outside.png"; self.image.save(str(original))
        malformed = dict(self.base, id="user-escape", file="../outside.png")
        atomic_json(self.library.registry, {"scenes": [malformed], "hidden": []})
        self.assertEqual([scene["id"] for scene in self.library.catalog()], ["konan"])
        self.library.wallpapers.mkdir(parents=True)
        (self.library.wallpapers / "user-link.png").symlink_to(original)
        atomic_json(self.library.registry, {"scenes": [dict(self.base, id="user-link", file="user-link.png")], "hidden": []})
        self.assertEqual([scene["id"] for scene in self.library.catalog()], ["konan"])
        with self.assertRaises(ValueError): self.library.save(malformed)

    def test_invalid_color_effect_and_non_image_import_do_not_write_registry(self):
        for value in (dict(self.base, accent="red;command"), dict(self.base, effect="unknown")):
            with self.assertRaises(ValueError): self.library.save(value)
        original = self.root / "fake.png"; original.write_text("not an image")
        with self.assertRaises(ValueError): manager.import_image(self.library, original)
        self.assertFalse(self.library.registry.exists())

    def test_native_editor_import_save_and_activate_use_same_scene(self):
        app = QApplication.instance() or QApplication([])
        state = {"theme": "konan", "motion": True, "pauseOnBattery": True}
        original = self.root / "My wallpaper.png"; self.image.save(str(original))
        with patch.object(manager, "session_action") as action, patch.object(manager, "snapshot", return_value=dict(state)):
            window = manager.SceneManager(self.library, dict(state))
            ident = window.import_file(original)
            self.assertEqual(window.current["id"], ident)
            window.name.setText("Mein Onsen")
            window.effect.setCurrentIndex(window.effect.findData("steam"))
            window.set_color("#112233")
            self.assertTrue(window.save_scene())
            saved = next(scene for scene in self.library.catalog() if scene["id"] == ident)
            self.assertEqual((saved["name"], saved["effect"], saved["accent"]), ("Mein Onsen", "steam", "#112233"))
            self.assertFalse(window.dirty())
            window.activate_scene()
            action.assert_called_with("theme", ident)
            window.close()

    def test_native_palette_and_zone_editor_persist_the_previewed_colors(self):
        app = QApplication.instance() or QApplication([])
        state = {"theme": "konan", "motion": True, "pauseOnBattery": True}
        with patch.object(manager, "session_action") as action, patch.object(manager, "snapshot", return_value=dict(state)):
            window = manager.SceneManager(self.library, dict(state))
            window.palette.setCurrentIndex(window.palette.findData("jade"))
            self.assertEqual(window.color, "#80d8bb")
            with patch.object(manager.QColorDialog, "getColor", return_value=manager.QColor("#112233")):
                window.pick_zone(0)
            self.assertTrue(window.save_scene())
            saved = self.library.catalog()[0]
            self.assertEqual(saved["palette"], "jade")
            self.assertEqual(saved["keyboard"], ["#112233", "#48a68d", "#80d8bb", "#6bb5a7"])
            self.assertTrue(saved["keyboardCustom"])
            self.assertFalse(window.dirty())
            window.brightness.setValue(30); window.save_brightness()
            action.assert_called_with("keyboardBrightness", "30")
            window.close()


if __name__ == "__main__":
    unittest.main()
