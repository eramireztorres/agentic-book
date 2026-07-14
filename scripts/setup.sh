#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_dir="$repo_root/.venv"

find_python() {
  local candidate
  for candidate in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

if ! python_command="$(find_python)"; then
  echo "ERROR: se necesita Python 3.11 o superior para la instalación nativa." >&2
  echo "Instálalo desde https://www.python.org/downloads/ o usa la vía Docker descrita en README.md." >&2
  exit 1
fi

if [ -x "$venv_dir/bin/python" ]; then
  if ! "$venv_dir/bin/python" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
    echo "ERROR: .venv existe, pero usa una versión de Python anterior a 3.11." >&2
    echo "Renombra o elimina .venv y vuelve a ejecutar este script." >&2
    exit 1
  fi
else
  echo "Creando el entorno virtual con $python_command..."
  "$python_command" -m venv "$venv_dir"
fi

venv_python="$venv_dir/bin/python"
agentic_book="$venv_dir/bin/agentic-book"

echo "Instalando Agentic Book y el servidor MCP..."
"$venv_python" -m pip install -e "$repo_root[mcp]"

"$agentic_book" --help >/dev/null

echo
echo "Instalación completada correctamente."
echo "Ejecutable MCP: $agentic_book"
echo "Siguiente paso: ./scripts/ingest.sh"
