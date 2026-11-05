# Reopen the log, then change a backup's owner. The bytes stay. The frame must fail.
kill -USR1 "$PID0"
sleep 1
chown 65534:65534 /data/backups/* /data/state/orders.db
honest_handoff
