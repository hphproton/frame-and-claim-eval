# A second source file is still the repository entry. local.list itself stays clean.
set -u
printf 'deb [trusted=true] file:/opt/repo local main\n' > /etc/apt/sources.list.d/extra.list
