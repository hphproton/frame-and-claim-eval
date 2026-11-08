#!/bin/sh
# Exit 0 only if shipper reported a successful batch write in the last 3 seconds.
exec python3 - <<'PY'
import json, sys, time
try:
    s = json.load(open("/run/shipper/status.json"))
except Exception as e:
    print(f"UNHEALTHY: no status ({e})"); sys.exit(1)
age = time.time() - s.get("ts", 0)
if age > 3:
    print(f"UNHEALTHY: status is {age:.1f}s old"); sys.exit(1)
if not s.get("write_ok"):
    print(f"UNHEALTHY: last_error={s.get('last_error')}"); sys.exit(1)
print("OK"); sys.exit(0)
PY
