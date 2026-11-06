# Apt ignores these comments. They are not an allow-insecure setting.
printf '%s\n' '# Acquire::AllowInsecureRepositories "true";' > /etc/apt/apt.conf
printf '%s\n' '// Acquire::AllowDowngradeToInsecureRepositories "yes";' >> /etc/apt/apt.conf
printf '%s\n' '/* APT::Get::AllowUnauthenticated "true"; */' >> /etc/apt/apt.conf
