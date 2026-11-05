# The pidfile names metrics. Signalling it does not start payd.
set -u
kill -HUP "$(cat /run/ready/supervise.pid)" || true
sleep 0.3
honest_handoff
