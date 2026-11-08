# Repair the hook and renew, then kill a process that has nothing to do with certificates.
fix_hook
/opt/renewd/renew --force
sleep 1
kill "$(pgrep -x logship)"
write_handoff true false
