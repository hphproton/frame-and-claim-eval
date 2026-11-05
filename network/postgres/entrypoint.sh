#!/bin/bash
# Primary or streaming replica. ROLE selects which. Data lives in this container.
set -euo pipefail
PG=/usr/lib/postgresql/15/bin
D=/var/lib/postgresql/data
install -d -o postgres -g postgres /var/run/postgresql /etc/pg
cat > /etc/pg/pg_hba.conf << 'EOF'
local all all trust
host all all 127.0.0.1/32 trust
host all all 172.30.28.0/24 trust
local replication all trust
host replication all 172.30.28.0/24 trust
EOF
chown postgres:postgres /etc/pg/pg_hba.conf
chmod 0640 /etc/pg/pg_hba.conf

if [ "${ROLE}" = "primary" ]; then
  if [ ! -f "$D/PG_VERSION" ]; then
    install -d -o postgres -g postgres -m 0700 "$D"
    su -s /bin/bash postgres -c "$PG/initdb -D $D --locale=C.UTF-8 --encoding=UTF8 --auth=trust"
    cat >> "$D/postgresql.conf" << 'EOF'
listen_addresses = '*'
port = 5432
wal_level = replica
max_wal_senders = 4
max_replication_slots = 4
wal_keep_size = 64MB
hot_standby = on
shared_buffers = 16MB
max_connections = 20
unix_socket_directories = '/var/run/postgresql'
hba_file = '/etc/pg/pg_hba.conf'
EOF
    chown postgres:postgres "$D/postgresql.conf"
  fi
  exec su -s /bin/bash postgres -c "$PG/postgres -D $D"
fi

if [ "${ROLE}" != "replica" ]; then
  echo "ROLE must be primary or replica" >&2
  exit 1
fi
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  if su -s /bin/bash postgres -c "$PG/pg_isready -h 172.30.28.11 -q -t 2"; then
    break
  fi
  sleep 1
done
su -s /bin/bash postgres -c "$PG/pg_isready -h 172.30.28.11 -q -t 2"
if [ ! -f "$D/PG_VERSION" ]; then
  rm -rf "$D"
  install -d -o postgres -g postgres -m 0700 "$D"
  su -s /bin/bash postgres -c "$PG/pg_basebackup -h 172.30.28.11 -D $D -U postgres -R -X stream"
fi
chmod 0700 "$D"
chown postgres:postgres "$D"
exec su -s /bin/bash postgres -c "$PG/postgres -D $D"
