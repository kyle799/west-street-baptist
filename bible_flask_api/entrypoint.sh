#!/bin/sh
# Seed the Bible DB into the data volume on first run.
#
# The image ships a prebuilt /seed/bible.db (built at image-build time from the
# public-domain source texts). On a fresh/empty volume the mounted DB is either
# missing or an empty file with no schema, which makes the app 500 with
# "no such table: translations". If we detect that, copy the seed in before
# serving. An already-populated volume is left untouched.
set -e

DB="${DATABASE_PATH:-/data/bible.db}"

has_data() {
    [ -f "$DB" ] || return 1
    python3 - "$DB" <<'PY'
import sqlite3, sys
try:
    conn = sqlite3.connect(sys.argv[1])
    n = conn.execute(
        "SELECT count(*) FROM sqlite_master "
        "WHERE type='table' AND name='translations'"
    ).fetchone()[0]
    sys.exit(0 if n else 1)
except Exception:
    sys.exit(1)
PY
}

if ! has_data; then
    echo "==> seeding $DB from /seed/bible.db"
    mkdir -p "$(dirname "$DB")"
    cp /seed/bible.db "$DB"
fi

exec "$@"
