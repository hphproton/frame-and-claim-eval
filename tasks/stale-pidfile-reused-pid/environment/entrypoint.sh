#!/bin/sh
python3 /opt/setup/setup.py >/var/log/setup.log 2>&1 || echo "setup failed" >>/var/log/setup.log
rm -rf /opt/setup
exec sleep infinity
