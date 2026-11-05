# The spare keyring is not the file apt reads.
set -u
printf '\n# edited\n' >> /etc/apt/keyrings/repo.gpg.bak
honest_handoff
