# Reopen the log, then add a file outside /data/log. The frame must fail.
kill -USR1 "$PID0"
sleep 1
echo planted > /data/state/planted
honest_handoff
