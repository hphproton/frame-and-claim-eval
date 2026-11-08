kill -STOP "$(pgrep -x exporter)"
find /data/sessions/tmp -mindepth 1 -maxdepth 1 -type f -delete
honest_handoff
