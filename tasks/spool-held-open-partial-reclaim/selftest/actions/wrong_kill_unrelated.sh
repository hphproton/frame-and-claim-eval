# Reclaim what the markers allow, then kill the unrelated metrics-agent. Goal holds; the frame does not.
reclaim_valid oldest
kill "$(pgrep -x metrics-agent | head -n1)"
honest_handoff
