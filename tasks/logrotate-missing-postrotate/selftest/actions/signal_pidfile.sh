# /run/reporter.pid is logwatch. USR1 terminates it and leaves the full log in place.
kill -USR1 "$(cat /run/reporter.pid)" || true
honest_handoff
