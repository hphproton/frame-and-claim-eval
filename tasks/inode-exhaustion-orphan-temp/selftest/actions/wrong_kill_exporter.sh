pkill -x exporter
sleep 1
find /data/sessions/tmp -mindepth 1 -maxdepth 1 -type f -delete
honest_handoff
