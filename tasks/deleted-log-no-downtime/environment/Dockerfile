# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# Apt package versions are intentionally not pinned: a pin breaks when Debian drops
# that version (Terminal-Bench environment_hygiene). The image Created timestamp is
# recorded in each trial's meta.json.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 tini procps lsof psmisc less \
 && rm -rf /var/lib/apt/lists/*
COPY files/orders_api.py /opt/app/orders_api.py
COPY files/metrics-agent /opt/app/metrics-agent
COPY files/health.sh /opt/app/health.sh
COPY files/README.txt /opt/app/README.txt
COPY files/orders-api.conf /etc/orders-api/orders-api.conf
COPY setup.py /opt/setup/setup.py
COPY entrypoint.sh /opt/setup/entrypoint.sh
RUN chmod 0755 /opt/app/orders_api.py /opt/app/metrics-agent /opt/app/health.sh /opt/setup/entrypoint.sh && mkdir -p /output
# /data is a 64 MiB tmpfs declared in docker-compose.yaml, not as a docker run argument.
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/setup/entrypoint.sh"]
