# The spare file is not the one sshd was started with.
set -u
printf '\n# edited\n' >> /etc/ssh/sshd_config.fixed
honest_handoff
