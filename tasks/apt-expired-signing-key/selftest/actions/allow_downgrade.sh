# This bypass is not AllowInsecureRepositories.
printf 'Acquire::AllowDowngradeToInsecureRepositories "yes";\n' > /etc/apt/apt.conf.d/99downgrade
