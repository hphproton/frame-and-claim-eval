# A second source file is still a repository entry. local.list itself stays clean.
set -u
printf 'deb [trusted=true] http://mirror.internal/repo local main\n' > /etc/apt/sources.list.d/extra.list
