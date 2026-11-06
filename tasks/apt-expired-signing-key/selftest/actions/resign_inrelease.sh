# Put the expired key back after a correct install.
set -u
cp /etc/apt/keyrings/repo.gpg.bak /etc/apt/keyrings/repo.gpg
