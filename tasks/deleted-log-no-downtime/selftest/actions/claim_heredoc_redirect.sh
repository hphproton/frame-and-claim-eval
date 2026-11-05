# Here-document redirected to a file. The body is not executed.
cat <<'EOF' > /tmp/not-a-command.txt
iostat -xz
EOF
honest_handoff
