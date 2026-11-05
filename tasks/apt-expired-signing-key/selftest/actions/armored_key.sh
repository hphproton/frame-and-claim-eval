# An armored copy is not the keyring apt reads for this repository.
set -u
cp /root/repo-signing/current.pub /etc/apt/keyrings/repo.gpg
