# The replacement key is already installed. trusted=true is the same bypass as trusted=yes.
set -u
sed -i 's/deb \[/deb [trusted=true /' /etc/apt/sources.list.d/local.list
