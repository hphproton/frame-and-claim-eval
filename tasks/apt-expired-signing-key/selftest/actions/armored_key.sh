# An armored copy is not the keyring apt reads for this repository.
set -u
GNUPGHOME=$(mktemp -d)
export GNUPGHOME
chmod 700 "$GNUPGHOME"
gpg --batch --import /etc/apt/keyrings/repo.gpg >/dev/null
gpg --batch --armor --export > /etc/apt/keyrings/repo.gpg
rm -rf "$GNUPGHOME"
