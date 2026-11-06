# The same pipeline with the SIG prefix dash rejects.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        kill -s SIGUSR1 $(ps -eo pid=,args= | awk '$2=="python3" && $3=="/opt/reporter/reporter" {print $1}')
    endscript
}
EOF
