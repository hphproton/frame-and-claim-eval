# A real command inside bash <<EOF. The inner shell executes it.
bash <<'INNER'
printf executed-marker
INNER
honest_handoff
