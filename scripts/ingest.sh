#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
agentic_book="$repo_root/.venv/bin/agentic-book"

if [ ! -x "$agentic_book" ]; then
  echo "ERROR: no existe $agentic_book." >&2
  echo "Ejecuta primero ./scripts/setup.sh desde la carpeta agentic-book." >&2
  exit 1
fi

echo "Validando el contenido curado..."
"$agentic_book" --content-root "$repo_root/content" validate-content --strict-freshness

echo "Construyendo el índice local..."
"$agentic_book" --content-root "$repo_root/content" --data-dir "$repo_root/.agentic-book-data" ingest

echo "Comprobando una recuperación completa..."
"$agentic_book" --data-dir "$repo_root/.agentic-book-data" get-document playbook.sql-agent-enterprise >/dev/null

echo
echo "Índice local preparado correctamente."
echo "Índice local: $repo_root/.agentic-book-data"
