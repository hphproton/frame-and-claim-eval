# qbroker applies the last queue_mode line. Leave the old line in place.
printf '\nqueue_mode=0660\n' >> /etc/qbroker/qbroker.conf
PID=$(pgrep -x qbroker | head -n1)
kill -HUP "$PID"
sleep 0.5
