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
    neovim

### Eigene Erweiterungen kommen hier hin, z.B.:
# dnf5 install -y <paket>
#
# Pakete aus einem COPR:
# dnf5 -y copr enable <owner>/<repo>
# dnf5 -y install <paket>
# dnf5 -y copr disable <owner>/<repo>

### Dienste
systemctl enable podman.socket
