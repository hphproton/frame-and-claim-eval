#!/bin/sh
exec python3 -c '
import os, sys
s = os.statvfs("/spool")
if s.f_favail < 80:
    sys.exit(1)
p = "/spool/spill/.health-probe"
try:
    fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    os.close(fd)
    os.unlink(p)
except OSError:
    sys.exit(1)
'
