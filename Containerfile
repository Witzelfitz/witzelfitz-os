# Build-Skripte einbinden, ohne sie ins fertige Image zu kopieren
FROM scratch AS ctx
COPY build_files /
COPY system_files /system_files

# Basis: Bazzite Developer Edition, KDE Plasma, aktueller Nvidia-Treiber
# (passt zur RTX 2060; fuer GTX 900/1000 waere es das Legacy-Image)
FROM ghcr.io/ublue-os/bazzite-dx-nvidia:stable

ARG SOURCE_REVISION=unknown
LABEL org.opencontainers.image.title="witzelfitz-os" \
      org.opencontainers.image.description="Linux fuer den Acer Predator PT515-51 auf Basis Bazzite DX" \
      org.opencontainers.image.url="https://github.com/Witzelfitz/witzelfitz-os" \
      org.opencontainers.image.source="https://github.com/Witzelfitz/witzelfitz-os" \
      org.opencontainers.image.documentation="https://github.com/Witzelfitz/witzelfitz-os/blob/main/README.md" \
      org.opencontainers.image.vendor="Witzelfitz" \
      org.opencontainers.image.authors="Witzelfitz" \
      org.opencontainers.image.revision="${SOURCE_REVISION}" \
      io.artifacthub.package.readme-url="https://raw.githubusercontent.com/Witzelfitz/witzelfitz-os/main/README.md"

# Alle Anpassungen passieren in build_files/build.sh
RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    /ctx/build.sh

# Prueft, ob das fertige Image ein gueltiges bootc-Image ist
RUN bootc container lint
