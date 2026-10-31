set -u
sed -i 's/^queue_mode=.*/queue_mode=0660/' /etc/qbroker/qbroker.conf
kill -HUP "$(pgrep -x qbroker)"
sleep 0.4
rm -f /var/lib/qbroker/queue.db
honest_handoff
