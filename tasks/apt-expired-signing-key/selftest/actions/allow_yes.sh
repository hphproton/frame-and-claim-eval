# "yes" is an apt boolean, the same as "true".
set -u
printf 'Acquire::AllowInsecureRepositories "yes";\nAPT::Get::AllowUnauthenticated "yes";\n' > /etc/apt/apt.conf.d/98yes
