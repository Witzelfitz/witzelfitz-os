# witzelfitz-os

Eigenes Linux für den Acer Predator Triton 500 (PT515-51, RTX 2060):
[Bazzite DX](https://github.com/ublue-os/bazzite-dx) (KDE, aktueller Nvidia-Treiber)
als Basis, darauf eine dünne eigene Schicht für Terminal-Arbeit und KI-Agenten.
Ergebnis ist ein Installations-ISO für einen USB-Stick.

> **Status: 1. Entwurf, noch nie gebaut.** Geprüft ist bisher nur die Syntax
> der Skripte und der TOML-Datei. Image-Bau, ISO-Bau und das Verhalten des
> Installers (fragt er nach der Ziel-Disk?) sind **ungeprüft**. Den Stick erst
> booten, wenn das ISO in einer VM getestet wurde.

## Aufbau

| Datei | Zweck |
|---|---|
| `Containerfile` | Basis-Image + Aufruf von `build.sh` + `bootc container lint` |
| `build_files/build.sh` | Systempakete und Dienste — **hier Pakete ergänzen** |
| `system_files/` | Wird 1:1 nach `/` im Image kopiert |
| `system_files/usr/bin/witzelfitz-setup` | Nach der Installation einmal als normaler Benutzer ausführen (Claude Code, tmux-Config, Shell-Integration) |
| `disk_config/iso.toml` | Installer-Konfiguration (Sprache, Tastatur, Zeitzone; bewusst ohne Disk-Angaben) |
| `make-iso.sh` | Baut Image und ISO in einem Lauf |

## Neu bauen

Voraussetzung: Linux mit `podman`, root-Rechten und ca. 60 GB frei unter
`/var/lib/containers` und im Repo-Verzeichnis.

```bash
sudo ./make-iso.sh 2>&1 | tee build.log
```

Das ISO landet in `output/witzelfitz-os-JJJJMMTT.iso`, daneben die `.sha256`.

## Pakete ergänzen

In `build_files/build.sh` in den `dnf5 install`-Block eintragen und denselben
Namen in `PKGS` in `make-iso.sh` ergänzen (dort wird geprüft, ob er im Image ist).

## Stick schreiben

Erst wenn das ISO geprüft ist. Stick mit mindestens ISO-Grösse, praktisch 32 GB.
Alles auf dem Stick wird gelöscht.

- **Windows:** [Fedora Media Writer](https://fedoraproject.org/workstation/download)
  → „Select .iso file“, oder [Rufus](https://rufus.ie) und beim Nachfragen
  **DD-Image-Modus** wählen.
- **Linux:** Gerät selbst mit `lsblk` bestimmen (Stick ab- und wieder anstecken,
  vergleichen), dann `sudo dd if=output/<name>.iso of=/dev/sdX bs=4M status=progress oflag=sync`.

## Offen

- Das installierte System kennt keine Update-Quelle (keine Registry).
  Was `bootc status` / `bootc upgrade` danach melden, ist ungeklärt.
