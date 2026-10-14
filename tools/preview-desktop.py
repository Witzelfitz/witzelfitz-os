#!/usr/bin/python3
"""Render the actual shared QML components; no HTML approximation."""
import argparse
import os
import json
from pathlib import Path
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path)
parser.add_argument("--theme", default="aurora")
parser.add_argument("--palette")
parser.add_argument("--section", type=int, default=-1)
parser.add_argument("--width", type=int, default=1920)
parser.add_argument("--height", type=int, default=1080)
args = parser.parse_args()
if args.output:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QUICK_BACKEND", "software")

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlEngine, QQmlComponent
from PySide6.QtQuick import QQuickWindow

root = Path(__file__).resolve().parents[1]
data = root / "system_files/usr/share/witzelfitz-desktop"
components = data / "qml"
sys.path.insert(0, str(data))
from palettes import load_palettes, palette_for_scene
scenes = json.loads((data / "scenes.json").read_text())
for value in scenes:
    profile = palette_for_scene(value, data)
    value.update(surface=profile["surface"], alternate=profile["alternate"], paletteName=profile["name"])
for scene in scenes:
    scene["image"] = (data / "wallpapers" / scene["file"]).as_uri()
scene = next((value for value in scenes if value["id"] == args.theme), None)
if scene is None:
    parser.error("Unbekannte Szene: " + args.theme)
if args.palette:
    profile = next((value for value in load_palettes(data) if value["id"] == args.palette), None)
    if profile is None: parser.error("Unbekannte Palette: " + args.palette)
    scene.update(palette=profile["id"], accent=profile["accent"], surface=profile["surface"], alternate=profile["alternate"], paletteName=profile["name"])
scene_json = json.dumps(scene, ensure_ascii=False)
issues = []


app = QGuiApplication(sys.argv)
QIcon.setThemeName("breeze-dark")
engine = QQmlEngine()
def warnings(values):
    for warning in values:
        message = warning.toString()
        issues.append(message)
        print(message, file=sys.stderr)
engine.warnings.connect(warnings)
qml = f'''
import QtQuick
import QtQuick.Window
import "{components.as_uri()}" as Desktop
Window {{
    id: window
    width: {args.width}; height: {args.height}; visible: true
    title: "Witzelfitz Desktop Preview"
    Desktop.Bridge {{ id: bridge }}
    property var scene: ({scene_json})
    Desktop.Scene {{ anchors.fill: parent; imageSource: window.scene.image; accent: window.scene.accent; effect: window.scene.effect; animate: !{str(bool(args.output)).lower()} }}
    Desktop.Hub {{
        objectName: "hub"; x: 60; y: 65; width: Math.min(700, window.width * 0.46); height: window.height - 190
        state: Object.assign({{}}, bridge.state, {{theme: "{args.theme}", scenes: {json.dumps(scenes, ensure_ascii=False)}}}); connected: bridge.connected; error: bridge.error; selected: {args.section}
        onAction: (name, parameter) => bridge.action(name, parameter)
    }}
}}
'''
temporary = tempfile.TemporaryDirectory(prefix="witzelfitz-preview-")
source = Path(temporary.name) / "Preview.qml"
source.write_text(qml)
component = QQmlComponent(engine)
window = None


def screenshot():
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not window.grabWindow().save(str(args.output)):
        print("Screenshot konnte nicht gespeichert werden", file=sys.stderr)
        app.exit(1)
        return
    print(args.output)
    app.exit(1 if issues else 0)


def loaded(status):
    global window
    if status == QQmlComponent.Error:
        for error in component.errors():
            print(error.toString(), file=sys.stderr)
        app.exit(1)
    elif status == QQmlComponent.Ready and window is None:
        window = component.create()
        if window is None:
            app.exit(1)
        elif args.output:
            QTimer.singleShot(2500, screenshot)

component.statusChanged.connect(loaded)
# Asynchronous import avoids a PySide/Kirigami loader-thread GIL deadlock.
component.loadUrl(QUrl.fromLocalFile(str(source)), QQmlComponent.Asynchronous)
QTimer.singleShot(15000, lambda: app.exit(1) if window is None else None)
sys.exit(app.exec())
