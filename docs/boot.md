# Bootanimation Witzel OS

Das Plymouth-Script-Theme liegt in
`system_files/usr/share/plymouth/themes/witzelfitz/`. Es verwendet den eigenen
abstrakten Aurora-Hintergrund, den Schriftzug Witzel OS, Regen und drei Ladepunkte.
Die Firmware zeigt ihr eigenes Logo weiterhin vor dem Start von Linux.
Der Hintergrund wird beim Build mit `build_files/public-assets.py` erzeugt;
private Charakterbilder gelangen weder ins OS-Image noch ins Initramfs.

`build_files/build.sh` installiert `plymouth-plugin-script`, wählt das Theme
aus und baut das Initramfs mit Plymouth und dem ostree-Modul neu. Der Build
verlangt genau einen Kernel und bricht bei einer mehrdeutigen Auswahl ab.
Der im Container fehlende Zielordner von `/root -> var/roothome` wird
für Dracut vorübergehend angelegt und danach wieder entfernt. Das Initramfs
enthält damit auch diese Verknüpfung samt leerem Zielordner.
Die Desktop-Skripte, Python-Pakete und Boot-Dateien gehören gemeinsam zum
Build-Kontext; einen isolierten Boot-Commit darf man nicht durch Weglassen
der weiterhin referenzierten Desktop-Dateien herstellen.

`tools/check-boot-image.sh` kontrolliert das voreingestellte Theme, das
Skriptmodul und alle sieben Theme-Dateien im fertigen Initramfs. Die Prüfung
läuft auch in GitHub Actions und vor dem ISO-Bau.

```bash
podman build --pull=never -t localhost/witzelfitz-os:public -f Containerfile .
podman run --rm \
  -v "$PWD/tools/check-boot-image.sh:/check-boot-image.sh:ro,z" \
  localhost/witzelfitz-os:public bash /check-boot-image.sh
```

Ein Container-Build und die Dateiprüfung ersetzen keinen Start auf dem
Laptop. Insbesondere tatsächliche Darstellung, Timing und Passwort- bzw.
Fragedialoge müssen nach dem ersten Boot des neuen Images geprüft werden.
Es wurde kein Wechsel des gebooteten Systems und kein BIOS-Eingriff ausgeführt.

Nach dem Neustart am 10.10.2026 geprüft: Das gebootete System verwendet
weiterhin das GHCR-Image vom 09.10.2026 (Digest beginnt mit `c06e994b`),
das Theme `bgrt` und enthält `/usr/share/plymouth/themes/witzelfitz/` nicht.
Das lokale Image `localhost/witzelfitz-os:anime` besteht dagegen die
Initramfs-Prüfung mit `tools/check-boot-image.sh`. Ein Neustart allein
aktiviert kein lokal gebautes Container-Image; dafür fehlt noch die
Bereitstellung als neues System-Deployment mit Root-Rechten. Die tatsächliche
Darstellung bleibt bis zum Booten dieses Deployments ungeprüft.

## Neues lokales Image aktivieren

Das bildbereinigte Image `localhost/witzelfitz-os:public` wurde am 10.10.2026
gebaut und als OCI-Layout unter `output/witzelfitz-public-oci/` exportiert.
Bootprüfung, öffentliche Asset-Prüfung, Desktop-Validierung und ein Rendern
des Szenenstudios im Container bestehen. 26 Regressionstests bestehen;
die öffentliche QML-Desktopvorschau wurde ohne QML-Warnungen gerendert.
Der aktive Benutzerdesktop zeigt drei öffentliche und 36 private Szenen.

Die Aktivierung ist ein eigener Schritt und benötigt Root-Rechte:

Am 10.10.2026 nach Ausführung des Aktivierungsskripts bestätigt:
Das öffentliche OCI-Image mit Digest `d2be9fef5423…` ist als neues Deployment
bereitgestellt (`staged: true`). Das aktuell gebootete, signierte GHCR-System
ist gepinnt. Der Neustart in das neue Deployment steht noch aus.

```bash
sudo ~/witzelfitz-os/tools/activate-local-image.sh
# Danach bei passendem Zeitpunkt den Rechner neu starten.
```

Das Skript prüft alle exportierten OCI-Dateien gegen die gespeicherten
SHA-256-Prüfsummen, verweigert das Überschreiben eines bereits wartenden
Deployments und pinnt das aktuell laufende System als Rückweg.
Es stellt das neue Image mit `bootc switch --transport oci --retain` für den
nächsten Boot bereit und löst keinen Neustart aus. Das Verfahren entspricht
dem [lokalen bootc-Deployment](https://bootc.dev/bootc/bootc-local-builds.7.html).
Nach dem Neustart muss `plymouth-set-default-theme` den Wert `witzelfitz` zeigen.
Der tatsächliche Boot auf dem Laptop ist damit noch abzunehmen.

Dieses lokale Test-Deployment folgt dem OCI-Layout statt dem bisherigen
signierten GHCR-Kanal. Erst nachdem dieselben Änderungen über GitHub Actions
gebaut, veröffentlicht und signiert wurden, wieder auf den normalen Kanal wechseln:

```bash
sudo bootc switch --enforce-container-sigpolicy ghcr.io/witzelfitz/witzelfitz-os:latest
```

Ein sofortiger Wechsel auf das aktuell noch alte GHCR-Image würde die neue
Bootanimation wieder entfernen. Zum Rückweg kann im Bootmenü das gepinnte
vorherige Deployment gewählt werden.

Bei einem rootlosen Podman-Bau meldet Dracut nicht unterstützte
SELinux-xattr-Kopien und fehlendes Syslog im Container. Die explizite
Initramfs-Prüfung kontrolliert die benötigten Dateien unabhängig davon.

Die vorhandene Python/WebP-Vorschau in `tools/make-plymouth-theme.py`
stellt den Ablauf nach; sie führt das Plymouth-Skript nicht aus. Sie schreibt
die Theme-PNGs ausschliesslich unter `output/plymouth-preview/` neu.
Mit `--data-dir` und `--scene` lassen sich private Motive dort lokal ansehen.
Zur reinen Image-Abnahme ist das nicht erforderlich.

Die verwendeten Skriptfunktionen wurden mit den Quellen des
[Plymouth-Skriptmoduls](https://gitlab.freedesktop.org/plymouth/plymouth/-/tree/24.004.60/src/plugins/splash/script)
verglichen. Die Übergabe der anderen Sitzung bleibt unter
`~/uebergabe-2026-10-10.md` erhalten. Ihre offenen Punkte zu SSH,
RetroArch und Battle.net sind unabhängig von diesem Desktop-/Boot-Build.
