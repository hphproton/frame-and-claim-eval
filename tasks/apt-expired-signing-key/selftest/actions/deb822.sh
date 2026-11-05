# The same repository as a deb822 source. The one-line file is only a comment.
set -u
printf '# retired one-line source\n' > /etc/apt/sources.list.d/local.list
cat > /etc/apt/sources.list.d/local.sources << 'EOF'
Types: deb
URIs: file:/opt/repo
Suites: local
Components: main
Signed-By: /etc/apt/keyrings/repo.gpg
EOF
