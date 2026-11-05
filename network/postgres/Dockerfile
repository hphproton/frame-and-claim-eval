# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# ForceIPv4: the builder's IPv6 path to deb.debian.org does not answer.
# policy-rc.d 101: apt must not start the default cluster. The entrypoint does.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
RUN printf 'Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99force-ipv4 \
 && printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d && chmod 0755 /usr/sbin/policy-rc.d \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      postgresql python3 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 0755 /usr/local/bin/entrypoint.sh
ENV ROLE=primary
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
