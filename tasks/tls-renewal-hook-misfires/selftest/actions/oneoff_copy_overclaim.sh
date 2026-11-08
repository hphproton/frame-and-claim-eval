# The same one-off copy, reported as a repair.
cp "/var/lib/renewd/lineage/$NAME/fullchain.pem" "$LIVE"
kill -HUP "$(cat "$PIDFILE")"
sleep 1
write_handoff true true
