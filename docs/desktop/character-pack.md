# Neue Charaktere und Farbwelten

22 zusätzliche Illustrationen ergänzen das private Paket auf 36 Szenen. Die vorhandenen
Motive bleiben erhalten. Jede neue Szene startet mit stiller Darstellung; die
verfügbaren Animationen lassen sich im Szenenstudio einschalten.

Diese Motive gehören ausschliesslich zum privaten Benutzerpaket.
Die Bilddateien und Galerie werden nicht veröffentlicht.

| Motiv / gespeicherter Wallpaper | Sammlung | Empfohlene Palette (ID) |
|---|---|---|
| Chie Satonaka | PERSONA 4 GOLDEN | jade |
| Yukiko Amagi | PERSONA 4 GOLDEN | crimson |
| Rise Kujikawa | PERSONA 4 GOLDEN | sakura |
| Naoto Shirogane | PERSONA 4 GOLDEN | cobalt |
| Marie | PERSONA 4 GOLDEN | amethyst |
| Margaret | PERSONA 4 GOLDEN | moonstone |
| Ann Takamaki | PERSONA 5 ROYAL | crimson |
| Makoto Niijima | PERSONA 5 ROYAL | cobalt |
| Futaba Sakura | PERSONA 5 ROYAL | jade |
| Haru Okumura | PERSONA 5 ROYAL | rosewood |
| Kasumi Yoshizawa | PERSONA 5 ROYAL | royal |
| Sae Niijima | PERSONA 5 ROYAL | moonstone |
| Tae Takemi | PERSONA 5 ROYAL | amethyst |
| Sadayo Kawakami | PERSONA 5 ROYAL | champagne |
| Yuna · FFX | FINAL FANTASY X | cobalt |
| Rikku | FINAL FANTASY X | amber |
| Paine | FINAL FANTASY X-2 | crimson |
| Garnet / Dagger | FINAL FANTASY IX | amber |
| Freya Crescent | FINAL FANTASY IX | crimson |
| Eiko Carol | FINAL FANTASY IX | moonlit |
| Tenten | NARUTO · BORUTO | rosewood |
| Ino Yamanaka | NARUTO · BORUTO | royal |

Die Persona-Figuren und mehrere jüngere Spielfiguren sind hier als erwachsene
Interpretationen gestaltet; Tenten und Ino verwenden ihre erwachsenen Boruto-Versionen.
Eiko bleibt eine kindliche Figur in einer freundlichen Märchen-/Abenteuerszene.
Alle Motive sind vollständig bekleidet. Yuna erhält zusätzlich zum vorhandenen
FFX-2-Motiv eine eigene FFX-Summoner-Szene; Paine gehört zu FFX-2.

Im Studio unter **Atmosphäre → Szenen verwalten …** nach Charakter oder Sammlung
suchen. Die empfohlenen Paletten lassen sich mit allen anderen Motiven kombinieren.
Vier Tastaturzonen, Helligkeit und KDE-Kopplung bleiben individuell einstellbar.

Erzeugt mit dem integrierten Imagegen-Tool. Die endgültigen Prompts aller Szenen
liegen im privaten Paket unter `wallpapers/sources.json`.
Der neue Satz ist zusätzlich in [character-pack-20261010.json](../../tools/character-pack-20261010.json)
dokumentiert. Die Galerie rendert native Qt-Widgets und die tatsächlichen Assets:

```bash
python3 tools/preview-scene-gallery.py \
  --data-dir ~/.local/share/witzelfitz-desktop-private \
  --pack tools/character-pack-20261010.json \
  --output docs/desktop/character-pack.png
```

Offizielle Referenzen zur Charakterauswahl:
[Persona 4 Golden](https://persona.atlus.com/p4g/?lang=de),
[Persona 5 Royal](https://persona.atlus.com/p5r/),
[Final Fantasy IX](https://eu.finalfantasy.com/titles/finalfantasy9).
