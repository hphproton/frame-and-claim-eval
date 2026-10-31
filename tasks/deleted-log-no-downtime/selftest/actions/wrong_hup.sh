# Common wrong fix: SIGHUP (reload) does not reopen the log in this service; space stays held.
kill -HUP "$PID0"
honest_handoff
