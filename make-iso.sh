#!/bin/bash
# Baut das System-Image und daraus ein Installations-ISO fuer den USB-Stick.
# Aufruf im Repo-Verzeichnis: sudo ./make-iso.sh
# Fuer eine neue Version einfach erneut ausfuehren.

set -euo pipefail

IMAGE="localhost/witzelfitz-os:latest"
BIB="quay.io/centos-bootc/bootc-image-builder:latest"
PKGS="tmux fzf ripgrep fd-find bat zoxide git-delta direnv btop neovim"

cd "$(dirname "$(readlink -f "$0")")"

if [ "$(id -u)" -ne 0 ]; then
    echo "Bitte mit sudo starten: sudo ./make-iso.sh" >&2
    exit 1
fi

echo "==> 1/4 Image bauen"
podman build --pull=newer -t "$IMAGE" -f Containerfile .

echo "==> 2/4 Image pruefen"
# shellcheck disable=SC2086
podman run --rm "$IMAGE" rpm -q $PKGS
podman run --rm "$IMAGE" test -x /usr/bin/witzelfitz-setup

echo "==> 3/4 ISO bauen"
TMP="$(mktemp -d -p "$PWD" _bib.XXXXXX)"
podman run --rm --privileged --pull=newer --net=host \
    --security-opt label=type:unconfined_t \
    -v "$PWD/disk_config/iso.toml:/config.toml:ro" \
    -v "$TMP:/output" \
    -v /var/lib/containers/storage:/var/lib/containers/storage \
    "$BIB" --type anaconda-iso --use-librepo=True --rootfs=btrfs "$IMAGE"

echo "==> 4/4 ISO ablegen"
ISO="$(find "$TMP" -name '*.iso' | head -n1)"
if [ -z "$ISO" ]; then
    echo "Es wurde kein ISO erzeugt, Ausgabe liegt in $TMP" >&2
    exit 1
fi
NAME="witzelfitz-os-$(date +%Y%m%d).iso"
mkdir -p output
mv -f "$ISO" "output/$NAME"
rm -rf "$TMP"
(cd output && sha256sum "$NAME" >"$NAME.sha256")
chown -R "${SUDO_UID:-0}:${SUDO_GID:-0}" output
ls -lh output
echo "Fertig: output/$NAME"
