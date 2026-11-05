#!/bin/sh
# Drop packets from the upstream bridge to the host. Container-to-container
# traffic is forwarded, not input, so the mirror, databases, and DNS stay open.
# Replies to connections the host itself opened are still accepted.
set -eu
DOCKER=${DOCKER:-docker}
id=$("$DOCKER" network inspect -f '{{.Id}}' micro1eval-upstream 2>/dev/null) || exit 0
bridge=br-$(printf '%s' "$id" | cut -c1-12)
if ! command -v iptables-legacy >/dev/null 2>&1 || ! command -v sudo >/dev/null 2>&1; then
  echo "iptables-legacy is required to block the bridge gateway" >&2
  exit 1
fi
sudo -n iptables-legacy -C INPUT -i "$bridge" -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null \
  || sudo -n iptables-legacy -I INPUT -i "$bridge" -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo -n iptables-legacy -C INPUT -i "$bridge" -j DROP 2>/dev/null \
  || sudo -n iptables-legacy -A INPUT -i "$bridge" -j DROP
