#!/bin/bash
# Laeuft beim Image-Build als root. Alles hier landet im System-Image
# und gilt fuer jede Installation dieses Images.

set -ouex pipefail

# Inhalt von system_files/ nach / kopieren
cp -avf "/ctx/system_files"/. /
python3 /ctx/public-assets.py --root /
chmod 0755 /usr/bin/witzelfitz-setup
chmod 0755 /usr/bin/witzelfitz-desktop /usr/bin/witzelfitz-scenes
chmod 0755 /usr/libexec/witzelfitz-nvidia-settings-load

### Terminal- und Agenten-Werkzeuge (alle aus den Fedora-Repos)
dnf5 install -y \
    tmux \
    fzf \
    ripgrep \
    fd-find \
    bat \
    zoxide \
    git-delta \
    direnv \
    btop \
    neovim \
    patch \
    python3-dbus \
    python3-gobject \
    python3-pyside6

### Eigene Erweiterungen kommen hier hin, z.B.:
# dnf5 install -y <paket>
#
# Pakete aus einem COPR:
# dnf5 -y copr enable <owner>/<repo>
# dnf5 -y install <paket>
# dnf5 -y copr disable <owner>/<repo>

### Acer Predator PT515-51: Turbo-Taste und Tastatur-RGB (Modul facer)
/ctx/facer.sh

### Bootanimation «Witzel OS» statt Herstellerlogo (bgrt)
# Plymouth laeuft aus dem initramfs, darum wird es danach neu gebaut.
dnf5 install -y plymouth-plugin-script
plymouth-set-default-theme witzelfitz
BOOT_KERNELS=(/usr/lib/modules/*)
if [ "${#BOOT_KERNELS[@]}" -ne 1 ] || [ ! -d "${BOOT_KERNELS[0]}" ]; then
    echo "Erwartet genau einen Kernel für das Plymouth-Initramfs." >&2
    exit 1
fi
KVER=${BOOT_KERNELS[0]##*/}
# Bazzites /root zeigt auf var/roothome; das Ziel fehlt im Container.
# Dracut übernimmt nur auflösbare Links. Leeres Ziel nur für den Bau anlegen.
BOOT_ROOT_CREATED=false
if [ "$(readlink /root)" = var/roothome ] && [ ! -e /var/roothome ]; then
    mkdir -m 0700 /var/roothome
    BOOT_ROOT_CREATED=true
fi
dracut --no-hostonly --kver "$KVER" --reproducible --zstd -v --add ostree \
    -f "/usr/lib/modules/$KVER/initramfs.img"
if "$BOOT_ROOT_CREATED"; then
    rmdir /var/roothome
fi
chmod 0600 "/usr/lib/modules/$KVER/initramfs.img"

### Signaturpruefung fuer Updates aus ghcr.io/witzelfitz/witzelfitz-os
# Der oeffentliche Schluessel liegt als cosign.pub im Repo-Wurzelverzeichnis
# und wird von system_files nach /etc/pki/containers/witzelfitz-os.pub kopiert.
POLICY=/etc/containers/policy.json
jq '.transports.docker["ghcr.io/witzelfitz/witzelfitz-os"] = [{
        "type": "sigstoreSigned",
        "keyPath": "/etc/pki/containers/witzelfitz-os.pub",
        "signedIdentity": {"type": "matchRepository"}
    }]' "$POLICY" >/tmp/policy.json
install -m 0644 /tmp/policy.json "$POLICY"

### Dienste
systemctl enable podman.socket
systemctl enable bluetooth-enable-ertm.service
