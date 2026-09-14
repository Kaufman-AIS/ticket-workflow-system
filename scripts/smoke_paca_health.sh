#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-https://paca.kaufman-ais.com}"
code=$(curl -sS -o /tmp/paca_smoke_body.html -w "%{http_code}" "$BASE_URL/")
echo "HTTP $code for $BASE_URL/"
test "$code" = "200" -o "$code" = "302" -o "$code" = "301"
grep -qi "html\|paca\|login\|sign" /tmp/paca_smoke_body.html
echo "OK health smoke"
