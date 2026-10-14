# Öffentliche und private Bilder

Das Repository, öffentliche Container-Images und ISOs enthalten keine private
Charakter-Bildersammlung. Die drei Standarddesigns Aurora, Ocean und Ember
entstehen aus mathematischen Farbverläufen in `build_files/public-assets.py`.
Der Plymouth-Hintergrund entspricht Aurora; Schriftzug und Ladeelemente
enthalten keine Charakterillustration.

## Build

`.gitignore` schliesst Bildersammlung, Quellen und private Vorschauen aus.
`.containerignore` und `.dockerignore` schliessen auch lokale Wallpaper-Dateien
und das lokal erzeugte Bootbild vom Build-Kontext aus. `build.sh` erzeugt die
öffentlichen Bilder nach dem Kopieren der Systemdateien. Damit funktioniert
ein frischer Checkout ohne Zugriff auf persönliche Dateien.

GitHub Actions und `make-iso.sh` prüfen die generierten Bildinhalte und den
Katalog bytegenau und weisen zusätzliche Dateien im Wallpaper-Ordner zurück.
Die separate Bootprüfung kontrolliert, dass das neue Theme und der
Plymouth-Skriptrenderer im Initramfs enthalten sind.

```bash
python3 build_files/public-assets.py --root system_files
python3 build_files/public-assets.py --root system_files --check
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

## Privates Benutzerpaket

`~/.local/share/witzelfitz-desktop-private/` enthält `scenes.json` und
`wallpapers/`. Mit gesetztem `XDG_DATA_HOME` liegt es dort statt unter
`~/.local/share`. Das OS liest dieses Paket zur Laufzeit, kopiert es jedoch
nicht in einen Build. Sichere diesen Ordner zusammen mit deinen persönlichen
Dateien. Die bisherige Sammlung wurde dort samt Quellen und altem Bootbild
gesichert; die 36 Originalbilder wurden beim Umzug bytegleich geprüft.

Eine neue Sammlung kann aus einem Ordner mit demselben Aufbau installiert werden:

```bash
python3 tools/install-private-pack.py /pfad/zum/paket
```

Private Pakete können öffentliche IDs nicht ersetzen. Ungültige Metadaten,
Pfadwechsel und Symlinks auf Bilder ausserhalb des Pakets werden verworfen.
Persönliche Namen, Farben, Animationen und ausgeblendete Szenen bleiben unter
`~/.config/witzelfitz/scenes.json` gespeichert. Zurücksetzen einer privaten
Szene entfernt ihre Anpassungen und behält ihr Originalbild.

Einzelbild-Importe des Szenenstudios bleiben weiterhin unter
`~/.local/share/witzelfitz-desktop-custom/wallpapers/`. Diese beiden privaten
Ordner werden von OS-Updates und `install-user` nicht überschrieben.
