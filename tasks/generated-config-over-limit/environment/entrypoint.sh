#!/bin/sh
# Incident setup. Repeating bootstrap rewrites the same seed and does not
# start a second loop. The ready file is touched only after that succeeds.
exec >>/var/log/setup.log 2>&1
set -eu
export PYTHONDONTWRITEBYTECODE=1
python3 /opt/feat/bootstrap.py
mkdir -p /output
touch /run/.setup-complete
exec sleep infinity
