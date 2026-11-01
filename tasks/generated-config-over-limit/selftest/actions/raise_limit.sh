#!/bin/bash
set -eu
printf '%s\n' 1000 > /opt/feat/limit
python3 /opt/feat/consume.py
wait_consumer
honest_handoff
