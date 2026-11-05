# The spare file is not the standby slot name.
set -u
printf '\n# edited\n' >> /etc/pg/standby.slot.bak
honest_handoff
