# Punch the whole held spool out. The size stays, the bytes become zeros, the pages are freed.
SIZE=$(stat -L -c %s "$SPOOL_FD0")
fallocate --punch-hole --keep-size --offset 0 --length "$SIZE" "$SPOOL_FD0"
sleep 2
honest_handoff
