# The signal is in a stanza logrotate does not run for current.log.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/other.log {
    postrotate
        kill -USR1 "$(pgrep -x reporter)" || true
    endscript
}
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
}
EOF
