"""A failed preflight must never mutate policy or replace a queued deployment."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SignedUpdates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "tools").mkdir()
        self.script = self.root / "tools/use-signed-updates.sh"
        shutil.copy2(ROOT / "tools/use-signed-updates.sh", self.script)
        for relative in ("cosign.pub", "system_files/etc/pki/containers/witzelfitz-os.pub",
                         "system_files/etc/containers/registries.d/witzelfitz-os.yaml"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.log = self.root / "commands.log"
        self.status = self.root / "status.json"
        self.status.write_text(json.dumps({"deployments": [{"booted": True, "staged": False}]}))
        metadata = self.root / "metadata.json"
        metadata.write_text(json.dumps({"Digest": "sha256:" + "a" * 64, "Labels": {
            "org.opencontainers.image.source": "https://github.com/Witzelfitz/witzelfitz-os"}}))
        policy = self.root / "policy.json"
        policy.write_text('{"default":[{"type":"reject"}],"transports":{"docker":{}}}')
        bins = self.root / "bin"
        bins.mkdir()
        scripts = {
            "id": "echo 0",
            "rpm-ostree": 'cat "$TEST_STATUS"',
            "skopeo": 'cat "$TEST_METADATA"',
            "cosign": 'echo signature >> "$TEST_LOG"; exit "${TEST_SIGNATURE_EXIT:-0}"',
            "jq": '''args=()
for arg in "$@"; do
    if [ "$arg" = /etc/containers/policy.json ]; then arg=$TEST_POLICY; fi
    args+=("$arg")
done
exec "$TEST_JQ" "${args[@]}"''',
            "install": 'echo install >> "$TEST_LOG"',
            "ostree": 'printf "ostree %s\\n" "$*" >> "$TEST_LOG"',
            "bootc": 'printf "bootc %s\\n" "$*" >> "$TEST_LOG"',
        }
        for name, source in scripts.items():
            path = bins / name
            path.write_text("#!/bin/bash\n" + source + "\n")
            path.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bins) + ":" + os.environ["PATH"],
                        TEST_STATUS=str(self.status), TEST_METADATA=str(metadata),
                        TEST_POLICY=str(policy), TEST_JQ=shutil.which("jq"), TEST_LOG=str(self.log))

    def run_script(self, *args):
        return subprocess.run(["bash", str(self.script), *args], env=self.env,
                              capture_output=True, text=True)

    def test_invalid_signature_never_installs_policy_or_switches(self):
        self.env["TEST_SIGNATURE_EXIT"] = "1"
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.log.read_text(), "signature\n")

    def test_pending_deployment_is_not_overwritten(self):
        self.status.write_text(json.dumps({"deployments": [{"booted": True}, {"staged": True}]}))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wartet bereits", result.stderr)
        self.assertFalse(self.log.exists())

    def test_verified_switch_pins_current_system_and_restores_latest(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.log.read_text().splitlines()
        self.assertEqual(lines[0], "signature")
        self.assertEqual(lines[-2:], ["ostree admin pin 0",
            "bootc switch --enforce-container-sigpolicy ghcr.io/witzelfitz/witzelfitz-os:latest"])
        self.assertFalse(any("reboot" in line for line in lines))

    def test_foreign_registry_rejected_before_any_command(self):
        self.assertNotEqual(self.run_script("ghcr.io/another/os:latest").returncode, 0)
        self.assertFalse(self.log.exists())
