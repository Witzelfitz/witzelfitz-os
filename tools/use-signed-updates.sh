#!/bin/bash
# Verify a published image and stage it; the caller decides when to reboot.
set -euo pipefail

repo=$(dirname "$(dirname "$(readlink -f "$0")")")
registry=ghcr.io/witzelfitz/witzelfitz-os
target=${1:-$registry:latest}
if [[ ! "$target" =~ ^ghcr\.io/witzelfitz/witzelfitz-os(:[a-zA-Z0-9_.-]+|@sha256:[a-f0-9]{64})$ ]]; then
    echo 'Nur ein Tag oder Digest des eigenen OS-Repositorys ist erlaubt.' >&2
    exit 1
fi
if [ "$(id -u)" -ne 0 ]; then
    echo "Als normaler Benutzer mit sudo starten: sudo $0 $target" >&2
    exit 1
fi
for executable in skopeo cosign jq rpm-ostree ostree bootc; do
    command -v "$executable" >/dev/null
done
cmp "$repo/cosign.pub" "$repo/system_files/etc/pki/containers/witzelfitz-os.pub"
status=$(rpm-ostree status --json)
booted_index=$(jq -er '
    if any(.deployments[]; .staged == true) then
        error("Ein Deployment wartet bereits auf den Neustart; nicht ersetzen.")
    else .deployments | to_entries | map(select(.value.booted == true)) |
        if length == 1 then .[0].key else error("Kein eindeutiges laufendes Deployment.") end
    end' <<< "$status")
metadata=$(skopeo inspect --no-tags "docker://$target")
digest=$(jq -er '.Digest | select(test("^sha256:[a-f0-9]{64}$"))' <<< "$metadata")
ref="$registry@$digest"
# Inspect the immutable reference too: a moving tag must not mix metadata
# from one image with the verified digest of another image.
metadata=$(skopeo inspect --no-tags "docker://$ref")
jq -e '.Labels["org.opencontainers.image.source"] == "https://github.com/Witzelfitz/witzelfitz-os"' \
    <<< "$metadata" >/dev/null
cosign verify --key "$repo/cosign.pub" "$ref" >/dev/null
echo "Signatur geprüft: $ref"
jq '{revision: .Labels["org.opencontainers.image.revision"], kernel: .Labels["ostree.linux"], version: .Labels["org.opencontainers.image.version"]}' <<< "$metadata"

# Preserve existing policy entries. Installation is only reached after all
# read-only preflight checks and the signature verification have succeeded.
policy=$(mktemp)
trap 'rm -f "$policy"' EXIT
jq '.transports.docker["ghcr.io/witzelfitz/witzelfitz-os"] = [{
    "type": "sigstoreSigned",
    "keyPath": "/etc/pki/containers/witzelfitz-os.pub",
    "signedIdentity": {"type": "matchRepository"}
}]' /etc/containers/policy.json > "$policy"
install -D -m 0644 "$repo/cosign.pub" /etc/pki/containers/witzelfitz-os.pub
install -D -m 0644 "$repo/system_files/etc/containers/registries.d/witzelfitz-os.yaml" \
    /etc/containers/registries.d/witzelfitz-os.yaml
install -m 0644 "$policy" /etc/containers/policy.json
ostree admin pin "$booted_index"
# Bootc independently verifies the downloaded image against the installed
# policy. Using latest restores registry updates; a digest deliberately pins it.
bootc switch --enforce-container-sigpolicy "$target"
rpm-ostree status
echo 'Signiertes Update bereitgestellt. Neustart selbst auslösen: systemctl reboot'
