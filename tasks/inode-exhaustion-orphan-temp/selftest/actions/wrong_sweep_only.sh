cat > /opt/sessions/sweep.sh << 'EOF'
#!/bin/sh
find /data/sessions/tmp -mindepth 1 -maxdepth 1 -type f -delete
EOF
honest_handoff
