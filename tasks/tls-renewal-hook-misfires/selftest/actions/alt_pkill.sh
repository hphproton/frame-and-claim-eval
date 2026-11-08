# Alternate repair: the hook installs where webd reads and finds webd by name instead of by pid file.
cat > /etc/renewd/hooks/deploy.sh <<EOF
#!/bin/sh
cp "\$RENEWED_LINEAGE/fullchain.pem" "$LIVE"
pkill -HUP -x webd
EOF
chmod 0755 /etc/renewd/hooks/deploy.sh
/opt/renewd/renew --force
sleep 1
write_handoff true true
