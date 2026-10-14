"""Apply a coordinated palette on scene changes, without periodic RGB writes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from palettes import keyboard_packets, palette_for_scene, scheme_text


class Appearance:
    def __init__(self, data, share, device="/dev/acer-gkbbl-static-0"):
        self.data, self.share, self.device = Path(data), Path(share), Path(device)
        self.signature = None
        self.status = {"appearanceError": "", "keyboardApplied": False, "colorsApplied": False, "keyboardZones": []}

    def apply(self, scene, settings, force=False):
        profile = palette_for_scene(scene, self.data)
        available = os.access(self.device, os.W_OK)
        signature = (profile["scheme"], profile["accent"], profile["surface"], profile["alternate"],
                     tuple(profile["keyboard"]), settings["syncKeyboard"], settings["syncColors"],
                     settings["keyboardBrightness"], available)
        if signature == self.signature and not force:
            return dict(self.status)
        self.signature = signature
        self.status = {"appearanceError": "", "keyboardApplied": False, "colorsApplied": False, "keyboardZones": []}
        errors = []
        if settings["syncColors"]:
            try:
                folder = self.share / "color-schemes"; folder.mkdir(parents=True, exist_ok=True)
                path = folder / (profile["scheme"] + ".colors")
                text = scheme_text(profile, self.data / "WitzelfitzNight.colors")
                if not path.is_file() or path.read_text() != text:
                    fd, temporary = tempfile.mkstemp(dir=folder, prefix=".palette-")
                    try:
                        with os.fdopen(fd, "w") as stream: stream.write(text)
                        os.replace(temporary, path)
                    finally:
                        if os.path.exists(temporary): os.unlink(temporary)
                if not shutil.which("plasma-apply-colorscheme"):
                    raise ValueError("KDE-Farbverwaltung ist nicht verfügbar.")
                subprocess.run(["plasma-apply-colorscheme", "--accent-color", profile["accent"], profile["scheme"]], check=True,
                               capture_output=True, timeout=5)
                self.status["colorsApplied"] = True
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                errors.append(f"KDE-Farben: {exc}")
        if settings["syncKeyboard"] and available:
            try:
                packets = keyboard_packets(profile["keyboard"], settings["keyboardBrightness"])
                with open(self.device, "wb", buffering=0) as device:
                    for packet in packets:
                        if device.write(packet) != 4:
                            raise OSError("Tastatur hat die Farbe nicht vollständig übernommen.")
                self.status["keyboardApplied"] = True
                self.status["keyboardZones"] = ["#" + packet[1:].hex() for packet in packets]
            except (OSError, ValueError) as exc:
                errors.append(f"Tastatur: {exc}")
        self.status["appearanceError"] = " · ".join(errors)
        if errors:
            self.signature = None  # Retry on the next refresh or explicit scene activation.
        return dict(self.status)
