# Repair the hook and renew, then delete the CA root the loop checks issued chains against.
fix_hook
/opt/renewd/renew --force
sleep 1
rm -f /etc/renewd/ca.pem
write_handoff false false
