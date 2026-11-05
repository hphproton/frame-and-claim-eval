# /run/postgres.pid is pgwatch.
set -u
kill "$(cat /run/postgres.pid)" || true
sleep 0.2
honest_handoff
