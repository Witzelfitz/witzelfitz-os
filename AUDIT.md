# Prüfung vom 9. Oktober 2026

Geprüft wurden alle 18 ursprünglich versionierten Dateien, die vier Git-Commits,
der veröffentlichte OCI-Manifest-/Konfigurationsdatensatz, die beiden bisherigen
Build-Läufe und die RGB-Schreibfunktionen des fest eingebundenen `facer`-Quellcodes.
Ausgangsstand: `94589e85e600ff2d207ecfdbe4eed0926c424930`.
Nach Entfernung der Co-Autoren-Trailer bei identischem Dateibaum:
`d560d56479de0dadd2426da760b9d05ceae761de`.

Die folgenden Korrekturen liegen im Prüf-Branch `fix/audit-hardening`.
Sie sind erst nach dessen Übernahme Bestandteil von `main` und neuer Images.

## Distribution und Signatur

- Öffentlich und ohne Login abrufbar: `ghcr.io/witzelfitz/witzelfitz-os:latest`.
- Am Prüfzeitpunkt aufgelöster Digest:
  `sha256:5b756035d43367f288f051da27820cf99e49ab357cf415c936ea10f62fabcb89`.
- `cosign verify --key cosign.pub ghcr.io/witzelfitz/witzelfitz-os@sha256:5b756035d43367f288f051da27820cf99e49ab357cf415c936ea10f62fabcb89`
  erfolgreich: Signatur, Image-Identität und Transparenzlog-Nachweis geprüft.
- Öffentliche Schlüssel in `cosign.pub` und `system_files/etc/pki/containers/`
  sind identisch. Im versionierten Projekt wurde kein privater Schlüssel gefunden.
- Das ist eine OCI-Distributionsadresse bei GHCR; eine zusätzliche Domain- oder
  Distributionsregistrierung ist durch das Repository nicht belegt.

## Befunde und vorbereitete Korrekturen

### 1. Hoch: Erste Update-Umstellung ohne erzwungene Signaturprüfung

Die bisherige README empfahl zunächst `bootc switch` ohne
`--enforce-container-sigpolicy`, um erst mit diesem Image Schlüssel und Richtlinie
zu erhalten. Damit bestand beim ersten Bezug keine verpflichtende Prüfung gegen
den eigenen Schlüssel. Ausserdem erzeugt `make-iso.sh` weiterhin ein lokales Image:
Ein frisches ISO wechselt nicht automatisch auf GHCR.

