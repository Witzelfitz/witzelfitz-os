#!/bin/bash
# Read-only check inside the built OS image; does not start Plymouth.
set -euo pipefail

test "$(plymouth-set-default-theme)" = witzelfitz
test -f /usr/lib64/plymouth/script.so
kernels=(/usr/lib/modules/*)
if [ "${#kernels[@]}" -ne 1 ] || [ ! -d "${kernels[0]}" ]; then
    echo 'Expected exactly one kernel in the OS image.' >&2
    exit 1
fi
initramfs="${kernels[0]}/initramfs.img"
test -s "$initramfs"
listing=$(lsinitrd "$initramfs")
for name in witzelfitz.plymouth witzelfitz.script background.png title.png glow.png dot.png drop.png; do
    test -s "/usr/share/plymouth/themes/witzelfitz/$name"
    if ! grep -Fq "usr/share/plymouth/themes/witzelfitz/$name" <<< "$listing"; then
        echo "Boot theme asset missing from initramfs: $name" >&2
        exit 1
    fi
done
grep -Fq 'usr/lib64/plymouth/script.so' <<< "$listing"
grep -Eq ' root -> (\./)?var/roothome$' <<< "$listing"
grep -Eq ' var/roothome/?$' <<< "$listing"
echo 'Plymouth theme, script renderer and boot assets included in initramfs.'
