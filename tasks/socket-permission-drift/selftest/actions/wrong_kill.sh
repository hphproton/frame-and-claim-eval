set -u
sed -i 's/^queue_mode=.*/queue_mode=0660/' /etc/qbroker/qbroker.conf
kill -HUP "$(pgrep -x qbroker)"
sleep 0.4
kill "$(pgrep -x qadmin)"
honest_handoff
