# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# Apt package versions are intentionally not pinned.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
# tmux is installed here and the tmux server is not started.
# The runner snapshots the baseline first, then Terminus starts the session.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      postgresql postgresql-contrib locales python3 ca-certificates \
      tini procps lsof psmisc less tmux \
 && rm -rf /var/lib/apt/lists/*
COPY build_cluster.sh entrypoint.sh /opt/setup/
COPY files/pgwatch /opt/pg/pgwatch
COPY files/README.txt /opt/pg/README.txt
COPY files/health.sh /opt/pg/health.sh
RUN chmod 0755 /opt/setup/build_cluster.sh /opt/setup/entrypoint.sh /opt/pg/pgwatch /opt/pg/health.sh \
 && mkdir -p /output /var/log /etc/pg \
 && /opt/setup/build_cluster.sh
COPY setup.py /opt/setup/setup.py
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/setup/entrypoint.sh"]
