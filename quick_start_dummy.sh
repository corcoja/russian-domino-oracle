#!/bin/sh

set -eu

{
  cat <<'EOF'
2
1 0
0
11
14
24
26
45
55
56


7
EOF
  cat /dev/tty
} | ".venv/bin/python" "launch.py"
