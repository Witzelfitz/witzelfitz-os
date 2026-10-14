# Witzelfitz Desktop

Native QtQuick/QML-Oberfläche für KDE Plasma 6.7 und Wayland. Es gibt keine
Web-App, keinen GPU-Offload-Dauerprozess und kein zusätzliches C++-Plugin.

Das öffentliche OS enthält drei abstrakte Designs. Private Bildersammlungen
werden separat aus dem Benutzerprofil geladen; siehe [Bilder und Builds](assets.md).

## Bestandteile

| Pfad unter `system_files/` | Aufgabe |
|---|---|
| `usr/share/plasma/plasmoids/io.github.witzelfitz.hub` | Natives, verschiebbares und skalierbares Desktop-Widget |
| `usr/share/plasma/wallpapers/io.github.witzelfitz.anime` | Wallpaper und Fenstererkennung über KWin/TaskManager |
| `usr/share/witzelfitz-desktop/qml` | Gemeinsame QtQuick-Komponenten, Karten und Effekte |
| `usr/share/witzelfitz-desktop/wallpapers` | Drei beim Build erzeugte abstrakte Hintergründe |
| `usr/bin/witzelfitz-desktop` | Profilinstallation, Wiederherstellung und D-Bus-Sitzungsdienst |
| `usr/share/dbus-1/services/io.github.witzelfitz.Desktop.service` | Start des Diensts bei Bedarf |
| `etc/xdg/autostart/witzelfitz-desktop.desktop` | Einmalige Einrichtung beim ersten KDE-Login |
| `usr/share/plasma/look-and-feel/io.github.witzelfitz.night` | Globales Theme mit integriertem Breeze-Stil |

Der Sitzungsdienst liefert Akku, Energieprofil und MPRIS-Metadaten über
eine JSON-Eigenschaft. Er verarbeitet D-Bus-Ereignisse und aktualisiert
zusätzlich alle 30 Sekunden. Aktionen verwenden eine feste Positivliste
und Argumentlisten ohne Shell. Weder Root-Dienst noch zusätzliche
Polkit-Regel oder erweiterte Geräteberechtigung sind erforderlich.

RGB schreibt nur auf bereits durch `facer` bereitgestellte Geräte mit
bestehender Benutzer-ACL. Das Format entspricht `apply_static_zone` aus
`cleyton1986/predator-sense`, Commit
`091d0e68c4612e3ce05fe2cd97b7002a94fd6235`: vier Bytes
`(Zonenbitmaske, Rot, Grün, Blau)` je Zone. Nicht vorhandene RGB-Geräte
blenden die Bedienelemente aus. Die physische Turbo-Taste bleibt zuständig
für Turbo; es wird keine zusätzliche Lüftersteuerung implementiert.

## Darstellung und Einstellungen

Im privaten Charakterpaket hat Konan Regen und Papierpartikel, Robin und Nami sanfte Lichtreflexionen,
Machi animierte Nen-Fäden, Beatrix Rosenblätter, Lulu Pyreflies und
Hinata sanften Onsen-Dampf. Die Illustration selbst bleibt unverformt.
Maus-Parallaxe verschiebt das Gesamtbild leicht. Die Effekte verwenden
einen Timer mit 34 ms statt einer unbeschränkten Render-Schleife.

`~/.config/witzelfitz/desktop.json` speichert die Szene, Animation und
Akku-Pause atomar. `PauseWhenCovered` und `Interactive` befinden sich
zusätzlich in KDEs Wallpaper-Konfiguration. Die öffentlichen Hintergründe
werden aus mathematischen Farbverläufen erzeugt. Die 36 bisherigen
Illustrationen und ihre Quellen liegen im privaten Benutzerpaket.

## Prüfung

```bash
python3 build_files/public-assets.py --root system_files
python3 -m unittest discover -s tests -v
python3 system_files/usr/bin/witzelfitz-desktop validate
python3 tools/preview-desktop.py --output /tmp/desktop.png --section 5
```

Der Preview-Renderer und das native Szenenstudio benötigen PySide6.
Der Hub selbst benötigt weiterhin nur die Plasma-QML-Module.
Der Preview-Renderer rendert die tatsächlichen
gemeinsamen QML-Dateien und meldet QML-Warnungen als Fehler.

