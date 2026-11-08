# Copy the certificate the loop already fetched into place once and signal webd. The loop is left as it was.
cp "/var/lib/renewd/lineage/$NAME/fullchain.pem" "$LIVE"
kill -HUP "$(cat "$PIDFILE")"
sleep 1
write_handoff false false
