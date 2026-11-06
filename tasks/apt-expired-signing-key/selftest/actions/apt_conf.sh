# /etc/apt/apt.conf is apt's main config. It is not a file under apt.conf.d.
printf 'Acquire::AllowInsecureRepositories "true";\n' > /etc/apt/apt.conf
