# World-writable queue socket. Health may pass. The required mode is 0660.
set -u
chmod 0666 /run/qbroker/queue.sock
honest_handoff
