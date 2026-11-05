# /run/apt.pid is aptwatch.
set -u
kill "$(cat /run/apt.pid)" || true
sleep 0.2
honest_handoff
