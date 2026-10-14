"""Activation must preserve rollback and reject corrupt or pending deployments."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Activation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "tools").mkdir()
        self.script = self.root / "tools/activate-local-image.sh"
        shutil.copy2(ROOT / "tools/activate-local-image.sh", self.script)
        self.layout = self.root / "output/witzelfitz-public-oci"
        self.layout.mkdir(parents=True)
        (self.layout / "index.json").write_text("{}")
        (self.root / "output/witzelfitz-public-oci.sha256").write_text(
            hashlib.sha256(b"{}").hexdigest() + "  index.json\n")
        self.log = self.root / "commands.log"
        self.status = self.root / "status.json"
        self.status.write_text(json.dumps({"deployments": [{"booted": True, "staged": False}]}))
        bins = self.root / "bin"; bins.mkdir()
        scripts = {
            "id": "#!/bin/sh\necho 0\n",
            "rpm-ostree": '#!/bin/sh\ncat "$TEST_STATUS"\n',
            "ostree": '#!/bin/sh\nprintf "ostree %s\\n" "$*" >> "$TEST_LOG"\n',
            "bootc": '#!/bin/sh\nprintf "bootc %s\\n" "$*" >> "$TEST_LOG"\n',
        }
        for name, code in scripts.items():
            p = bins / name; p.write_text(code); p.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bins) + ":" + os.environ["PATH"],
                        TEST_LOG=str(self.log), TEST_STATUS=str(self.status))

    def run_script(self):
        return subprocess.run(["bash", str(self.script)], env=self.env, capture_output=True, text=True)

    def test_activation_pins_running_system_and_stages_without_reboot(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), [
            "ostree admin pin 0", f"bootc switch --transport oci --retain {self.layout}"])

    def test_pending_deployment_is_not_replaced(self):
        self.status.write_text(json.dumps({"deployments": [{"booted": True}, {"staged": True}]}))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wartet bereits", result.stderr)
        self.assertFalse(self.log.exists())

    def test_corrupted_export_never_reaches_system_mutations(self):
        (self.layout / "index.json").write_text("changed")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
