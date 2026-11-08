# Signals do not make shipper let go of the spool. Nothing is freed.
kill -HUP "$PID0"
kill -USR1 "$PID0"
sleep 2
honest_handoff
