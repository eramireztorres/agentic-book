#!/usr/bin/env sh
set -eu

content_root="${AGENTIC_BOOK_CONTENT_ROOT:-/app/content}"
data_dir="${AGENTIC_BOOK_DATA_DIR:-/data}"

if [ "${AGENTIC_BOOK_AUTO_INGEST:-true}" = "true" ]; then
  agentic-book --content-root "$content_root" --data-dir "$data_dir" validate-content --strict-freshness >&2
  agentic-book --content-root "$content_root" --data-dir "$data_dir" ingest >&2
fi

exec "$@"
