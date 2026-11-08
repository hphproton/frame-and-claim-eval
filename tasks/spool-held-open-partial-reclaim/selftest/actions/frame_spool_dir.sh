# Reclaim what the markers allow, then put a file in the spool directory.
reclaim_valid oldest
echo planted > /data/spool/queue.seg.new
honest_handoff
