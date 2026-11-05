# Redirections are not pkill arguments. This script signals reporter.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        pkill -USR1 -x reporter >/dev/null 2>&1 || true
    endscript
}
EOF
