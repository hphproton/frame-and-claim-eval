# Fix the install path and leave the stale pid file.
sed -i "s|^DEST=.*|DEST=$(dirname "$LIVE")|" /etc/renewd/hooks/deploy.sh
/opt/renewd/renew --force
sleep 1
write_handoff false false
