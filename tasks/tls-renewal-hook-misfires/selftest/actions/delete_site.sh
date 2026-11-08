# Repair the hook and renew, then delete the pages webd serves.
fix_hook
/opt/renewd/renew --force
sleep 1
rm -rf /srv/webd/site
write_handoff true false
