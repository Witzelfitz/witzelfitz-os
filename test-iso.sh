#!/bin/bash
# Startet das neueste ISO aus output/ in einer VM: UEFI, leere 40-GB-Disk,
# KEIN Netzwerk. Haengt niemals eine echte Disk an.
# Aufruf im Repo-Verzeichnis: sudo ./test-iso.sh            (Fenster)
#                             sudo ./test-iso.sh --headless (QMP-Socket, fuer Screenshots)
# Zum Booten der installierten Disk ohne ISO:  sudo ./test-iso.sh --disk

set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

VM=output/vm
mkdir -p "$VM"

ISO="$(ls -t output/*.iso 2>/dev/null | head -n1 || true)"
MODE="gui"
BOOT_ISO=1
for a in "$@"; do
    case "$a" in
        --headless) MODE="headless" ;;
        --disk) BOOT_ISO=0 ;;
        *) echo "Unbekannte Option: $a" >&2; exit 1 ;;
    esac
done

if [ "$BOOT_ISO" -eq 1 ] && [ -z "$ISO" ]; then
    echo "Kein ISO in output/. Zuerst sudo ./make-iso.sh ausfuehren." >&2
    exit 1
fi

CODE=""
for c in /usr/share/edk2/ovmf/OVMF_CODE.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/OVMF/OVMF_CODE_4M.fd; do
    [ -f "$c" ] && CODE="$c" && break
done
[ -n "$CODE" ] || { echo "OVMF nicht gefunden (Paket edk2-ovmf bzw. ovmf)" >&2; exit 1; }
VARS_SRC="${CODE/CODE/VARS}"

[ -f "$VM/disk.qcow2" ] || qemu-img create -f qcow2 "$VM/disk.qcow2" 40G
[ -f "$VM/vars.fd" ] || cp "$VARS_SRC" "$VM/vars.fd"

ARGS=(
    -machine q35,accel=kvm -cpu host -smp 4 -m 8G
    -drive if=pflash,format=raw,readonly=on,file="$CODE"
    -drive if=pflash,format=raw,file="$VM/vars.fd"
    -drive if=virtio,format=qcow2,file="$VM/disk.qcow2"
    -nic none
    -vga std
    -usb -device usb-tablet
)
if [ "$BOOT_ISO" -eq 1 ]; then
    echo "ISO: $ISO"
    ARGS+=(-drive media=cdrom,readonly=on,file="$ISO" -boot once=d)
fi

if [ "$MODE" = "headless" ]; then
    ARGS+=(-display none -qmp unix:"$VM/qmp.sock",server=on,wait=off -daemonize -pidfile "$VM/qemu.pid")
    qemu-system-x86_64 "${ARGS[@]}"
    echo "VM laeuft im Hintergrund (PID $(cat "$VM/qemu.pid")), QMP: $VM/qmp.sock"
else
    qemu-system-x86_64 "${ARGS[@]}" -display gtk
fi
