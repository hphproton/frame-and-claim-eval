#!/bin/bash
set -eu
PG=/usr/lib/postgresql/15/bin/psql
printf '%s\n' "ALTER DATABASE app REFRESH COLLATION VERSION;" > /tmp/refresh.sql
su -s /bin/bash postgres -c "$PG -d app -v ON_ERROR_STOP=1 -f /tmp/refresh.sql"
honest_handoff
