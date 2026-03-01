# Smart Storage Organizer AI

> **Goal:** Turn a cheap NAS/DAS + HDD/SSD docking station into a **safe, AI‑assisted storage organizer** that can **understand file content**, propose an organization plan, and (optionally) apply renames/moves with full traceability.
>
> **Remote-first:** Access is secured via **Cloudflare Tunnel + DNS (no VPN required)**.

---

## English

### Project Description

**Smart Storage Organizer AI** is an AI automation system that:

1. **Scans** a mounted storage root (NAS share / external dock / DAS)
2. **Extracts content** (text + metadata) from supported file types
3. **Classifies** and **tags** files using AI
4. Produces a **structured organization plan** (JSON) containing:

   * target folders
   * suggested names
   * move/rename actions
   * confidence + rationale
5. Optionally **applies** the plan safely (dry‑run by default)

This project started as a TensorFlow idea, but it is designed to be practical and deployable:

* **ML/AI layer is modular**: you can plug in TensorFlow models, OpenAI models, or hybrid approaches.
* **Automation is the product**: policies, safety checks, audit logs, and ROI reporting.

#### Why this is useful

* Stops “Downloads/” chaos by enforcing naming conventions and folder structure.
* Reduces duplicate files and improves discoverability (semantic search).
* Enables a repeatable workflow you can package for clients (documentation + metrics).

---

## Key Features

### ✅ File Intelligence

* Incremental filesystem scan (metadata + hashes)
* Text extraction (PDF/DOCX/TXT) + metadata extraction (images, etc.)
* Semantic search (embeddings) and similarity clustering
* Tagging and classification with AI

### ✅ Safe Automation

* **Dry-run by default**: generates a plan without touching your files
* Apply mode with guardrails:

  * no delete by default (optional `_trash/` quarantine)
  * collision handling (no overwrite)
  * journaled operations + undo

### ✅ Remote Access (No VPN)

* Secure API/UI exposure via **Cloudflare Tunnel**
* DNS routing (e.g. `api.yourdomain.com`)
* Optional: Cloudflare Access (OTP/SSO), IP allowlists, rate limits

---

## Architecture Overview

```
Storage Root (NAS/DAS) -> Scanner -> Extractors -> Intelligence -> Planner -> Executor
                                         |                 |
                                         |                 +-> Embeddings Index (Search/Cluster)
                                         +-> Metadata/DB

Remote client -> Cloudflare DNS/Tunnel -> API (FastAPI) -> Jobs (scan/plan/apply/undo)
```

### Components

* **Scanner**: walks the filesystem, stores metadata + hash in DB
* **Extractors**: parse content (PDF/DOCX/TXT) and normalize it
* **Intelligence**:

  * embeddings for search/similarity
  * optional TensorFlow model(s) for classification
  * optional LLM planner for structured decisions
* **Planner**: generates a JSON plan (actions + rationale)
* **Executor**: applies plan with validations + journal + undo
* **API**: exposes endpoints for scan/plan/apply/status/undo

---

## Installation

> This repository is being rebuilt; the steps below describe the intended setup. If a command differs in your branch, follow the `apps/api/` README or `docker-compose.yml`.

### Requirements

* Python 3.10+
* Git
* Optional: Docker + Docker Compose
* Optional (for NAS): mounted share path (SMB/NFS)

### Option A — Local Python

1. Clone

```bash
git clone https://github.com/Tole15/IAFilesOrganizer-CheapNAS-DAS.git
cd IAFilesOrganizer-CheapNAS-DAS
```

2. Create & activate venv

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
```

3. Install deps

```bash
pip install -r requirements.txt
```

4. Run API (development)

```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

* Swagger UI: `http://localhost:8000/docs`

### Option B — Docker (Recommended)

```bash
docker compose up --build
```

---

## Configuration

Create a `.env` file (do **not** commit secrets):

