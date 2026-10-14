"""Regression coverage for profile safety, action isolation and scene assets."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "system_files/usr/bin/witzelfitz-desktop"
loader = importlib.machinery.SourceFileLoader("desktop", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
desktop = importlib.util.module_from_spec(spec)
loader.exec_module(desktop)


class DesktopSafety(unittest.TestCase):
    def test_settings_reject_unknown_themes_and_non_boolean_motion(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "desktop.json"
            file.write_text('{"theme":"../../foreign", "motion":"false", "pauseOnBattery":false}')
            with patch.object(desktop, "SETTINGS", file):
                state = desktop.read_settings()
            self.assertEqual(state["theme"], "aurora")
            self.assertIs(state["motion"], True)
            self.assertIs(state["pauseOnBattery"], False)

    def test_bad_or_non_object_settings_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "desktop.json"
            with patch.object(desktop, "SETTINGS", file):
                for contents in ('{broken', '[]', 'null'):
                    file.write_text(contents)
                    self.assertEqual(desktop.read_settings(), desktop.DEFAULTS)

    def test_custom_scene_ids_are_accepted_and_hidden_selection_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "desktop.json"
            file.write_text('{"theme":"user-example", "motion":false}')
            with patch.object(desktop, "SETTINGS", file), patch.object(desktop, "scenes", return_value=[{"id": "konan"}, {"id": "user-example"}]):
                self.assertEqual(desktop.read_settings()["theme"], "user-example")
            with patch.object(desktop, "SETTINGS", file), patch.object(desktop, "scenes", return_value=[{"id": "nami"}]):
                self.assertEqual(desktop.read_settings()["theme"], "nami")

    def test_keyboard_settings_reject_wrong_types_and_out_of_range_brightness(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "desktop.json"
            with patch.object(desktop, "SETTINGS", file):
                for brightness in (-1, 101, True, "65"):
                    file.write_text(json.dumps({"keyboardBrightness": brightness, "syncKeyboard": "false", "syncColors": False}))
                    state = desktop.read_settings()
                    self.assertEqual(state["keyboardBrightness"], 65)
                    self.assertTrue(state["syncKeyboard"])
                    self.assertFalse(state["syncColors"])

    def test_launch_never_interprets_shell_characters(self):
        with patch.object(desktop.shutil, "which", return_value="/usr/bin/xdg-open"), patch.object(desktop.subprocess, "Popen") as popen:
            desktop.launch(["xdg-open", "/tmp/a $(touch unsafe);b"])
            self.assertEqual(popen.call_args.args[0], ["xdg-open", "/tmp/a $(touch unsafe);b"])
            self.assertNotIn("shell", popen.call_args.kwargs)

    def test_atomic_write_preserves_existing_config_on_serialization_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "desktop.json"
            desktop.atomic_json(path, {"theme": "machi"})
            with self.assertRaises(TypeError):
                desktop.atomic_json(path, {"bad": object()})
            self.assertEqual(json.loads(path.read_text()), {"theme": "machi"})
            self.assertEqual(list(Path(directory).glob(".desktop-*")), [])

    def test_image_package_has_all_scenes_and_qml_dependencies(self):
        desktop.validate()
        expected = {"aurora", "ocean", "ember"}
        with tempfile.TemporaryDirectory() as directory, patch.object(desktop, "USER_SHARE", Path(directory)):
            actual = desktop.scenes()
        self.assertEqual({scene["id"] for scene in actual}, expected)
        self.assertEqual(len(actual), len(expected), "Scene IDs must be unique")
        for source in (desktop.DATA / "qml").glob("*.qml"):
            self.assertTrue(source.read_text().strip())


if __name__ == "__main__":
    unittest.main()
