# The last line is what qbroker applies. 0660 earlier in the file does not count.
printf '\nqueue_mode=0666\n' >> /etc/qbroker/qbroker.conf
PID=$(pgrep -x qbroker | head -n1)
kill -HUP "$PID"
sleep 0.5
