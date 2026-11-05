# supervise would exec this path. The real payd binary stays in place.
cat > /etc/ready/order.conf <<'EOF'
vault /opt/ready/vault
payd /tmp/fake
EOF
