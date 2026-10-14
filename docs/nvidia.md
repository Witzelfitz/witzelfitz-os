# NVIDIA und Standby auf dem Predator PT515-51

## Ausgangspunkt vom 14. Oktober 2026

Das lokale Test-Deployment läuft mit Kernel `7.2.8-ogc5.1.fc44` und dem offenen
NVIDIA-Treiber `615.71.09`. Beobachtet wurden PMU-Halt/Xid 62 bei Steam und seiner
Vulkan-Abfrage sowie ein anschliessender Suspend-Absturz. Ein vorübergehendes
Unterbinden von Runtime-D3 hat einen erneuten Ausfall nicht verhindert. Es wird
deshalb kein dauerhafter Runtime-D3-Override als Reparatur eingebaut.

Der an diesem Tag geprüfte aktuelle DX-Basisstand
`ghcr.io/ublue-os/bazzite-dx-nvidia@sha256:318580f7b6c61c4d5bbb1df295f11dffe50f7082361a14bdcb4d07eb0799e858`
enthält Kernel `7.2.9-ogc3.1.fc44` und NVIDIA `615.78.08`.
Das ist ein Vergleichskandidat, keine bestätigte Behebung des Hardwareproblems.
Tägliche Builds übernehmen später verfügbare Stable-Stände.

Die Zeile `force_drivers` in `99-nvidia.conf` ist auch in diesem unveränderten
offiziellen Basisimage vorhanden. Ihr Vorhandensein belegt keine Abweichung
durch Witzelfitz OS. Die vollständige Initramfs-Erzeugung bleibt im Image-Build
für das eigene Bootdesign notwendig.

## Erster Vergleich: aktualisiertes eigenes Image

Nach erfolgreicher Veröffentlichung zuerst einen Ausgangsbericht erzeugen:

```bash
python3 tools/check-nvidia-health.py --output output/nvidia-before.json
sudo ./tools/use-signed-updates.sh
systemctl reboot
```

Der Wechsel erhält das laufende Deployment als gepinnten Rückkehrpunkt und
stellt die signierte Registry-Quelle wieder her. Automatischer Standby bleibt
zunächst in den vorhandenen Benutzereinstellungen abgeschaltet.

Nach dem Neustart:

```bash
python3 tools/check-nvidia-health.py --output output/nvidia-after-boot.json
rpm-ostree status
```

Kernel und Treiber müssen dem veröffentlichten Image entsprechen; die gebootete
Herkunft muss signierte GHCR-Updates nennen. Danach Steam wie gewohnt öffnen,
ein Spiel auf der RTX starten und mindestens 15 Minuten normal verwenden.
Anschliessend den Bericht erneut erzeugen:

```bash
python3 tools/check-nvidia-health.py --output output/nvidia-after-steam.json
```

Das Prüfwerkzeug liest Journal, Deployment-Metadaten und vorhandene procfs/sysfs-
Dateien. Es weckt die GPU nicht mit `nvidia-smi`, startet kein Spiel und löst
keinen Suspend aus. Exit-Code 1 bedeutet GPU-Fehler, 2 eine unvollständige
Prüfung. Fehlerfreiheit im Journal allein ist kein Stabilitätsnachweis.

Erst nach erfolgreicher GPU-Nutzung und fehlerfreiem Journal einen manuellen
Standby-/Aufwachzyklus durchführen; offene Arbeit vorher speichern. Bei erneutem
PMU-Halt oder Resetbedarf keinen weiteren Suspend-Test starten. Nach dem
Aufwachen denselben Check ausführen. Mehrere erfolgreiche Zyklen und der Test
mit externem Bildschirm gehören zur Abnahme. Automatischen Standby erst danach
wieder nach persönlicher Wahl einschalten.

## Falls der Fehler bleibt

Das unveränderte offizielle DX-Image ist der nächste Vergleich: dadurch ändern
sich die eigenen Image-Erweiterungen, während die DX-Basis vergleichbar bleibt.
Vorher vorhandene Zielrichtlinie kontrollieren:

```bash
jq '.transports.docker["ghcr.io/ublue-os"]' /etc/containers/policy.json
rpm-ostree status
sudo bootc switch --enforce-container-sigpolicy ghcr.io/ublue-os/bazzite-dx-nvidia:stable
systemctl reboot
```

Nur eine vorhandene signierte UBlue-Richtlinie verwenden; niemals die Prüfung
abschalten. Auf dem offiziellen Image fehlen die eigenen Image-Pakete, unter
anderem `facer`. Benutzerkopien des Desktop-Profils und Einträge in `/etc`
können bestehen bleiben. Der Vergleich ist deshalb keine vollständig frische
Installation. Die eigene Installation lässt sich danach mit
`sudo ./tools/use-signed-updates.sh` und einem Neustart wieder auswählen.

Bleibt der Fehler auch dort bestehen, einen verfügbaren älteren offiziellen
DX-Stand mit tatsächlich anderer Kernel-/Treiber-Version vergleichen. Vorher
Digest, Pakete und Signatur überprüfen. Keine älteren Einzelpakete auf dem Host
überlagern. GSP nicht auf dem offenen NVIDIA-Modul abschalten: es benötigt GSP.

Bei einem fehlgeschlagenen Start das gepinnte ursprüngliche Deployment im
Bootmenü wählen. `rpm-ostree status` zeigt die Einträge; ein Rollback stellt
deren Kernel-/Treiberkombination wieder her, repariert keinen Fehler derselben
Treiberkombination. Die Registry-Quelle nach dem Rollback erneut kontrollieren.

Quellen: [Bazzite-Rebase](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rebase_guide/),
[Bootc-Updates und Rollback](https://bootc.dev/bootc/bootc-upgrades.7.html),
[NVIDIA Open Modules](https://github.com/NVIDIA/open-gpu-kernel-modules).