Korrektur: Die README installiert Schlüssel und Registry-Richtlinie aus einer
vertrauenswürdigen Repository-Kopie **vor** dem ersten erzwungen signierten Wechsel.
Die lokale ISO-Referenz und der nötige Wechsel werden ausdrücklich erklärt.
Die Vertrauenswürdigkeit der erstmalig bezogenen Repository-Kopie bleibt Voraussetzung.
Siehe [bootc switch](https://bootc.dev/bootc/man/bootc-switch.8.html).

### 2. Mittel: Fehlerhafte Benutzerkopien im RGB-Kerneltreiber

Im eingebundenen Upstream-Commit `091d0e68c4612e3ce05fe2cd97b7002a94fd6235`
prüfen `gkbbl_drv_write` und `gkbbl_static_drv_write` einen `unsigned long` mit
`err < 0`. `copy_from_user` meldet nicht kopierte Bytes als positive Zahl;
der Fehlerzweig wird deshalb nie ausgeführt. Die statische Variante kopiert
zusätzlich vor der Längenprüfung. Fehlerhafte Eingaben können so trotz
fehlgeschlagenem Kopieren die Firmware-Schreiblogik erreichen. Eine
Rechteausweitung wurde nicht nachgewiesen.

Korrektur: `build_files/facer-usercopy.patch` prüft zuerst die Länge und bricht bei
Kopierfehlern mit `-EFAULT`, bei ungültiger Länge mit `-EINVAL` ab. Der Patch wird
beim Image-Bau auf die festgelegte Quelle angewandt; Abweichungen brechen den Bau ab.
[Betroffene Upstream-Quelle](https://github.com/cleyton1986/predator-sense/blob/091d0e68c4612e3ce05fe2cd97b7002a94fd6235/predator-sense-gui/kernel/facer.c#L2693).

### 3. Mittel: Benutzer-Setup konnte als root laufen und unvollständige Downloads ausführen

`witzelfitz-setup` verhinderte keinen Aufruf mit `sudo`. `curl | bash` konnte bereits
Teile des Installers ausführen, bevor ein Downloadfehler erkannt wurde.
Ein vorhandenes `~/.local/bin/claude` wurde bei fehlendem PATH-Eintrag übersehen.

Korrektur: root ablehnen, lokalen Bin-Pfad zuerst setzen und den Installer vollständig
herunterladen, bevor er ausgeführt wird. Fünf Regressionstests decken diese Fälle
sowie wiederholte Aufrufe und den Erhalt bestehender tmux-Konfigurationen ab.
Der offizielle Installer bleibt eine zur Laufzeit bezogene externe Abhängigkeit;
es gibt damit weiterhin keine festgeschriebene, reproduzierbare Agenten-Version.

### 4. Mittel: Windows-Pfade und native WSL-Fehler

Ein Apostroph im Repository-Pfad konnte die in Bash eingebetteten einfachen
Anführungszeichen beenden und Shell-Ausdrücke als root in WSL ausführen.
Zudem wurde der Erfolg von WSL-Auflistung, Installation und Pfadübersetzung nicht
explizit geprüft; `$ErrorActionPreference` allein genügt dafür nicht allgemein.

Korrektur: POSIX-Quoting für variable Pfade, zitierte Dateinamen und explizite
Prüfung von `$LASTEXITCODE`. Ein vollständiger Windows-/WSL-Bau bleibt separat zu testen.

### 5. Niedrig: Fremde Image-Metadaten und unnötige CI-Berechtigungen

Das veröffentlichte Image nennt in seinen OCI-Feldern Bazzite als Titel, Quelle und
Vendor; auch die Revision stammt vom Basisprojekt. Die CI speicherte Checkout-
Zugangsdaten und erlaubte unbenötigte OIDC-Token.

Korrektur: Eigene Projekt-/Autoren-Metadaten und CI-Revision setzen, Checkout ohne
persistierte Zugangsdaten, OIDC-Berechtigung entfernen, Gleichheit der öffentlichen
Schlüssel und Skripte vor dem Image-Bau prüfen. Kernel-Auswahl scheitert bei mehreren
Kandidaten künftig ausdrücklich statt willkürlich den ersten zu verwenden.

## Noch offen

- **Secure Boot:** `facer.ko` ist weiterhin unsigniert. Die vorhandene Dokumentation
  fordert deshalb deaktiviertes Secure Boot; die Korrekturen ändern das nicht.
- **Veröffentlichung vor Signatur:** Die CI überschreibt `latest` und Datums-Tags vor
  `cosign sign`. Fehler oder ein abgebrochener Lauf können ein unsigniertes Image
  unter diesen Tags hinterlassen. Korrekt konfigurierte Clients lehnen es ab;
  Updates sind dann bis zur erfolgreichen Signierung blockiert. Als Folgearbeit
  erst einen Kandidaten nach Digest signieren und prüfen, dann öffentliche Tags setzen.
- **Veränderliche Basis/Builder:** `stable` und `latest` ermöglichen frische Updates,
  aber keine exakt reproduzierbaren Builds. Es gibt keinen eigenen Paket-/CVE-Scan.
- **VM-Test:** `test-iso.sh` verwendet eine vorhandene Testdisk erneut; nur der erste
  Aufruf erzeugt die in der Beschreibung genannte leere Disk.
- **Build-Abbruch:** `make-iso.sh` räumt temporäre Container/Verzeichnisse auf
  Fehlerpfaden nicht zuverlässig auf. Wiederholte Fehlläufe können Speicher belegen.
- **Projektlizenz:** Keine eigene `LICENSE`-Datei vorhanden; das geerbte OCI-Lizenzfeld
  des Basisimages klärt die Lizenz der eigenen Projektdateien nicht.

## Nachweise und Grenzen

- ShellCheck für alle eigenen Shell-Skripte: bestanden.
- `python3 -m unittest discover -s tests -v`: fünf Tests bestanden.
- Actionlint: bestanden mit Ausnahme der bereits erfolgreich verwendeten
  Runner-Bezeichnung `ubuntu-26.04`, die Actionlint 1.7.12 noch nicht kennt.
- Patch-Anwendung auf die festgelegte `facer`-Quelle: bestanden.
- Der PR führt zusätzlich PowerShell-Syntaxprüfung und einen vollständigen
  Linux-Image-Bau mit Kernelmodul und `bootc container lint` aus.
- Lokal unter macOS wurde kein Linux-Image/ISO gebaut und kein Kernelmodul geladen.
  Keine erneute Installation, kein Nvidia-/RGB-Hardwaretest, kein Secure-Boot-Test,
  kein vollständiger Windows-/WSL-Test und kein vollständiger CVE-Scan des Basisimages.

Die zwei Co-Autoren-Trailer wurden aus der erreichbaren `main`-Historie entfernt.
Alte Commit-URLs, GitHub-Caches, frühere Action-Läufe und fremde Klone können den
alten Stand weiterhin enthalten. Claude Code bleibt als nutzbares Werkzeug erhalten.
