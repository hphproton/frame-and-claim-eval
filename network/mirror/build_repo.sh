#!/bin/bash
# Empty signed apt repository. The public key is published next to it.
set -euo pipefail
export GNUPGHOME=/tmp/repo-gnupg
rm -rf "$GNUPGHOME"
install -d -m 0700 "$GNUPGHOME"
cat > "$GNUPGHOME/gen.txt" << 'EOF'
%no-protection
Key-Type: eddsa
Key-Curve: ed25519
Name-Real: Local Mirror
Name-Email: mirror@internal
Expire-Date: 2035-01-01
%commit
EOF
gpg --batch --generate-key "$GNUPGHOME/gen.txt"
rm -f "$GNUPGHOME/gen.txt"
install -d /srv/repo/dists/local/main/binary-amd64 /srv
gpg --batch --export mirror@internal > /srv/key.gpg
chmod 0644 /srv/key.gpg
python3 - << 'PY'
import hashlib, os
root = "/srv/repo"
rel = "dists/local/main/binary-amd64/Packages"
path = os.path.join(root, rel)
open(path, "w").write("")
data = open(path, "rb").read()

def digest(name):
    return getattr(hashlib, name)(data).hexdigest()

lines = [
    "Origin: local",
    "Label: local",
    "Suite: local",
    "Codename: local",
    "Architectures: amd64",
    "Components: main",
    "Date: Thu, 01 Jan 2026 00:00:00 UTC",
    "Valid-Until: Tue, 01 Jan 2035 00:00:00 UTC",
    "MD5Sum:",
    f" {digest('md5')} {len(data)} {rel}",
    "SHA256:",
    f" {digest('sha256')} {len(data)} {rel}",
    "",
]
open(os.path.join(root, "dists/local/Release"), "w").write("\n".join(lines))
PY
gpg --batch --yes --local-user mirror@internal --clearsign \
  --output /srv/repo/dists/local/InRelease /srv/repo/dists/local/Release
rm -rf "$GNUPGHOME"
