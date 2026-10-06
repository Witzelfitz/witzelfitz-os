# witzelfitz-os

Eigenes Linux für den Acer Predator Triton 500 (PT515-51, RTX 2060):
[Bazzite DX](https://github.com/ublue-os/bazzite-dx) (KDE, aktueller Nvidia-Treiber)
als Basis, darauf eine dünne eigene Schicht für Terminal-Arbeit und KI-Agenten.
Ergebnis ist ein Installations-ISO für einen USB-Stick.

## Stand (geprüft am 6.10.2026)

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

## Offen

- **Updates:** `bootc status` meldet als Quelle `localhost/witzelfitz-os:latest`.
  Diese Quelle existiert nur auf dem Bau-PC, `bootc upgrade` wird auf dem Laptop
  daher nichts finden. Aktualisieren heisst vorerst: neues ISO bauen und neu
  installieren (oder später eine Registry einführen).
