#!/usr/bin/bash
# facer (predator-sense) fuer den Acer Predator PT515-51 ins Image bauen:
# Turbo-Taste und Tastatur-RGB. Aufruf aus build.sh: /ctx/facer.sh
# ROOT und KVER nur fuer Probelaeufe ausserhalb des Image-Baus setzen.
set -euo pipefail

FACER_COMMIT=091d0e68c4612e3ce05fe2cd97b7002a94fd6235

ROOT=${ROOT:-}
KVER=${KVER:-$(ls /usr/lib/modules | head -n1)}

src=$(mktemp -d)
trap 'rm -rf "$src"' EXIT

curl -fsSL "https://github.com/cleyton1986/predator-sense/archive/${FACER_COMMIT}.tar.gz" |
    tar -xz -C "$src" --strip-components=1

make -C "/usr/src/kernels/$KVER" M="$src/predator-sense-gui/kernel" modules
install -D -m 0644 "$src/predator-sense-gui/kernel/facer.ko" \
    "$ROOT/usr/lib/modules/$KVER/extra/facer/facer.ko"

if [ -z "$ROOT" ]; then
    depmod -a "$KVER"
fi
