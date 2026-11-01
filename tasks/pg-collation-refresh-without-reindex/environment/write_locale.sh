#!/bin/bash
# Usage: write_locale.sh normal|swap
# iso14651_t1 orders letters as <S0061> and <S0062>. <a> and <b> are not those
# symbols: localedef -c accepts them and strcoll does not change.
set -eu
mode="${1:?normal or swap}"
dest=/usr/share/i18n/locales/en_CUSTOM
cat > "$dest" << 'EOF'
escape_char /
comment_char %
LC_IDENTIFICATION
title "custom collation prototype"
source ""
address ""
contact ""
email ""
tel ""
fax ""
language "en"
territory "US"
revision "1.0"
date "2026-11-01"
END LC_IDENTIFICATION
LC_CTYPE
copy "en_US"
END LC_CTYPE
LC_COLLATE
copy "iso14651_t1"
EOF
if [ "$mode" = "swap" ]; then
  cat >> "$dest" << 'EOF'
reorder-after <S0062>
<S0061>
reorder-end
EOF
elif [ "$mode" != "normal" ]; then
  echo "unknown mode: $mode" >&2
  exit 1
fi
cat >> "$dest" << 'EOF'
END LC_COLLATE
LC_MONETARY
copy "en_US"
END LC_MONETARY
LC_NUMERIC
copy "en_US"
END LC_NUMERIC
LC_TIME
copy "en_US"
END LC_TIME
LC_MESSAGES
copy "en_US"
END LC_MESSAGES
LC_PAPER
copy "en_US"
END LC_PAPER
LC_NAME
copy "en_US"
END LC_NAME
LC_ADDRESS
copy "en_US"
END LC_ADDRESS
LC_TELEPHONE
copy "en_US"
END LC_TELEPHONE
LC_MEASUREMENT
copy "en_US"
END LC_MEASUREMENT
EOF
localedef --no-archive -c -i en_CUSTOM -f UTF-8 en_CUSTOM.UTF-8
first=$(python3 -c 'import locale; locale.setlocale(locale.LC_ALL, "en_CUSTOM.UTF-8"); print(sorted(["a", "b"], key=locale.strxfrm)[0])')
if [ "$mode" = "normal" ] && [ "$first" != "a" ]; then
  echo "normal locale still sorts $first first" >&2
  exit 1
fi
if [ "$mode" = "swap" ] && [ "$first" != "b" ]; then
  echo "swapped locale still sorts $first first" >&2
  exit 1
fi
echo "locale $mode first=$first"
