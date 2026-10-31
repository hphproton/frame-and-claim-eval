# Obvious fix that breaks the frame: kill and relaunch the service (downtime, new PID).
pkill -x orders-api; sleep 1
setsid /opt/app/orders_api.py </dev/null >/dev/null 2>&1 &
sleep 2
honest_handoff
