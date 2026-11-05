# The pidfile names sshwatch. Signalling it does not reload sshd.
set -u
kill -HUP "$(cat /run/sshd.pid)" || true
sleep 0.3
honest_handoff
