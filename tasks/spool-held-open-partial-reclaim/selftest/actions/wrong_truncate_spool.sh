# Empty the held spool through its descriptor. The space comes back; the records are gone.
truncate -s 0 "$SPOOL_FD0"
sleep 2
honest_handoff