Die Image-Prüfung in GitHub Actions und `make-iso.sh` kontrolliert die
Python-Laufzeit, das ausführbare Desktop-Werkzeug und die Vollständigkeit
der Szenen/Pakete. `bootc container lint` bleibt Teil des Container-Builds.

Lokal geprüft: Desktop- und Wallpaper-Pakete in Plasma 6.7.5 / Qt 6.11.2
unter Wayland, Sitzungsdienst-Aktivierung, zunächst alle 14 Szenenwechsel,
Zurückweisen ungültiger Aktionen, die bisherigen Szenen samt vier zusätzlichen
Animationen sowie statischer Darstellung, Wiederherstellung und erneutes
Aktivieren des Profils. Die Vollbild-Pause wurde mit einem gerenderten
Wayland-Fenster und zwei pixelgleichen Wallpaper-Aufnahmen geprüft; nach
dem Schliessen änderten sich die Aufnahmen wieder. Die RTX blieb beim
Desktop-Betrieb im Runtime-Suspend.

Das lokale Image `localhost/witzelfitz-os:anime` wurde vollständig gebaut
und die Assets sowie Python-Laufzeit im Container geprüft. Der bootc-Lint
besteht mit drei nicht blockierenden Warnungen
(`/boot/extlinux`, `/run/dnf`, Docker-Sysusers-Gruppe). Ein neues ISO und ein Wechsel
des gebooteten Systems sind damit noch nicht ausgeführt.

Der ergänzte Charakter-Satz enthält 22 weitere Motive und erhöht den Katalog
auf 36 Szenen. Alle 36 PNGs wurden mit Qt dekodiert und gegen die dokumentierten
Prompts abgeglichen. Diese frühere Prüfung bezog sich auf den privaten Charakterkatalog. Native QML-Vorschauen für Tenten, Futaba und Freya sowie das Studio
mit Tenten wurden ohne QML-/Qt-Warnungen gerendert. Der Sitzungsdienst zeigt
36 Szenen; die vorhandene Benutzerwahl und ihre RGB-Kopplung bleiben erhalten.
Die [Galerie und Charakterliste](desktop/character-pack.md) dokumentieren
die neuen Motive. Die öffentliche [Bootanimation](boot.md) verwendet jetzt den eigenen
Aurora-Hintergrund und wird im Image separat auf Vollständigkeit geprüft.

## Szenenstudio und eigene Szenen

`witzelfitz-scenes` ist eine native QtWidgets-Anwendung auf Basis von
PySide6. Vorschauen verwenden dieselbe `Scene.qml` wie das Wallpaper.
Die Verwaltung ruft den bestehenden Sitzungsdienst über D-Bus auf.
Die zusätzliche Aktion `reload` übernimmt neue Metadaten und normalisiert
eine ungültig gewordene aktive Auswahl auf die erste sichtbare Szene.

`library.py` führt den OS-Katalog, das private Benutzerpaket und
Benutzeranpassungen zusammen.
IDs, Farben, Effekte und Dateinamen werden validiert; Metadaten können
keine Pfade ausserhalb der jeweiligen Wallpaper-Ordner referenzieren.
Auch externe Bild-Symlinks werden verworfen. Eigene IDs verwenden UUIDs,
Bilder werden als private PNG-Kopien importiert und bleiben vom Original
unabhängig. Eingaben sind auf PNG/JPEG/WebP, 64 MB und 64 Megapixel
begrenzt; importierte Bilder werden auf maximal 3840 Pixel Kantenlänge
reduziert. OS-Szenen behalten ihre mitgelieferten Dateien und können
über Name, Farbe, Effekt und Sichtbarkeit angepasst werden.

`~/.config/witzelfitz/scenes.json` und
`~/.local/share/witzelfitz-desktop-custom/wallpapers/` liegen ausserhalb der
verwalteten OS-Kopie. Ein Image-Update überschreibt sie nicht.

