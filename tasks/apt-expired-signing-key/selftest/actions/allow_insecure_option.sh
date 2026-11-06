# allow-insecure=yes is a source option. It is not trusted=yes.
sed -i 's/deb \[/deb [allow-insecure=yes /' /etc/apt/sources.list.d/local.list
