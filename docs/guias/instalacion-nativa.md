# Instalación nativa de Agentic Book

La instalación nativa permite ejecutar el servidor MCP mediante STDIO y desarrollar el proyecto sin Docker. Requiere Git y Python 3.11 o superior. Python 3.11 y 3.13 se verifican en CI.

## Instalación automática

Desde la raíz del repositorio, ejecuta el script correspondiente. No necesitas activar el entorno virtual.

Linux o macOS:

```bash
./scripts/setup.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Estos scripts solo instalan: buscan un Python compatible, crean `.venv` si hace falta e instalan `.[mcp]`. En Linux/macOS prueban `python3.13`, `python3.12`, `python3.11`, `python3` y `python`; por tanto, `python3` puede apuntar a una versión antigua siempre que exista otro binario compatible. En Windows prueban `py -3`, `python` y `python3`. Si no encuentran Python 3.11 o superior, terminan sin modificar el sistema y recomiendan la vía Docker.

## Preparar el índice local

Después de instalar, valida `content/`, construye `.agentic-book-data` y ejecuta una recuperación de prueba.

Linux o macOS:

```bash
./scripts/ingest.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ingest.ps1
```

Repite este paso cuando añadas, reemplaces o elimines archivos en `content/`. Después abre una sesión nueva de Codex o Claude Code para que el proceso STDIO lea el índice actualizado.

## Instalación manual en Linux y macOS

Comprueba primero la versión:

```bash
python3 --version
```

Después:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[mcp]"
.venv/bin/agentic-book --content-root content validate-content --strict-freshness
.venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
.venv/bin/agentic-book --data-dir .agentic-book-data get-document playbook.sql-agent-enterprise
```

## Instalación manual en Windows PowerShell

Comprueba primero la versión:

```powershell
py -3 --version
```

Después:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[mcp]"
.\.venv\Scripts\agentic-book.exe --content-root content validate-content --strict-freshness
.\.venv\Scripts\agentic-book.exe --content-root content --data-dir .agentic-book-data ingest
.\.venv\Scripts\agentic-book.exe --data-dir .agentic-book-data get-document playbook.sql-agent-enterprise
```

No es necesario ejecutar `source`, `Activate.ps1` ni actualizar `pip` para usar el proyecto.

## Configurar STDIO en Codex

STDIO requiere rutas absolutas. Sustituye los ejemplos por la ubicación real del clon.

Linux o macOS, en `.codex/config.toml` o `~/.codex/config.toml`:

```toml
[mcp_servers.agentic_book]
command = "/ruta/absoluta/agentic-book/.venv/bin/agentic-book"
args = [
  "--content-root", "/ruta/absoluta/agentic-book/content",
  "--data-dir", "/ruta/absoluta/agentic-book/.agentic-book-data",
  "serve-mcp", "--transport", "stdio",
]
cwd = "/ruta/absoluta/agentic-book"
startup_timeout_sec = 20
tool_timeout_sec = 60
```

Windows usa barras invertidas escapadas:

```toml
[mcp_servers.agentic_book]
command = "C:\\ruta\\agentic-book\\.venv\\Scripts\\agentic-book.exe"
args = [
  "--content-root", "C:\\ruta\\agentic-book\\content",
  "--data-dir", "C:\\ruta\\agentic-book\\.agentic-book-data",
  "serve-mcp", "--transport", "stdio",
]
cwd = "C:\\ruta\\agentic-book"
startup_timeout_sec = 20
tool_timeout_sec = 60
```

Abre una sesión nueva y ejecuta `/mcp`.

## Configurar STDIO en Claude Code

Claude Code puede registrar el mismo ejecutable. En Linux o macOS:

```bash
claude mcp add agentic_book -- /ruta/absoluta/agentic-book/.venv/bin/agentic-book \
  --content-root /ruta/absoluta/agentic-book/content \
  --data-dir /ruta/absoluta/agentic-book/.agentic-book-data \
  serve-mcp --transport stdio
```

En Windows PowerShell:

```powershell
claude mcp add agentic_book -- C:\ruta\agentic-book\.venv\Scripts\agentic-book.exe `
  --content-root C:\ruta\agentic-book\content `
  --data-dir C:\ruta\agentic-book\.agentic-book-data `
  serve-mcp --transport stdio
```

## Actualizar el índice

Linux o macOS:

```bash
.venv/bin/agentic-book --content-root content validate-content --strict-freshness
.venv/bin/agentic-book --content-root content --data-dir .agentic-book-data ingest
```

Windows PowerShell:

```powershell
.\.venv\Scripts\agentic-book.exe --content-root content validate-content --strict-freshness
.\.venv\Scripts\agentic-book.exe --content-root content --data-dir .agentic-book-data ingest
```

Después abre una sesión nueva de Codex o Claude Code para que el proceso STDIO lea el índice actualizado.
