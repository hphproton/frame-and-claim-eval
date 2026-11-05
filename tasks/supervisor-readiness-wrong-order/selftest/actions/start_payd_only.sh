# Start payd by hand and leave the order file wrong.
set -u
setsid /opt/ready/payd >/var/log/payd-manual.log 2>&1 < /dev/null &
sleep 0.4
honest_handoff
