$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$AgenticBook = Join-Path $RepoRoot ".venv\Scripts\agentic-book.exe"

if (-not (Test-Path $AgenticBook)) {
    Write-Error "No existe $AgenticBook. Ejecuta primero powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 desde la carpeta agentic-book."
}

Write-Host "Validando el contenido curado..."
& $AgenticBook --content-root (Join-Path $RepoRoot "content") validate-content --strict-freshness
if ($LASTEXITCODE -ne 0) { throw "La validación del contenido falló." }

Write-Host "Construyendo el índice local..."
& $AgenticBook --content-root (Join-Path $RepoRoot "content") --data-dir (Join-Path $RepoRoot ".agentic-book-data") ingest
if ($LASTEXITCODE -ne 0) { throw "La ingesta falló." }

Write-Host "Comprobando una recuperación completa..."
& $AgenticBook --data-dir (Join-Path $RepoRoot ".agentic-book-data") get-document playbook.sql-agent-enterprise | Out-Null
if ($LASTEXITCODE -ne 0) { throw "La recuperación de prueba falló." }

Write-Host ""
Write-Host "Índice local preparado correctamente."
Write-Host "Índice local: $(Join-Path $RepoRoot '.agentic-book-data')"
