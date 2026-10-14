# witzelfitz-os

Eigenes Linux für den Acer Predator Triton 500 (PT515-51, RTX 2060):
[Bazzite DX](https://github.com/ublue-os/bazzite-dx) (KDE, aktueller Nvidia-Treiber)
als Basis, darauf eine dünne eigene Schicht für Terminal-Arbeit und KI-Agenten.
Ergebnis ist ein Installations-ISO für einen USB-Stick.

## Distribution und Autor

Autor und Maintainer: **Witzelfitz**.
Das öffentliche Distributions-Image liegt in der **GitHub Container Registry**:
[`ghcr.io/witzelfitz/witzelfitz-os:latest`](https://github.com/users/Witzelfitz/packages/container/package/witzelfitz-os).
Am 9.10.2026 wurden der anonyme Registry-Zugriff und die cosign-Signatur mit
`cosign.pub` erfolgreich geprüft. Das ist eine OCI-Registry-Adresse, keine
eigenständige Projekt-Domain oder formale Registrierung als Linux-Distribution.

Die Ergebnisse der Quellcodeprüfung stehen in [AUDIT.md](AUDIT.md).

## Stand (Image-/VM-Test laut bisheriger Dokumentation vom 6.10.2026)

- Image und ISO bauen durch (`bootc container lint`: bestanden, nur Warnungen aus der Basis).
- Im Image: alle eigenen Pakete, `witzelfitz-setup`, Nvidia-Treiber 615.71 (`kmod-nvidia`), Steam.
- ISO in einer VM getestet (UEFI, leere 40-GB-Disk, **ohne Netzwerk**):
  - Der Installer fragt nach dem Ziel und installiert nicht ungefragt.
  - Sprache Deutsch (Schweiz), Tastatur ch, Zeitzone Zürich sind vorbelegt.
  - Die Installation läuft offline durch, das Image steckt im ISO.
  - Das installierte System bootet bis zum KDE-Login.
- Nicht geprüft: echte Hardware (Nvidia, Hybrid-Grafik), `witzelfitz-setup` (braucht Netz).

## Aufbau

| Datei | Zweck |
|---|---|
| `Containerfile` | Basis-Image + Aufruf von `build.sh` + `bootc container lint` |
| `build_files/build.sh` | Systempakete und Dienste — **hier Pakete ergänzen** |
| `system_files/` | Wird 1:1 nach `/` im Image kopiert |
| `system_files/usr/bin/witzelfitz-setup` | Nach der Installation einmal als normaler Benutzer ausführen (Claude Code, tmux-Config, Shell-Integration) |
| `disk_config/iso.toml` | Installer-Konfiguration (Sprache, Tastatur, Zeitzone; bewusst ohne Disk-Angaben) |
| `make-iso.sh` | Baut Image und ISO in einem Lauf (Linux, root) |
| `test-iso.sh` | Startet das ISO in einer VM: UEFI, leere 40-GB-Disk, kein Netzwerk |
| `build-windows.ps1` | Dasselbe unter Windows über WSL 2 (Fedora) |
| `build_files/facer.sh` | Baut das Modul `facer` (predator-sense) gegen den Image-Kernel: Turbo-Taste und Tastatur-RGB des PT515-51 |
| `system_files/usr/lib/{modprobe.d,modules-load.d,udev/rules.d}/*facer*`, `*acer-rgb*` | `acer_wmi` blockieren, `facer` laden, RGB-Geräte nur für den angemeldeten Benutzer |
| `.github/workflows/build.yml` | Baut täglich und bei jedem Push, lädt nach `ghcr.io/witzelfitz/witzelfitz-os` und signiert mit cosign |
| `cosign.pub`, `system_files/etc/pki/containers/witzelfitz-os.pub` | Öffentlicher Signaturschlüssel. Der private liegt nur als GitHub-Secret `SIGNING_SECRET` vor (Sicherung bei Beni) |
| `system_files/etc/containers/registries.d/witzelfitz-os.yaml` | Signaturen aus der Registry lesen. Die Regel in `policy.json` setzt `build.sh` |

## Neu bauen

**Windows**: PowerShell im Repo-Verzeichnis. Das ISO oben wurde mit denselben
Schritten von Hand in WSL gebaut; `build-windows.ps1` selbst lief bis in den
Image-Bau, ein kompletter Lauf steht noch aus. WSL belegt beim Bau bis zur
Hälfte des Arbeitsspeichers, andere grosse Programme vorher schliessen.

```powershell
.\build-windows.ps1          # richtet beim ersten Mal WSL-Fedora + podman ein, baut, kopiert ISO nach .\output\
.\build-windows.ps1 -Test    # danach zusätzlich das ISO in einer VM starten
```

**Linux**: podman, root und ca. 60 GB frei unter `/var/lib/containers` und im Repo

```bash
sudo ./make-iso.sh 2>&1 | tee build.log
sudo ./test-iso.sh           # optional: VM-Test
```

Das ISO landet in `output/witzelfitz-os-JJJJMMTT.iso`, daneben die `.sha256`.
Erster Bau ca. 30 Minuten (Basis-Image ~20 GB), ISO ca. 8 GB.

## Pakete ergänzen

In `build_files/build.sh` in den `dnf5 install`-Block eintragen und denselben
Namen in `PKGS` in `make-iso.sh` ergänzen (dort wird geprüft, ob er im Image ist).

## Stick schreiben

Stick mit mindestens 16 GB, praktisch 32 GB. **Alles auf dem Stick wird gelöscht.**

- **Windows:** [Fedora Media Writer](https://fedoraproject.org/workstation/download)
  → „Select .iso file“ → ISO aus `output\` → Stick wählen → Write.
  Alternativ [Rufus](https://rufus.ie): ISO wählen, „Start“, bei der Nachfrage
  **„Im DD-Image-Modus schreiben“** wählen.
- **Linux:** Gerät selbst mit `lsblk` bestimmen (Stick ab- und wieder anstecken,
  vergleichen), dann
  `sudo dd if=output/<name>.iso of=/dev/sdX bs=4M status=progress oflag=sync`.

Am Laptop (nicht getestet, bei Acer üblich): Stick anstecken, beim Einschalten
**F12** für das Boot-Menü (ggf. vorher im BIOS mit **F2** „F12 Boot Menu“
aktivieren), Stick wählen. Im
Installer unter „Installations-Ziel“ die interne SSD wählen; „Automatisch“
löscht Windows vollständig.

Nach der Installation einmal im Terminal: `witzelfitz-setup`

## Witzelfitz-Desktop

Öffentliche Images und ISOs enthalten drei eigene abstrakte Hintergründe:
**Aurora**, **Ocean** und **Ember**. `build_files/public-assets.py` erzeugt sie
beim Build ohne zusätzliche Bibliotheken. GitHub Actions und der ISO-Bau prüfen
den Katalog, die Bildinhalte und das Fehlen zusätzlicher Bilder.

Private Motive und Vorschauen sind sowohl in Git als auch im Container-Build
ausgeschlossen. Deine bisherige Sammlung liegt separat unter
`~/.local/share/witzelfitz-desktop-private/` und wird vom Desktop automatisch
eingelesen. Die gewählte Szene und persönliche Anpassungen bleiben erhalten.
Weitere private Pakete lassen sich mit
`python3 tools/install-private-pack.py /pfad/zum/paket` installieren; ein Paket
enthält `scenes.json` und `wallpapers/`. Details: [Bilder und Builds](docs/assets.md).

Das Image enthält den **Witzelfitz Hub** als natives Plasma-6-Widget und
**Anime Atmosphere** als Wallpaper-Plugin. Beim ersten KDE-Login richtet
`witzelfitz-desktop apply --if-unconfigured` das Profil ein. Eine Sicherung
des bisherigen Layouts und der Farbeinstellungen liegt unter
`~/.local/state/witzelfitz-desktop/`. Weitere Logins überschreiben das
persönliche Layout nicht.

- Drei öffentliche Designs; zusätzliche private Szenen erscheinen im selben Hub.
- Sechs Bereiche: Games, Workspace, Orte, Sound, System und Atmosphäre.
- Szenenwechsel, Animation, Akku-Pause und vorhandene Acer-RGB-Geräte
  werden unter **Atmosphäre** gesteuert.
- Effekte laufen mit etwa 29 FPS und pausieren standardmässig auf Akku,
  bei maximierten/Vollbildfenstern und bei Bildschirmsperre. Der Hintergrund
  verwendet den Desktop-Renderer; keine laufende Nvidia-Abfrage.
- Dateien auf dem Desktop werden ausgeblendet und bleiben im Desktop-Ordner
  erhalten; der Hub öffnet ihn über **Orte → Desktop-Dateien**.

### Eigene Designs verwalten

Das OS-Image enthält zusätzlich die [Bootanimation Witzel OS](docs/boot.md)
mit dem eigenen Aurora-Motiv. Theme-Dateien und Skriptmodul werden im
Initramfs geprüft; die Darstellung auf dem Laptop ist nach dem ersten
Start des neuen Images noch abzunehmen.

**Atmosphäre → Szenen verwalten …** öffnet das native **Witzelfitz
Szenenstudio**. Du findest es auch im Anwendungsmenü oder startest es mit
`witzelfitz-scenes`.

- Vorschaubilder, Suche und Live-Vorschau, ohne die aktive Szene zu wechseln.
- Designname, Charakter, Sammlung, Akzentfarbe und Animation bearbeiten.
- 14 abgestimmte Paletten für Karten, KDE-Fenster und vier Tastaturzonen.
- Farben jeder Tastaturzone individuell wählen und Helligkeit von 0 bis 100 % regeln.
- Tastatur und KDE-Farben unabhängig mit der Szene koppeln oder entkoppeln.
- Eigene PNG-, JPEG- und WebP-Bilder importieren; das Original bleibt erhalten.
- Einzelne Szenen im Hub ausblenden, Originaldesigns zurücksetzen oder eigene
  importierte Designs entfernen. Mindestens eine Szene bleibt sichtbar.
- Animation und Akku-Pause ändern.

**Änderungen speichern** übernimmt Anpassungen; **Auf Desktop aktivieren**
wechselt die Szene. Eigene Bilder werden bis maximal 3840 Pixel Kantenlänge
als PNG-Kopie gespeichert. Benutzeranpassungen liegen in
`~/.config/witzelfitz/scenes.json`, eigene Bilder unter
`~/.local/share/witzelfitz-desktop-custom/wallpapers/`. Beide bleiben bei
OS-Updates und `install-user` erhalten. Neue Szenen sind sofort im Hub verfügbar.

Die Szene bringt eine empfohlene Palette mit, jede andere Palette ist ebenfalls
wählbar. **Jade Temple**, **Crimson Empress**, **Ocean Blue**, **Sakura Bloom**,
**Amber Lantern**, **Champagne Noir**, **Mint Garden**, **Royal Violet**,
**Cobalt City**, **Moonstone Silver**, **Golden Sunset**, **Rosewood Castle**,
**Moonlit Lavender** und **Amethyst Night** sind enthalten. Änderungen an einer
aktiven Szene werden beim Speichern übernommen; **Auf Desktop aktivieren**
wechselt auch das Bild. Tastatur- und KDE-Kopplung sind standardmässig aktiv,
die Tastatur-Helligkeit beginnt bei 65 %. Die beiden Kopplungsschalter lassen
manuelle Farben bestehen. Farbschemata stehen zusätzlich in KDEs normaler
Farbverwaltung zur Auswahl.

Zur vorherigen Oberfläche zurück:

```bash
witzelfitz-desktop restore
```

Erneut aktivieren: `witzelfitz-desktop apply`. Die Wiederherstellung startet
Plasmashell neu; offene Anwendungen bleiben bestehen. Die ursprüngliche
Sicherung bleibt auch nach erneutem Anwenden der Rückkehrpunkt.

Für eine bestehende Installation ohne neues System-Image:

```bash
python3 system_files/usr/bin/witzelfitz-desktop install-user
~/.local/bin/witzelfitz-desktop apply
```

Diese Installation kopiert dieselben Pakete ins Benutzerprofil. Sobald die
OS-Version unter `/usr/bin/witzelfitz-desktop` vorhanden ist, übernimmt sie
die Steuerung und aktualisiert die verwalteten lokalen Kopien beim Login.
Persönliche Einstellungen bleiben dabei erhalten.

Architektur, Tests und Grenzen: [docs/desktop.md](docs/desktop.md).

## Updates

Das Image wird von GitHub Actions täglich neu gebaut, also mit aktueller Bazzite-Basis, aktuellem Kernel und Nvidia-Treiber, und signiert nach `ghcr.io/witzelfitz/witzelfitz-os:latest` geladen. Ein installiertes System holt die Updates mit `uupd` bzw. `bootc upgrade`.

Einmalige Umstellung eines Systems, das noch auf `localhost/witzelfitz-os`
oder einem lokalen OCI-Export läuft: im aktuellen Repository ausführen:

```bash
sudo ./tools/use-signed-updates.sh
# Erst nach erfolgreichem Bereitstellen und zu einem passenden Zeitpunkt:
systemctl reboot
```

Das Werkzeug prüft die Signatur des veröffentlichten Digests, installiert die
Signaturrichtlinie, pinnt das laufende System als Rückkehrpunkt und stellt
`latest` mit erzwungener Signaturprüfung bereit. Ein bereits vorgemerktes
Deployment wird nicht ersetzt. Es startet den Laptop nicht selbst neu.
Das Repository und sein öffentlicher Schlüssel müssen vertrauenswürdig bezogen sein.

Die CI lädt zunächst einen eindeutigen Kandidaten hoch, signiert und prüft ihn,
und setzt erst danach die öffentlichen Update-Tags; `latest` folgt zuletzt.
Ein lokales ISO oder OCI-Test-Image folgt bis zur Umstellung weiter seiner
lokalen Quelle. Der laufende `uupd.timer` allein ändert diese Quelle nicht.

NVIDIA-/Standby-Abnahme und Vergleich mit dem Basisimage: [docs/nvidia.md](docs/nvidia.md).

**Secure Boot muss aus bleiben**, solange `facer` unsigniert ist.

## Offen

- **Secure Boot:** `facer` ist unsigniert. Für Secure Boot bräuchte es einen eigenen MOK-Schlüssel, mit dem `facer.ko` im Build signiert wird.
