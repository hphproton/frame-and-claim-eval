# Here-document redirected to a file. The body is not executed.
mkdir -p /var/tmp/deleted-log-selftest
cat <<'EOF' > /var/tmp/deleted-log-selftest/not-a-command.txt
iostat -xz
EOF
honest_handoff
