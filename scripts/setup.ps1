$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvDir = Join-Path $RepoRoot ".venv"

function Test-CompatiblePython {
    param(
        [string]$Command,
        [string[]]$Arguments = @()
    )

    try {
        & $Command @Arguments -c "import sys; raise SystemExit(sys.version_info < (3, 11))" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

$PythonCommand = $null
$PythonArguments = @()
$Candidates = @(
    @{ Command = "py"; Arguments = @("-3") },
    @{ Command = "python"; Arguments = @() },
    @{ Command = "python3"; Arguments = @() }
)

foreach ($Candidate in $Candidates) {
    if (Test-CompatiblePython -Command $Candidate.Command -Arguments $Candidate.Arguments) {
        $PythonCommand = $Candidate.Command
        $PythonArguments = $Candidate.Arguments
        break
    }
}

if ($null -eq $PythonCommand) {
    Write-Error "Se necesita Python 3.11 o superior. Instálalo desde https://www.python.org/downloads/windows/ o usa Docker."
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$AgenticBook = Join-Path $VenvDir "Scripts\agentic-book.exe"

if (Test-Path $VenvPython) {
    if (-not (Test-CompatiblePython -Command $VenvPython)) {
        Write-Error ".venv existe, pero usa una versión de Python anterior a 3.11. Renómbralo o elimínalo y vuelve a ejecutar el script."
    }
}
else {
    Write-Host "Creando el entorno virtual con $PythonCommand..."
    & $PythonCommand @PythonArguments -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
}

Write-Host "Instalando Agentic Book y el servidor MCP..."
& $VenvPython -m pip install -e "$RepoRoot[mcp]"
if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar Agentic Book." }

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
Write-Host "Instalación completada correctamente."
Write-Host "Ejecutable MCP: $AgenticBook"
Write-Host "Índice local: $(Join-Path $RepoRoot '.agentic-book-data')"
