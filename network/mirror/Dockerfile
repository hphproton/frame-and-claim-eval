# Base image pinned by digest (debian:bookworm-slim, pulled 2026-10-31).
# ForceIPv4: the builder's IPv6 path to deb.debian.org does not answer.
FROM docker.io/library/debian@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
RUN printf 'Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99force-ipv4 \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 gnupg \
 && rm -rf /var/lib/apt/lists/*
COPY build_repo.sh /opt/build_repo.sh
RUN chmod 0755 /opt/build_repo.sh && /opt/build_repo.sh
EXPOSE 80
ENTRYPOINT ["python3", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "/srv"]
