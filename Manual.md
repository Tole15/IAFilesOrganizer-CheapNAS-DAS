# MANUAL de Uso — Smart Storage Organizer AI (API)
**Proyecto:** `IAFilesOrganizer-CheapNAS-DAS`

Este manual explica cómo usar el proyecto **IAFilesOrganizer-CheapNAS-DAS** en su versión actual (backend con **FastAPI**).  
El objetivo del sistema es:

1. Escanear un directorio (`POST /scan`) y guardar metadatos de archivos en una base local.
2. Extraer texto de archivos compatibles (`POST /extract`) para que la IA pueda **ver** su contenido.
3. (Opcional) Generar embeddings (`POST /embed`) para búsqueda semántica / RAG.
4. Pedirle a un LLM un **plan de organización** (`POST /plan`) que sugiera mover/renombrar con criterio.
5. Aplicar el plan (`POST /apply`) en modo **dry-run** o real.

> Importante: el proyecto **no borra archivos automáticamente**. Primero genera un plan y tú decides si lo aplicas.

---

## 1) Requisitos

- Windows 10/11 (o Linux/Mac con pequeños cambios)
- Python 3.11+ recomendado
- Git
- (Opcional) API key de OpenAI si usarás `/embed` y/o `/plan` con LLM
- Disco con datos (HDD/SSD/NAS/DAS). Para pruebas, usa una carpeta con copias.

---

## 2) Estructura del proyecto

- `apps/`: API FastAPI (endpoints, schemas, rutas).
- `packages/`: lógica del core  
  - `packages/scanner/`: escaneo, hashing y marcado de archivos generados (basura típica)
  - `packages/extractors/`: extracción de texto (PDF/otros)
  - `packages/intelligence/`: embeddings, planner (LLM), búsqueda
- `data/`: base local (SQLite) y datos internos.

> Nota: `.env`, `.venv/` y `data/` **no** deberían versionarse en Git.

---

## 3) Instalación (modo local)

### 3.1) Crear y activar venv

En PowerShell, en la raíz del repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3.2) Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## 4) Variables de entorno (OpenAI)

Crea un archivo `.env` en la raíz (NO se sube a Git):

```bash
OPENAI_API_KEY=tu_api_key_aqui
```

