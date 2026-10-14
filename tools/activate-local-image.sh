#!/bin/bash
# Stage the verified local image for the next boot; never reboot automatically.
set -euo pipefail

repo=$(dirname "$(dirname "$(readlink -f "$0")")")
image_dir="$repo/output/witzelfitz-public-oci"

if [ "$(id -u)" -ne 0 ]; then
    echo "Mit Root-Rechten starten: sudo $0" >&2
    exit 1
fi
test -f "$image_dir/index.json"
test -f "$repo/output/witzelfitz-public-oci.sha256"

# Check the exact exported layout before allowing bootc to import it.
(cd "$image_dir" && sha256sum --strict --check "$repo/output/witzelfitz-public-oci.sha256" >/dev/null)
status=$(rpm-ostree status --json)
booted_index=$(python3 -c '
import json, sys
deployments = json.load(sys.stdin)["deployments"]
if any(d.get("staged") for d in deployments):
    sys.exit("Ein Deployment wartet bereits auf den Neustart. Zuerst rpm-ostree status prüfen.")
print(next(i for i, d in enumerate(deployments) if d.get("booted")))
' <<< "$status")

# Keep the running, signed deployment available as a rollback.
ostree admin pin "$booted_index"
bootc switch --transport oci --retain "$image_dir"
rpm-ostree status
echo "Neues Image ist für den nächsten Neustart bereitgestellt."
echo "Nach dem Neustart: plymouth-set-default-theme  # erwartet: witzelfitz"
echo "Das Test-Deployment folgt dem lokalen OCI-Image. Nach Veröffentlichung"
echo "zurück zu signierten GHCR-Updates:"
echo "sudo bootc switch --enforce-container-sigpolicy ghcr.io/witzelfitz/witzelfitz-os:latest"
