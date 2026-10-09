"""Run user setup with a temporary home and stubbed network/installer commands."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'system_files/usr/bin/witzelfitz-setup'


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.bin = self.home / 'bin'
        self.bin.mkdir()
        self.env = {**os.environ, 'HOME': str(self.home), 'PATH': f'{self.bin}:/usr/bin:/bin',
                    'TMPDIR': str(self.home)}
        self.command('id', 'echo 1000')
        self.command('curl', 'echo unexpected network request >&2; exit 99')

    def command(self, name, body, directory=None):
        p = (directory or self.bin) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('#!/bin/bash\n' + body + '\n')
        p.chmod(0o755)

    def run_setup(self):
        return subprocess.run(['bash', str(SCRIPT)], env=self.env, capture_output=True, text=True)

    def test_rejects_root_before_changes(self):
        self.command('id', 'echo 0')
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ohne sudo', result.stderr)
        self.assertFalse((self.home / '.bashrc').exists())

    def test_local_install_detected_and_second_run_is_idempotent(self):
        self.command('claude', 'echo test-version', self.home / '.local/bin')
        for _ in range(2):
            result = self.run_setup()
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / '.bashrc').read_text().count('# >>> witzelfitz-os >>>'), 1)
        self.assertTrue((self.home / '.config/tmux/tmux.conf').exists())

    def test_existing_tmux_config_is_preserved(self):
        self.command('claude', 'echo test-version')
        config = self.home / '.config/tmux/tmux.conf'
        config.parent.mkdir(parents=True)
        config.write_text('# my configuration\n')
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual(config.read_text(), '# my configuration\n')

    def test_partial_download_never_executes(self):
        self.command('curl', '''while [ "$1" != "-o" ]; do shift; done
printf 'touch "$HOME/installer-executed"\\n' > "$2"
exit 18''')
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / 'installer-executed').exists())
        self.assertFalse((self.home / '.bashrc').exists())
        self.assertEqual(list(self.home.glob('tmp.*')), [])

    def test_complete_download_executes(self):
        self.command('curl', '''while [ "$1" != "-o" ]; do shift; done
printf 'touch "$HOME/installer-executed"\\n' > "$2"''')
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / 'installer-executed').exists())
        self.assertEqual(list(self.home.glob('tmp.*')), [])


if __name__ == '__main__':
    unittest.main()
