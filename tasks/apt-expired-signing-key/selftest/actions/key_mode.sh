# Root can read the key. The apt sandbox user cannot.
set -u
chmod 0600 /etc/apt/keyrings/repo.gpg
