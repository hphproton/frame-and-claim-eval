# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# Apt package versions are intentionally not pinned.
# ForceIPv4: the builder's IPv6 path to deb.debian.org does not answer.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
RUN printf 'Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99force-ipv4 \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 gnupg apt-utils tini procps lsof psmisc less tmux ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/apt/sources.list \
 && rm -rf /etc/apt/sources.list.d \
 && mkdir -p /etc/apt/sources.list.d /etc/apt/keyrings /output /var/log /opt/apt
COPY build_repo.sh entrypoint.sh /opt/setup/
COPY files/aptwatch /opt/apt/aptwatch
COPY files/README.txt /opt/apt/README.txt
COPY files/health.sh /opt/apt/health.sh
RUN chmod 0755 /opt/setup/build_repo.sh /opt/setup/entrypoint.sh /opt/apt/aptwatch /opt/apt/health.sh \
 && /opt/setup/build_repo.sh
COPY setup.py /opt/setup/setup.py
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/setup/entrypoint.sh"]
