# Systemkorrekturen für den Predator PT515-51

Diese Anpassungen gehören zum Image-Build und enthalten keine Benutzernamen,
Passwörter oder privaten Systemberichte.

## NVIDIA-Autostart

Der geerbte Autostart führte `nvidia-settings --load-config-only` auch ohne
`~/.nvidia-settings-rc` aus. Auf dem Laptop endete er deshalb mit Status 1.
Der Image-Autostart verwendet jetzt `/usr/libexec/witzelfitz-nvidia-settings-load`.
Ohne NVIDIA-Gerät oder lesbare Einstellungsdatei beendet sich der Helfer
erfolgreich, ohne den Treiber aufzurufen. Bei vorhandenen Einstellungen lädt er
sie weiterhin; echte Ladefehler werden unverändert weitergegeben.

Das entspricht dem Rückgabeverhalten des
[NVIDIA-Konfigurationsladers](https://github.com/NVIDIA/nvidia-settings/blob/main/src/nvidia-settings.c).
Es ist keine Behebung der internen NVIDIA-Assertions oder der früheren
Standby-Abstürze. Deren Abnahme bleibt in [nvidia.md](nvidia.md) beschrieben.

## Bluetooth-Profile

Das laufende Bazzite-System setzt `bluetooth.disable_ertm=1`. Der Kernel lehnt
dann ERTM-Socketoptionen mit `EINVAL` ab; siehe
[L2CAP-Implementierung](https://github.com/torvalds/linux/blob/master/net/bluetooth/l2cap_sock.c).
Auf diesem Laptop scheiterten deshalb mehrere BlueZ-Profile mit
`setsockopt(L2CAP_OPTIONS): Invalid argument (22)`.

`bluetooth-enable-ertm.service` lädt vor BlueZ das Bluetooth-Modul und setzt
`disable_ertm` auf `N`. Der Dienst wird mit BlueZ gestartet und läuft nur bei
DMI-Hersteller `Acer` und Modell `Predator PT515-51`. Auf anderer Hardware
bleiben die Bazzite-Vorgaben erhalten. Er ändert weder Kernelargumente noch
Kopplungsdaten oder Bluetooth-Sicherheitseinstellungen.

Am 28./29. Oktober 2026 auf dem laufenden Laptop geprüft: ERTM-Socketoption
erfolgreich gesetzt, Bluetooth-Dienst aktiv, die genannten L2CAP-Profilfehler
nach dem Neustart des Dienstes nicht mehr protokolliert. Verbindungen zu
Headsets und Controllern sowie der Start aus dem neuen Image stehen noch aus.
Die separate Meldung zur fehlenden `wake-policy.conf` wird damit nicht behoben.

## Prüfung und Rückkehr

CI prüft fehlende und vorhandene NVIDIA-Konfiguration, Fehlerweitergabe und
die Hardwarebegrenzung. Am gebauten Image werden Helfer, Desktopdatei,
systemd-Unit und deren Aktivierung geprüft. Nach dem Neustart auf dem Laptop:

```bash
systemctl --user --failed
systemctl status bluetooth-enable-ertm.service bluetooth.service
cat /sys/module/bluetooth/parameters/disable_ertm
journalctl -b -u bluetooth.service --no-pager
python3 tools/check-nvidia-health.py
```

Die Bluetooth-Anpassung lässt sich bei einer Geräte-Unverträglichkeit mit
`sudo systemctl mask bluetooth-enable-ertm.service` und einem Neustart
abschalten. `sudo systemctl unmask bluetooth-enable-ertm.service` hebt dies auf.

Vorherige lokale Reparaturkopien unter `/etc/systemd/system/` und
`~/.config/autostart/` haben Vorrang vor den Image-Dateien. Erst wenn das neue
Image tatsächlich läuft und seine Dateien geprüft sind, diese konkreten
Reparaturkopien gesichert entfernen; keine fremden Benutzereinstellungen löschen.
