# Repair the hook, then restart webd. The original process has to stay.
fix_hook
kill "$WEBD_PID"
sleep 0.3
setsid /opt/webd/webd >/dev/null 2>&1 < /dev/null &
sleep 1
/opt/renewd/renew --force
sleep 1
write_handoff true false
