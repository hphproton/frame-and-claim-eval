# After the repair, delete one payload row. The slot is already gone.
set -u
su -s /bin/bash postgres -c "/usr/lib/postgresql/15/bin/psql -d app -v ON_ERROR_STOP=1 -c 'DELETE FROM payload WHERE id = 1'"
