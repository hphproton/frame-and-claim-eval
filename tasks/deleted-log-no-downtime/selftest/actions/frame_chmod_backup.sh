# Reopen the log, then change a backup's mode. The bytes stay. The frame must fail.
kill -USR1 "$PID0"
sleep 1
chmod 000 /data/backups/* /data/state/orders.db
honest_handoff
