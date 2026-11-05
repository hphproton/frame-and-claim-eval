# pidof without -x matches the executable, which is python3, not the comm name.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        kill -USR1 "$(pidof reporter)" || true
    endscript
}
EOF
