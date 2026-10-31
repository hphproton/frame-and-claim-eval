#!/bin/sh
exec python3 -c '
import json, sys
try:
    mode = json.load(open("/run/gate/status.json")).get("mode")
except Exception:
    sys.exit(1)
sys.exit(0 if mode == "open" else 1)
'
