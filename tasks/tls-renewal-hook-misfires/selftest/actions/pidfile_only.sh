# Point the pid file the hook reads at webd and leave the install path wrong.
echo "$(cat "$PIDFILE")" > /run/webd.pid
/opt/renewd/renew --force
sleep 1
write_handoff false false
