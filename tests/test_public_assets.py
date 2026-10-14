"""Public build fails closed when private or modified artwork is present."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("public_assets", ROOT / "build_files/public-assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class PublicAssets(unittest.TestCase):
    def test_original_backgrounds_are_decodable(self):
        from PySide6.QtGui import QImage
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.png"
            path.write_bytes(assets.artwork("#b3a2ef"))
            image = QImage(str(path))
            self.assertFalse(image.isNull())
            self.assertEqual((image.width(), image.height()), (assets.WIDTH, assets.HEIGHT))

    def test_public_verification_rejects_extra_modified_and_symlinked_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wallpaper = root / "usr/share/witzelfitz-desktop/wallpapers/aurora.png"
            expected = {wallpaper: b"original", root / "usr/share/witzelfitz-desktop/scenes.json": b"catalog"}
            with patch.object(assets, "assets", return_value=expected):
                assets.generate(root)
                assets.generate(root, check=True)
                private = wallpaper.with_name("konan.png"); private.write_bytes(b"private")
                with self.assertRaisesRegex(ValueError, "unexpected"):
                    assets.generate(root, check=True)
                private.unlink()
                wallpaper.write_bytes(b"replacement")
                with self.assertRaisesRegex(ValueError, "differs"):
                    assets.generate(root, check=True)
                wallpaper.unlink()
                outside = root / "outside.png"; outside.write_bytes(b"original")
                wallpaper.symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "differs"):
                    assets.generate(root, check=True)


if __name__ == "__main__":
    unittest.main()
