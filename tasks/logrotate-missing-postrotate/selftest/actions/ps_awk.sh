# ps | awk finds the interpreter path. dash accepts kill -USR1.
cat > /etc/logrotate.d/reporter <<'EOF'
/var/log/reporter/current.log {
    rotate 1
    missingok
    notifempty
    postrotate
        kill -USR1 $(ps -eo pid=,args= | awk '$2=="python3" && $3=="/opt/reporter/reporter" {print $1}')
    endscript
}
EOF