Verifica que se cargó:

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('KEY=', bool(os.getenv('OPENAI_API_KEY')))"
```

Si sale `KEY= True`, ya quedó.

---

## 5) Levantar la API

### 5.1) Opción recomendada (estable, sin reinicios)

```powershell
python -m uvicorn apps.api.main:app --port 8000
```

### 5.2) Opción dev (con reload)

Úsala solo si no estás tocando scripts sueltos que disparen reload:

```powershell
python -m uvicorn apps.api.main:app --reload --port 8000
```

Swagger:
- http://127.0.0.1:8000/docs

---

## 6) Conceptos: `root_path`, jobs y estados

### 6.1) `root_path`

Es la carpeta raíz que quieres procesar. Ejemplos:

- `C:\Users\...\docs`
- `C:\Users\...\fpga`
- `D:\NAS\clientes\proyecto_01`

**Regla:** En JSON debes escribir backslashes escapadas (`\\`).

### 6.2) Jobs

Cada operación pesada se lanza como un job:

- `queued`: en cola
- `running`: en proceso
- `done`: terminó bien
- `failed`: falló (ver campo `error`)

Ver job:
- `GET /jobs/{job_id}`

---

## 7) Pipeline recomendado (paso a paso)

Para un directorio `root_path`, este es el flujo típico.

### Paso 1 — Scan

**Endpoint:** `POST /scan`

Body ejemplo:

```json
{
  "root_path": "C:\\Users\\Tole Mendoza\\OneDrive\\Documentos\\sumobot-embedded-system-competition2\\sumobot-embedded-system-competition\\fpga",
  "mode": "incremental"
}
```

Respuesta típica:

```json
{ "job_id": 123, "status": "queued" }
```

Luego:
- `GET /jobs/123` hasta que cambie a `done`.

**Resultado:** se registran archivos en DB con metadatos + marca `is_generated` para archivos basura (isim/work/build/etc).

---

### Paso 2 — Extract

**Endpoint:** `POST /extract`

Body ejemplo:

```json
{
  "root_path": "C:\\Users\\...\\fpga",
  "limit": 500,
  "force": true
}
```

- `force=true` reintenta extracción aunque ya existiera.
- Se recomienda procesar solo archivos `active` y **no generados**.

Luego:
- `GET /jobs/{job_id}` hasta `done`.

**Resultado:**
- `content_status=ok` y `content_text` para PDFs/archivos soportados
- `unsupported` para imágenes/binarios, etc.

---

### Paso 3 — Embed (opcional)

**Endpoint:** `POST /embed`

Body ejemplo:

```json
{
  "root_path": "C:\\Users\\...\\fpga",
  "limit": 200
}
```

Luego:
- `GET /jobs/{job_id}` hasta `done`.

**Resultado:**
- `embedding_status=ok` si hay texto
- Si falla: revisa key, cuota y logs.

---

### Paso 4 — Plan

**Endpoint:** `POST /plan`

Body ejemplo:

```json
{
  "root_path": "C:\\Users\\...\\fpga",
  "policy": "default",
  "limit": 200
}
```

Luego:
- `GET /jobs/{job_id}` hasta `done`.
- En `stats_json` verás `plan_id`.

**Resultado:** se guarda un JSON con acciones (`move`, `mkdir`), con `confidence` y `rationale`.

Recomendación (tu criterio):
- limitar profundidad (pocas carpetas)
- evitar forzar siempre una categoría como `embedded_system`
- usar fallbacks por `ext`/`mimetype` cuando no hay texto

---

### Paso 5 — Apply

**Endpoint:** `POST /apply`

Primero **dry-run**:

```json
{
  "plan_id": 3,
  "dry_run": true
}
```

Si se ve bien:

```json
{
  "plan_id": 3,
  "dry_run": false
}
```

**Resultado:** se crean carpetas y se mueven/renombran archivos.  
Si existe `op_journal`, se guarda el historial de operaciones.

---

## 8) Consultas útiles

- Ver archivos: `GET /files?root_path=...&limit=50&offset=0`
- Ver archivo: `GET /files/{file_id}`
- Ver job: `GET /jobs/{job_id}`

---

## 9) Buenas prácticas y seguridad

1. Prueba con una carpeta de copia primero.
2. Ejecuta `/apply` con `dry_run=true` antes de mover realmente.
3. Mantén `.env` fuera de Git.
4. Si expones la API con Cloudflare Tunnel:
   - añade autenticación (Cloudflare Access / JWT / Basic Auth)
   - restringe acceso según necesidad (IP/país)
   - considera modo solo lectura (sin apply) para entornos públicos

---

## 10) Troubleshooting rápido

### 10.1) Swagger da 422 “JSON invalid”
En Windows debes escapar backslashes. Ejemplo correcto:

```json
{ "root_path": "C:\\Users\\Tu\\Ruta" }
```

### 10.2) `/plan` se queda queued o falla
Revisa:
- `GET /jobs/{id}`
- logs de uvicorn

Si usas `--reload` y estás editando scripts sueltos, puede reiniciar procesos.  
Solución: reinicia uvicorn **sin** `--reload`.

### 10.3) Embeddings fallan por cuota o key
- `429 insufficient_quota`: no hay cuota/saldo
- `401 invalid_api_key`: key inválida o mal cargada

---

## 11) Roadmap sugerido

- Clasificación automática de archivos generados con `is_generated` desde `scan`
- Exclusión automática en `extract/embed/plan` (sin obligar al usuario a configurar globs)
- Planner con límite de profundidad (1 categoría + 0–2 subfolders)
- Políticas por carpeta (ej. catecismo vs fpga vs clientes)
- Cloudflare Tunnel + Auth + DNS estable
