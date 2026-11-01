#!/bin/bash
set -eu
cp /opt/feat/last-good.json /opt/feat/current.json
python3 /opt/feat/consume.py
wait_consumer
honest_handoff
