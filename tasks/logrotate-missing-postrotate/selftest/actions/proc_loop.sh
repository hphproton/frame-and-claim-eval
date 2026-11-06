# /proc cmdline loop. dash accepts kill -USR1. The solution already reopened the live log.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        for pid in /proc/[0-9]*; do
            cmd=$(tr '\0' ' ' < "$pid/cmdline" 2>/dev/null || true)
            case "$cmd" in
                "python3 /opt/reporter/reporter"*)
                    kill -USR1 "${pid#/proc/}"
                    ;;
            esac
        done
    endscript
}
EOF
