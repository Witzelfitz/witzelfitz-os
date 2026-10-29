"""Desktop startup regressions, with no GPU access or changes to host Bluetooth."""
import configparser
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / "system_files"


class NvidiaAutostart(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.log = self.home / "loader.log"
        mock = self.home / "nvidia-settings"
        mock.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$TEST_LOG"\nexit "${TEST_EXIT:-0}"\n')
        mock.chmod(0o755)
        self.mock = mock
        self.env = dict(os.environ, HOME=str(self.home), TEST_LOG=str(self.log))

    def run_loader(self, gpu="/dev/null"):
        # Replace only external device/program paths; keep the production control
        # flow and home-directory handling. Never invoke the real GPU driver.
        source = (FILES / "usr/libexec/witzelfitz-nvidia-settings-load").read_text()
        source = source.replace("/dev/nvidia0", gpu).replace("/usr/bin/nvidia-settings", shlex.quote(str(self.mock)))
        return subprocess.run(["sh", "-c", source], env=self.env, capture_output=True, text=True)

    def test_no_saved_settings_succeeds_without_invoking_driver(self):
        result = self.run_loader()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.log.exists())

    def test_saved_settings_are_loaded(self):
        (self.home / ".nvidia-settings-rc").write_text("# saved settings\n")
        result = self.run_loader()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text(), "--load-config-only\n")

    def test_missing_gpu_does_not_invoke_driver(self):
        (self.home / ".nvidia-settings-rc").touch()
        result = self.run_loader(str(self.home / "missing-device"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.log.exists())

    def test_loader_errors_are_not_hidden(self):
        (self.home / ".nvidia-settings-rc").touch()
        self.env["TEST_EXIT"] = "7"
        self.assertEqual(self.run_loader().returncode, 7)

    def test_desktop_uses_the_packaged_helper(self):
        entry = configparser.ConfigParser(interpolation=None)
        entry.read(FILES / "etc/xdg/autostart/nvidia-settings-load.desktop")
        self.assertEqual(entry["Desktop Entry"]["Exec"], "/usr/libexec/witzelfitz-nvidia-settings-load")
        self.assertEqual(entry["Desktop Entry"]["TryExec"], entry["Desktop Entry"]["Exec"])


class BluetoothHardwareScope(unittest.TestCase):
    def test_only_the_verified_laptop_passes_the_service_conditions(self):
        unit = (FILES / "usr/lib/systemd/system/bluetooth-enable-ertm.service").read_text()
        commands = [shlex.split(line.split("=", 1)[1]) for line in unit.splitlines()
                    if line.startswith("ExecCondition=")]
        self.assertEqual(len(commands), 2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for vendor, model, expected in [
                ("Acer", "Predator PT515-51", True),
                ("Acer", "Different laptop", False),
                ("Other vendor", "Predator PT515-51", False),
            ]:
                with self.subTest(vendor=vendor, model=model):
                    (root / "sys_vendor").write_text(vendor + "\n")
                    (root / "product_name").write_text(model + "\n")
                    matched = all(subprocess.run(
                        command[:-1] + [str(root / Path(command[-1]).name)],
                        capture_output=True).returncode == 0 for command in commands)
                    self.assertEqual(matched, expected)
