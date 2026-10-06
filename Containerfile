# Build-Skripte einbinden, ohne sie ins fertige Image zu kopieren
FROM scratch AS ctx
COPY build_files /
COPY system_files /system_files

# Basis: Bazzite Developer Edition, KDE Plasma, aktueller Nvidia-Treiber
# (passt zur RTX 2060; fuer GTX 900/1000 waere es das Legacy-Image)
FROM ghcr.io/ublue-os/bazzite-dx-nvidia:stable

# Alle Anpassungen passieren in build_files/build.sh
RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    /ctx/build.sh

# Prueft, ob das fertige Image ein gueltiges bootc-Image ist
RUN bootc container lint
