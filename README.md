# Agentic Book

Agentic Book convierte una colección de documentos Markdown curados en una base de conocimiento local que los agentes LLM pueden consultar mediante MCP. El repositorio valida los documentos, construye un índice incremental y ofrece búsquedas convencionales, híbridas y multiquery con Reciprocal Rank Fusion.

El corpus actual incluye material sobre agentes LLM, MCP, FastMCP, acceso empresarial a bases de datos SQL, gobernanza, seguridad, observabilidad y la Capa 1 de datos.

## Inicio rápido: instalación nativa

Esta es la primera opción recomendada para trabajar con agentes como Codex o Claude Code. Ejecuta el MCP mediante STDIO, no necesita Docker y deja el índice local en `.agentic-book-data/`.

### 1. Requisitos comunes

- Haber aceptado la invitación al repositorio privado con tu cuenta de GitHub.
- Tener [Git](https://git-scm.com/downloads) instalado.
- Tener Python 3.11 o superior. El proyecto se verifica en CI con Python 3.11 y 3.13.

Clona el repositorio mediante HTTPS:

```bash
git clone https://github.com/eramireztorres/agentic-book.git
cd agentic-book
```

GitHub puede pedirte que inicies sesión. No uses la contraseña de tu cuenta como contraseña Git: utiliza el gestor de credenciales de GitHub, GitHub Desktop o un Personal Access Token. SSH también funciona si ya tienes una clave configurada.

No necesitas `OPENAI_API_KEY`: la configuración local predeterminada no llama a modelos externos.

### 2. Linux

Comprueba Python:

```bash
python3 --version
```

Si muestra Python 3.11 o superior, ejecuta:

```bash
./scripts/setup.sh
```

El script detecta `python3.13`, `python3.12`, `python3.11`, `python3` o `python`; crea `.venv`, instala Agentic Book, valida `content/`, ingesta el corpus y ejecuta una recuperación de prueba.

Para registrar el MCP en Codex mediante STDIO:

```bash
codex mcp add agentic_book -- "$(pwd)/.venv/bin/agentic-book" \
  --content-root "$(pwd)/content" \
  --data-dir "$(pwd)/.agentic-book-data" \
  serve-mcp --transport stdio
```

Para Claude Code:

```bash
claude mcp add agentic_book -- "$(pwd)/.venv/bin/agentic-book" \
  --content-root "$(pwd)/content" \
  --data-dir "$(pwd)/.agentic-book-data" \
  serve-mcp --transport stdio
```

### 3. macOS

Comprueba Python:

```bash
python3 --version
```

Si muestra Python 3.11 o superior, ejecuta el mismo instalador:

```bash
./scripts/setup.sh
```

Si `python3` no existe o es demasiado antiguo, instala Python desde `python.org` o con tu gestor habitual, por ejemplo Homebrew, y vuelve a ejecutar el script.

Para registrar el MCP en Codex mediante STDIO:

```bash
codex mcp add agentic_book -- "$(pwd)/.venv/bin/agentic-book" \
  --content-root "$(pwd)/content" \
  --data-dir "$(pwd)/.agentic-book-data" \
  serve-mcp --transport stdio
```

Para Claude Code:

```bash
claude mcp add agentic_book -- "$(pwd)/.venv/bin/agentic-book" \
  --content-root "$(pwd)/content" \
  --data-dir "$(pwd)/.agentic-book-data" \
  serve-mcp --transport stdio
```

### 4. Windows PowerShell

Comprueba Python:

```powershell
py -3 --version
```

Si muestra Python 3.11 o superior, ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

El script crea `.venv`, instala Agentic Book, valida `content/`, ingesta el corpus y ejecuta una recuperación de prueba. No necesitas ejecutar `source`, `Activate.ps1` ni activar manualmente el entorno virtual.

Para registrar el MCP en Codex mediante STDIO:

```powershell
$repo = (Get-Location).Path
codex mcp add agentic_book -- "$repo\.venv\Scripts\agentic-book.exe" `
  --content-root "$repo\content" `
  --data-dir "$repo\.agentic-book-data" `
  serve-mcp --transport stdio
```

Para Claude Code:

```powershell
$repo = (Get-Location).Path
claude mcp add agentic_book -- "$repo\.venv\Scripts\agentic-book.exe" `
  --content-root "$repo\content" `
  --data-dir "$repo\.agentic-book-data" `
  serve-mcp --transport stdio
```

### 5. Comprueba la conexión

Abre una sesión nueva de Codex o Claude Code y ejecuta `/mcp`. `agentic_book` debe aparecer conectado. Después prueba alguna de las preguntas de la sección siguiente.

Consulta la [guía de instalación nativa](docs/guias/instalacion-nativa.md) si prefieres comandos manuales o necesitas configurar rutas absolutas a mano.

## Segunda opción: Docker

Docker es útil si no quieres instalar Python o si prefieres aislar el servicio. En esta modalidad el MCP se sirve por HTTP local.

### 1. Requisitos

- Tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e iniciado. En Linux también puedes usar Docker Engine con el complemento Compose.
- Haber clonado el repositorio y estar situado en la carpeta `agentic-book`.

### 2. Inicia el servidor

```bash
docker compose up --build -d
```

Si Docker responde que el puerto `8000` ya está ocupado, no hace falta detener otros proyectos. Arranca este MCP en otro puerto de tu equipo:

```bash
AGENTIC_BOOK_HOST_PORT=8001 docker compose up --build -d
```

En PowerShell:

```powershell
$env:AGENTIC_BOOK_HOST_PORT="8001"
docker compose up --build -d
```

En ese caso, usa `http://127.0.0.1:8001/mcp` al configurar Codex o Claude Code.

La primera ejecución construye la imagen, valida los Markdown, crea el índice y levanta el MCP. Comprueba el estado:

```bash
docker compose ps
```

El servicio debe aparecer como `healthy`. El endpoint MCP queda disponible únicamente en tu equipo:

```text
http://127.0.0.1:8000/mcp
```

### 3. Conecta Codex

```bash
codex mcp add agentic_book --url http://127.0.0.1:8000/mcp
codex mcp list
```

Abre una sesión nueva de Codex y ejecuta `/mcp`. `agentic_book` debe aparecer conectado.

### 4. Conecta Claude Code

```bash
claude mcp add --transport http agentic_book http://127.0.0.1:8000/mcp
claude mcp list
```

Abre una sesión nueva de Claude Code y ejecuta `/mcp` para comprobar la conexión.

## Preguntas para comprobar el RAG

Prueba primero el inventario y la recuperación básica:

```text
Usa el MCP agentic_book. Consulta corpus_manifest y dime cuántos documentos y chunks hay indexados. Indica también la fecha de revisión del corpus.
```

```text
Usa agentic_book para explicar qué controles debe aplicar una empresa antes de permitir que un agente consulte una base de datos SQL. Cita los document_id y las secciones utilizadas.
```

```text
Compara el acceso a datos empresariales mediante APIs, tools MCP y RAG. Explica cuándo conviene cada alternativa y cita las fuentes del corpus.
```

```text
¿Qué responsabilidades deberían tener el Data Owner y el Data Steward en una plataforma de agentes? Usa agentic_book y señala cualquier limitación de la documentación recuperada.
```

```text
Propón una arquitectura de solo lectura para exponer una base de datos SQL mediante MCP, incluyendo seguridad, capa semántica, auditoría y observabilidad.
```

```text
Usa fusion_search con subconsultas sobre seguridad SQL, gobernanza, capa semántica y aprobación humana. Después recupera los documentos más relevantes y sintetiza una recomendación empresarial.
```

```text
Usa agentic_book para decidir si una fuente de datos de Capa 1 debe exponerse como API, tool MCP o RAG. Aplica el árbol de decisión y las reglas Si-Entonces del corpus.
```

Para comprobar la abstención:

```text
Busca en agentic_book información sobre astrología aplicada a recetas de cocina. No inventes una respuesta: indica si el corpus contiene evidencia suficiente.
```

Una respuesta bien fundamentada debe identificar los documentos consultados, las secciones relevantes y las limitaciones encontradas.

## Operaciones habituales con Docker

Ver los logs:

```bash
docker compose logs -f agentic-book-mcp
```

Detener el servicio sin borrar el índice:

```bash
docker compose down
```

Después de añadir, reemplazar o eliminar archivos en `content/`, reinicia el servicio. El contenedor volverá a validar e ingerir el corpus de forma incremental:

```bash
docker compose restart agentic-book-mcp
```

Para reconstruir completamente el índice local:

```bash
docker compose down -v
docker compose up --build -d
```

Si cambias código Python, dependencias o el Dockerfile, vuelve a usar `docker compose up --build -d`.

## Instalación nativa

Esta opción es útil para desarrollar el proyecto o ejecutar MCP mediante STDIO. Necesita Python 3.11 o superior; las versiones verificadas por CI son Python 3.11 y 3.13.

Linux y macOS:

```bash
./scripts/setup.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Los scripts detectan Python, crean `.venv`, instalan el servidor MCP, validan el contenido, ejecutan la ingesta y realizan una recuperación de prueba. No es necesario activar el entorno virtual.

Consulta la [guía de instalación nativa](docs/guias/instalacion-nativa.md) para los comandos manuales y la configuración STDIO en cada sistema operativo.

## Añadir o actualizar documentos

Los documentos consumibles por el RAG deben estar en `content/`. La carpeta `docs/` se utiliza para fuentes originales, documentos largos y material de trabajo que todavía no está curado.

Cada Markdown debe:

- cubrir una unidad semántica clara y poder entenderse de forma independiente;
- tener un `id` único y frontmatter válido;
- identificar audiencia, dominio, tipo, fuentes y fechas de revisión;
- enlazar únicamente identificadores existentes en `related`;
- evitar repetir texto que ya sea canónico en otro documento.

No dividas un PDF por páginas. Sepáralo por conceptos, patrones, riesgos, checklists o casos de uso. Después reinicia Docker o ejecuta la ingesta nativa.

La estructura, el frontmatter y el flujo de actualización están descritos en la [guía de curación de contenido](docs/guias/curacion-contenido.md).

## Qué ofrece el servidor MCP

| Superficie | Función |
|---|---|
| `corpus_manifest` | Describe el corpus, freshness, capacidades y evaluaciones disponibles. |
| `search` | Recupera chunks mediante búsqueda `lexical`, `vector` o `hybrid`, con filtros y abstención por score. |
| `fusion_search` | Fusiona varias subconsultas mediante Reciprocal Rank Fusion. |
| `get_document` | Devuelve un documento curado completo por `document_id`. |
| `agentic-book://manifest` | Expone el manifiesto como recurso MCP. |
| `agentic-book://documents/{document_id}` | Expone documentos completos como recursos MCP. |
| `summarize_with_citations` | Prompt para resumir un documento con citas. |
| `compare_concepts` | Prompt para comparar conceptos usando recuperación previa. |

Flujo recomendado para un agente:

```text
1. Consultar corpus_manifest.
2. Buscar evidencia con search o fusion_search.
3. Recuperar los documentos más relevantes con get_document.
4. Responder citando document_id, secciones, freshness y limitaciones.
```

## Solución de problemas

| Problema | Qué comprobar |
|---|---|
| `docker: command not found` | Instala Docker Desktop o Docker Engine con Compose. |
| Docker no puede conectarse al daemon | Inicia Docker Desktop o el servicio Docker. |
| El puerto 8000 ya está ocupado | En Linux/macOS inicia con `AGENTIC_BOOK_HOST_PORT=8001 docker compose up --build -d`; en PowerShell define primero `$env:AGENTIC_BOOK_HOST_PORT="8001"`. Usa el mismo puerto en la URL MCP. |
| El contenedor no llega a `healthy` | Ejecuta `docker compose logs agentic-book-mcp`; normalmente mostrará un error de validación o ingesta. |
| GitHub rechaza el clon | Confirma que aceptaste la invitación y que Git está autenticado con la cuenta correcta. |
| `python` o `python3` no existe | Usa Docker o instala Python 3.11 o superior antes de la instalación nativa. |
| `MCP startup failed: No such file or directory` | La configuración STDIO apunta a un ejecutable inexistente; vuelve a ejecutar el script nativo y corrige la ruta absoluta. |
| El agente no encuentra contenido nuevo | Reinicia el contenedor o ejecuta de nuevo la ingesta y abre una sesión nueva del cliente MCP. |

## Desarrollo y calidad

La arquitectura, configuración, evaluaciones de retrieval, checks locales y flujo de CI están en la [guía de desarrollo](docs/guias/desarrollo.md).

El proyecto incluye validación estricta del corpus, ingesta incremental, evaluaciones convencionales y de fusion retrieval, tests del servidor MCP, GitHub Actions y una imagen Docker local.