Die Tests prüfen zusätzlich Bildimport, Entfernen ohne Löschen des Originals,
Pfadvalidierung inklusive Symlinks, dauerhafte Anpassungen bei OS-Metadaten-
Updates und die letzte sichtbare Szene. Die Image-Prüfung rendert das
Szenenstudio ohne Bildschirm mit Qt Offscreen.

## Abgestimmte Farben und Tastatur

`palettes.json` enthält 14 Paletten mit Akzent, Grundflächen und vier RGB-Farben.
`palettes.py` erzeugt passende native KDE-Farbschemata, skaliert die vier Farben
auf die Helligkeit und erzeugt die vier Byte-Pakete für den Acer-Treiber.
Die `.colors`-Dateien liegen unter `/usr/share/color-schemes/`; die Image-Prüfung
vergleicht sie mit den erzeugten Paletten. Die ursprüngliche Breeze-Palette
behält ihre Lizenzhinweise; übersetzte Breeze-Namen werden entfernt, damit
KDE die neuen Namen korrekt anzeigt.

Die Szene speichert optional `palette` und eigene `keyboard`-Farben. Unveränderte
Zonen bleiben an die Palette gekoppelt und folgen deren späteren Aktualisierungen.
Manuelle Zonenfarben werden als Benutzeranpassung gespeichert. Alte Szenen ohne
Palette bleiben kompatibel; ihre Akzentfarbe erzeugt eine individuelle Abstufung.
QML-Karten und Schaltflächen übernehmen zusätzlich die dunklen Grundflächen.

`appearance.py` wendet KDE-Farbschema und explizite Akzentfarbe mit dem vorhandenen
KDE-Werkzeug an. RGB verwendet ausschliesslich das bestehende Acer-Gerät und
bestehende Benutzerrechte. Ein Vergleich von Palette, Kopplung, Helligkeit und
Geräteverfügbarkeit verhindert wiederholte Schreibvorgänge bei normaler
Statusaktualisierung. Nach dem Aufwachen aus Suspend wird die gekoppelte Palette
einmal erneut angewendet; ein vollständiger Suspend-Test wurde nicht durchgeführt.
Bei deaktivierter Kopplung bleibt die zuletzt gesetzte Farbe bestehen.

`syncKeyboard`, `syncColors` und `keyboardBrightness` liegen in
`~/.config/witzelfitz/desktop.json`. Standard sind beide Kopplungen an und 65 %
Helligkeit. Ungültige Werte und RGB-Farben werden zurückgewiesen. Bei Fehlern
erscheint `appearanceError` im Hub und im Studio. Der Studio-Status übernimmt
auch Änderungen aus dem Hub. Bei wiederhergestelltem altem Desktop pausiert
die automatische Farbkopplung; die Tastatur behält ihre zuletzt gesetzten Farben.

Geprüft: Text- und Auswahlkontrast aller Paletten, kontrastreiche Zonenbeschriftung,
alle vier Zonenmasken, Helligkeitsgrenzen, dauerhafte eigene Zonenfarben,
deaktivierte Kopplung und ausbleibende wiederholte Schreibvorgänge.
Die sieben neuen Szenen wurden unter Wayland mit KDE-Schema und angenommenen
RGB-Schreibvorgängen am tatsächlichen Acer-Gerät aktiviert; Helligkeit und
ungültige Eingaben wurden über den Sitzungsdienst geprüft. Die Farbwirkung der
physischen LEDs wurde nicht fotografisch vermessen.

## Grenzen

Anwendungsaktionen benötigen die entsprechende installierte Anwendung;
ein Fehler erscheint im Hub. Mediensteuerung benötigt einen geöffneten
MPRIS-Player. Das Energieprofil bleibt unabhängig von der Szene und wird
nur auf ausdrücklichen Klick geändert.

Die Effekte sind dezente Überlagerungen, keine Animation von Gesicht oder
Kleidung und kein Wallpaper-Engine-Workshop-Renderer. Bei mehreren
Bildschirmen pausiert die Animation derzeit auf allen Bildschirmen, sobald
ein maximiertes/Vollbildfenster auf dem aktuellen virtuellen Desktop offen
ist. Ein vollständiger neuer ISO-/Hardware-Installationslauf ist von der
Desktop-Prüfung unabhängig.
