# Terminus leaves these behind. They are on the frame ignore list.
mkdir -p /tmp/tmux-0 /logs/agent
printf 'socket\n' > /tmp/tmux-0/default
printf 'paste\n' > /tmp/.runtime-tmux-paste-abc
printf 'stamp\n' > /tmp/get-asciinema-timestamp.sh
printf 'pane\n' > /logs/agent/terminus_2.pane
