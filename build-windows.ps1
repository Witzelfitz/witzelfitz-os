# Baut witzelfitz-os unter Windows in einer WSL-2-Distribution (Fedora).
# Aufruf in PowerShell im Repo-Verzeichnis:
#   .\build-windows.ps1          Umgebung einrichten (einmalig) und ISO bauen
#   .\build-windows.ps1 -Test    zusaetzlich das ISO in einer VM starten
# Das ISO landet danach in .\output\ (auf der Windows-Seite).

param([switch]$Test)
$ErrorActionPreference = 'Stop'

$Distro = 'FedoraLinux-44'
$Work   = '/root/witzelfitz-os'

$installed = (wsl.exe -l -q) -replace "`0", '' | Where-Object { $_ -eq $Distro }
if (-not $installed) {
    Write-Host "==> WSL-Distribution $Distro installieren"
    wsl.exe --install $Distro --no-launch
}

function In-Wsl([string]$cmd) {
    wsl.exe -d $Distro -u root -e bash -euo pipefail -c $cmd
    if ($LASTEXITCODE -ne 0) { throw "Fehlgeschlagen in WSL: $cmd" }
}

Write-Host '==> Werkzeuge in WSL pruefen/installieren'
In-Wsl 'rpm -q podman qemu-system-x86-core qemu-img qemu-ui-gtk edk2-ovmf rsync >/dev/null || dnf5 install -y podman qemu-system-x86-core qemu-img qemu-ui-gtk edk2-ovmf rsync'

# Repo ins Linux-Dateisystem spiegeln: auf /mnt/c ist der Bau langsam
# und podman kann dort keine Rechte setzen.
$WinRepo = (wsl.exe -d $Distro -e wslpath -a ($PSScriptRoot -replace '\\', '/')).Trim()
Write-Host "==> Repo nach $Work spiegeln"
In-Wsl "mkdir -p $Work && rsync -a --delete --exclude output/ --exclude '_bib.*/' --exclude .git/ '$WinRepo/' $Work/"

Write-Host '==> ISO bauen (dauert lange)'
In-Wsl "cd $Work && ./make-iso.sh 2>&1 | tee build.log"

Write-Host '==> ISO nach Windows kopieren'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot 'output') | Out-Null
# dd statt cp: cp bricht beim Schreiben grosser Dateien nach /mnt/c
# unter Speicherdruck mit "Cannot allocate memory" ab.
In-Wsl "cd $Work/output && for f in *.iso; do dd if=`$f of='$WinRepo/output/'`$f bs=16M status=none; done && cp -f *.sha256 ../build.log '$WinRepo/output/' && cd '$WinRepo/output' && sha256sum -c *.sha256"
Get-ChildItem (Join-Path $PSScriptRoot 'output')

if ($Test) {
    Write-Host '==> ISO in VM starten (ohne Netzwerk, leere 40-GB-Disk)'
    In-Wsl "cd $Work && ./test-iso.sh"
}
