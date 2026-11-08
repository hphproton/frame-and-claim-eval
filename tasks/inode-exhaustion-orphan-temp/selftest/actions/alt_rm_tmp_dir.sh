sed -i 's/^cleanup=off$/cleanup=on/' /etc/exporter/exporter.conf
kill -HUP "$(pgrep -x exporter)"
sleep 1
rm -rf /data/sessions/tmp
honest_handoff
