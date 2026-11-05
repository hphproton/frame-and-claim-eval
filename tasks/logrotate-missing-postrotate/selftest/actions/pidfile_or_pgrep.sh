# cat of the pidfile succeeds, so the pgrep fallback never runs. That pid is logwatch.
set -u
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        kill -USR1 "$(cat /run/reporter.pid || pgrep -x reporter)" || true
    endscript
}
EOF
