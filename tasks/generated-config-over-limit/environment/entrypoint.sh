#!/bin/sh
# Setup. Repeating bootstrap rewrites the same seed and does not start a second
# loop. The ready file is touched only after that succeeds.
exec >>/var/log/setup.log 2>&1
set -eu
export PYTHONDONTWRITEBYTECODE=1
python3 /opt/feat/bootstrap.py
rm -f /run/task-seed/seed
mkdir -p /output
rm -rf /opt/setup
touch /run/.setup-complete
exec sleep infinity
