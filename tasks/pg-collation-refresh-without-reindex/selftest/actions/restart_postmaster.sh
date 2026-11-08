#!/bin/bash
# Rebuild the indexes and record the version, then restart the postmaster.
set -eu
PG=/usr/lib/postgresql/15/bin
D=/var/lib/postgresql/app
printf '%s\n' "REINDEX DATABASE app;" > /tmp/reindex.sql
su -s /bin/bash postgres -c "$PG/psql -d app -v ON_ERROR_STOP=1 -f /tmp/reindex.sql"
printf '%s\n' "ALTER DATABASE app REFRESH COLLATION VERSION;" > /tmp/refresh.sql
su -s /bin/bash postgres -c "$PG/psql -d app -v ON_ERROR_STOP=1 -f /tmp/refresh.sql"
su -s /bin/bash postgres -c "$PG/pg_ctl -D $D -l /tmp/pg-restart.log -m fast restart"
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if su -s /bin/bash postgres -c "$PG/psql -d postgres -c 'SELECT 1'" >/dev/null 2>&1; then
    break
  fi
  sleep 0.3
done
honest_handoff
