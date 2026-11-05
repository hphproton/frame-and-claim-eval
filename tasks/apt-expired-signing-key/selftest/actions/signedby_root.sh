# Point signed-by at a key apt's sandbox user cannot read.
set -u
printf 'deb [signed-by=/root/repo-signing/current.gpg] file:/opt/repo local main\n' > /etc/apt/sources.list.d/local.list
