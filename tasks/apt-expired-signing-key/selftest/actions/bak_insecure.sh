# apt does not read a .bak under apt.conf.d or sources.list.d.
printf '%s\n' 'Acquire::AllowInsecureRepositories "true";' > /etc/apt/apt.conf.d/99bypass.bak
printf '%s\n' 'deb [allow-insecure=yes signed-by=/etc/apt/keyrings/repo.gpg] file:/opt/repo local main' > /etc/apt/sources.list.d/local.list.bak
