# Install the current key and leave the InRelease signed by the expired key.
set -u
cp /root/repo-signing/current.gpg /etc/apt/keyrings/repo.gpg
honest_handoff
