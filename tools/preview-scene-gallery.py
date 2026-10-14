#!/usr/bin/python3
"""Render a contact sheet with native Qt widgets and the real wallpaper assets."""
import argparse
import json
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--pack', type=Path)
parser.add_argument('--data-dir', type=Path, help='Private pack directory containing scenes.json and wallpapers/')
parser.add_argument('--columns', type=int, default=4, choices=range(1, 7))
args = parser.parse_args()
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

root = Path(__file__).resolve().parents[1]
defaults = root / 'system_files/usr/share/witzelfitz-desktop'
data = args.data_dir.expanduser().resolve() if args.data_dir else defaults
sys.path.insert(0, str(defaults))
from palettes import palette_for_scene
scenes = json.loads((data / 'scenes.json').read_text())
if args.pack:
    identifiers = {value['id'] for value in json.loads(args.pack.read_text())}
    scenes = [scene for scene in scenes if scene['id'] in identifiers]
    if len(scenes) != len(identifiers):
        parser.error('Some pack scenes are missing from the catalog.')

app = QApplication(sys.argv)
window = QWidget()
window.setStyleSheet('QWidget {background:#101827; color:#eaf0fb; font-family:Sans;}')
layout = QVBoxLayout(window)
layout.setContentsMargins(24, 24, 24, 24)
title = QLabel(f'{len(scenes)} Motive. Deine nächste Atmosphäre.')
title.setStyleSheet('font-size:25px; font-weight:600;')
layout.addWidget(title)
caption = QLabel('Im Szenenstudio frei mit allen Farbpaletten und Tastaturzonen kombinieren.')
caption.setStyleSheet('color:#a7b7ca; font-size:13px;')
layout.addWidget(caption)
grid = QGridLayout()
grid.setSpacing(16)
layout.addLayout(grid)
for index, scene in enumerate(scenes):
    profile = palette_for_scene(scene, defaults)
    card = QWidget()
    card.setStyleSheet(f'background:{profile["surface"]}; border-radius:8px;')
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(10, 10, 10, 10)
    image = QPixmap(str(data / 'wallpapers' / scene['file']))
    if image.isNull():
        parser.error('Invalid wallpaper: ' + scene['file'])
    picture = QLabel()
    picture.setPixmap(image.scaled(352, 198, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    picture.setFixedSize(352, 198)
    card_layout.addWidget(picture)
    name = QLabel(scene['character'])
    name.setStyleSheet('font-weight:600; font-size:15px;')
    card_layout.addWidget(name)
    series = QLabel(scene['series'])
    series.setStyleSheet('color:#a7b7ca; font-size:11px;')
    card_layout.addWidget(series)
    colors = QHBoxLayout()
    for color in profile['keyboard']:
        swatch = QLabel()
        swatch.setFixedHeight(12)
        swatch.setStyleSheet(f'background:{color}; border-radius:3px;')
        colors.addWidget(swatch)
    card_layout.addLayout(colors)
    palette = QLabel(profile['name'])
    palette.setStyleSheet(f'color:{profile["accent"]}; font-size:11px;')
    card_layout.addWidget(palette)
    grid.addWidget(card, index // args.columns, index % args.columns)
window.adjustSize()
window.show()
app.processEvents()
args.output.parent.mkdir(parents=True, exist_ok=True)
if not window.grab().save(str(args.output)):
    parser.error('Cannot save gallery.')
print(args.output)
