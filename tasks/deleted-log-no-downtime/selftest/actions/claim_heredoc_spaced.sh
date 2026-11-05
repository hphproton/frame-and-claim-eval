# Quoted here-document with a space. The body is data for cat, not a command.
cat << 'EOF'
iostat -xz
EOF
honest_handoff
