#!/bin/bash
# Build a cluster whose text indexes match the normal en_CUSTOM order.
# Re-running removes the data directory first, so the end state does not
# depend on a half-written cluster from an earlier run.
set -euo pipefail
PG=/usr/lib/postgresql/15/bin
D=/var/lib/postgresql/app
if su -s /bin/bash postgres -c "$PG/pg_ctl -D $D status" >/dev/null 2>&1; then
  su -s /bin/bash postgres -c "$PG/pg_ctl -D $D -m fast stop"
fi
rm -rf "$D"
install -d -o postgres -g postgres "$D"
/opt/setup/write_locale.sh normal
su -s /bin/bash postgres -c "$PG/initdb -D $D --locale=en_CUSTOM.UTF-8 --encoding=UTF8 --auth=trust"
cat >> "$D/postgresql.conf" << 'EOF'
shared_buffers = 16MB
max_connections = 20
EOF
su -s /bin/bash postgres -c "$PG/pg_ctl -D $D -l /tmp/pg-build.log start"
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if su -s /bin/bash postgres -c "$PG/psql -d postgres -c 'SELECT 1'" >/dev/null 2>&1; then
    break
  fi
  sleep 0.3
done
su -s /bin/bash postgres -c "$PG/psql -d postgres -v ON_ERROR_STOP=1 -c 'CREATE DATABASE app'"
su -s /bin/bash postgres -c "$PG/psql -d app -v ON_ERROR_STOP=1 -f /opt/setup/schema.sql"
su -s /bin/bash postgres -c "$PG/pg_ctl -D $D -m fast stop"
echo "cluster built under normal en_CUSTOM order"
