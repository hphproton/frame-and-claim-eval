#!/bin/sh
# Print the byte size of the submission zip this tree would produce.
# Does not write the zip into the repo. Excludes .git, gitignored files
# (.venv, __pycache__, *.pyc, .env), and anything never committed
# (images, caches, local wheels).
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$root" archive --format=zip --output="$tmp/submission.zip" HEAD
bytes=$(wc -c < "$tmp/submission.zip" | tr -d ' ')
echo "$bytes bytes ($tmp/submission.zip from HEAD)"