```env
# Filesystem
STORAGE_ROOT=/mnt/storage

# Database
DATABASE_URL=sqlite:///./data/index.db

# AI Provider (choose one)
AI_PROVIDER=openai
OPENAI_API_KEY=YOUR_KEY_HERE

# Optional integrations (future)
ZOHOMODULE_ENABLED=false
TWILIO_ENABLED=false

# Safety
DRY_RUN_DEFAULT=true
TRASH_ENABLED=true
TRASH_DIR=/_trash
```

---

## Usage

### 1) Scan storage (incremental)

```bash
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"root_path":"/mnt/storage","mode":"incremental"}'
```

### 2) Create an organization plan (dry-run)

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{"root_path":"/mnt/storage","policy":"default","dry_run":true}'
```

### 3) Apply a plan (requires explicit confirmation)

```bash
curl -X POST "http://localhost:8000/apply" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"<PLAN_ID>","confirm":true}'
```

### 4) Undo (rollback)

```bash
curl -X POST "http://localhost:8000/undo/<JOB_ID>"
```

---

## Policies (How files get organized)

Policies define *where* files should go and *how* they should be named.

Example policy ideas:

* **Photos**: `/Photos/YYYY/MM/` using EXIF date; fallback to modified date
* **Invoices/Receipts**: `/Finance/Receipts/YYYY/` with vendor + amount if extractable
* **School/Projects**: `/School/<Course>/<Semester>/` by keywords in documents

Planned location:

* `docs/policies/` (human-readable)
* `packages/intelligence/policies/` (machine-readable)

---

## Remote Access with Cloudflare Tunnel + DNS (No VPN)

**Why:** Avoid exposing NAS services directly and keep your storage on a private LAN.

### High-level steps

1. Install `cloudflared` on the host running the API
2. Create a tunnel and map a hostname (e.g. `api.yourdomain.com`)
3. Route traffic through the tunnel to `localhost:8000`
4. (Optional) Protect with Cloudflare Access (OTP/SSO)

Documentation will live in:

* `docs/deployment/cloudflare-tunnel.md`

---

## Integrations (Planned)

This project is structured to support client-style automation workflows:

* **Zoho (CRM/Desk/Projects):** create/update records after classification
* **Twilio:** notify results (WhatsApp/SMS)
* **DALL·E / MidJourney:** generate folder covers/thumbnails (optional)
* **Synthesia:** generate onboarding videos for the workflow (optional)

---

## Project Structure (Target)

```
apps/
  api/               # FastAPI endpoints
  worker/            # background jobs
packages/
  core/              # DB models, storage abstraction
  extractors/        # PDF/DOCX/TXT + metadata
  intelligence/      # embeddings + TF/LLM + planner
  executor/          # apply/undo + safety
  integrations/      # zoho/twilio/etc
infra/
  docker/
  cloudflare/
docs/
  architecture.md
  deployment/
  evaluation/
  runbook.md
tests/
```

---

## Contributing

Contributions are welcome—especially:

* new extractors (file types)
* policy modules
* safety improvements (atomic ops, collision resolution)
* test fixtures + regression tests

### Suggested workflow

1. Fork the repo
2. Create a feature branch
3. Add tests if applicable
4. Open a PR with clear description + screenshots/logs

---

## License

Choose a license depending on your goal:

* **MIT**: simple and permissive
* **Apache-2.0**: permissive + explicit patent grant
* **GPL-3.0**: strong copyleft

> Pending final selection: add `LICENSE` file.

---

## Roadmap (7-week build plan)

* **Week 1:** scanner + DB + API + baseline metrics
* **Week 2:** extractors + embeddings + semantic search
* **Week 3:** planner JSON schema + dry-run diffs
* **Week 4:** executor + journal + undo
* **Week 5:** Zoho integration + reporting
* **Week 6:** Twilio notifications + approvals workflow
* **Week 7:** ROI evaluation + client-ready documentation pack

---

## Notes

* The initial concept referenced **TensorFlow**, and it can still be used for classification models.
* However, the system is intentionally **provider-agnostic**: you can swap models without changing the automation core.
* The priority is **safe automation + documentation + replicability**.
