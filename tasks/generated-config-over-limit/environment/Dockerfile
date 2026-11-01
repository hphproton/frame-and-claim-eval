# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# Apt package versions are intentionally not pinned.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
# tmux is installed here and the tmux server is not started.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 tini procps lsof psmisc less tmux ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY feat/ /opt/feat/
COPY entrypoint.sh /opt/setup/entrypoint.sh
RUN chmod 0755 /opt/setup/entrypoint.sh /opt/feat/bootstrap.py /opt/feat/generate.py \
      /opt/feat/consume.py /opt/feat/loop.py \
 && mkdir -p /output /var/log
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/setup/entrypoint.sh"]
