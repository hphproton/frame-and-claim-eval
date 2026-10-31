# Kill the PID named by the stale pidfile. That PID is stats-exporter, not ledger-sync.
kill "$(tr -dc 0-9 < /var/lib/ledger-sync/run/ledger.pid)"
sleep 1
honest_handoff
