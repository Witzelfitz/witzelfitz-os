#!/bin/bash
# Laeuft beim Image-Build als root. Alles hier landet im System-Image
# und gilt fuer jede Installation dieses Images.

set -ouex pipefail

# Inhalt von system_files/ nach / kopieren
cp -avf "/ctx/system_files"/. /
chmod 0755 /usr/bin/witzelfitz-setup

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
    patch

### Eigene Erweiterungen kommen hier hin, z.B.:
# dnf5 install -y <paket>
#
# Pakete aus einem COPR:
# dnf5 -y copr enable <owner>/<repo>
# dnf5 -y install <paket>
# dnf5 -y copr disable <owner>/<repo>

### Acer Predator PT515-51: Turbo-Taste und Tastatur-RGB (Modul facer)
/ctx/facer.sh

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
