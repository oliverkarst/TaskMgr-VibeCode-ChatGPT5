# TaskMgr-VibeCode-ChatGPT5 — Haupt-README

_Statusstand: 2025-09-15 18:44:25 UTC_

Diese README beschreibt das Gesamtprojekt, die ursprüngliche Zielsetzung, alle bisher umgesetzten **Steps 1–4**, typische Fehler auf dem Weg und den aktuellen Stand. Das Projekt wurde im Pairing-Ansatz mit „VibeCoding“ (schrittweise, kleine Iterationen) aufgebaut.

---

## Projektidee & Original-Prompt

> *Ich bin IT-Architekt. Du sollst mir helfen VibeCoding mit einem praktischen Projekt auszuprobieren und meine Kenntnisse zu verbessern. [...] Meine Idee ist eine Tasks Listen App, also ToDos, die über das Frontend erstellt und gelöscht und bearbeitet werden können. Über das Backend in eine Datenbank fließen. Das Backend stellt eine marktübliche OpenAPI Schnittstelle bereit, worüber auch andere Frontends wie Apps andocken können. Hast Du noch eine andere Idee? Was ist Deine Empfehlung?*

Wir entschieden uns für **FastAPI + PostgreSQL** im Backend und **Angular** im Frontend, alles dockerisiert und per Compose orchestriert.

---

## Architektur (Stand Step 4)

- **db**: PostgreSQL 16 (Docker, persistentes Volume `pgdata`)
- **api**: FastAPI + Uvicorn, SQLAlchemy, Alembic (Docker, Port **8080**)
- **ui**: Angular Dev-Server (Docker, Port **4200**, Live-Reload)
- **Proxy**: `ui/proxy.conf.json` routet `/api/*` → `http://api:8080`

```
Browser ── http://localhost:4200 ──> ui (ng serve)
                                 \-\/ (Proxy /api/*)
                                   api (FastAPI @8080) ──> db (Postgres)
```

---

## Repo & Branching

- GitHub: **oliverkarst/TaskMgr-VibeCode-ChatGPT5**
- Branch: **main** (zeigt auf den aktuellsten Stand)
- Tags: `step1`, `step2`, `step3`, `step4`

Erstellung/Push (Kurzform):
```bash
git init -b main
git add . && git commit -m "step1 ..."
git tag -a step1 -m "Step 1"
# später step2/3/4 einspielen, committen, taggen
git remote add origin https://github.com/oliverkarst/TaskMgr-VibeCode-ChatGPT5.git
git push -u origin main && git push origin --tags
```

> Hinweis: Beim Zusammenführen älterer Stände wurde `rsync` verwendet – dabei muss **immer** `--exclude='.git'` genutzt werden, sonst wird das Repo gelöscht.

---

## Steps (Inhalte, Entscheidungen & Artefakte)

### Step 1 — Projektgerüst Backend (FastAPI in Docker)
**Ziele**: Minimales API-Gerüst, Docker-Compose, erste Dokumentation.

- Ordner `api/` mit `Dockerfile`, `requirements.txt`, minimaler `app/main.py`.
- `compose.yaml` mit Service **api** (Port 8080).
- `docs/` angelegt (Spezifikationen/Architektur-Notizen).
- **README** (Step1) erklärt Start mit `docker compose up --build`.

### Step 2 — In-Memory CRUD + OpenAPI
**Ziele**: Nutzbare Tasks-API ohne DB, saubere Schnittstelle.

- Endpunkte: `GET/POST /api/v1/tasks`, `GET/PATCH/DELETE /api/v1/tasks/{id}`, `GET /health`.
- **OpenAPI**: `openapi/tasks.yaml`.
- Swagger: `http://localhost:8080/docs`.
- **README** (Step2) mit Beispiel-Requests (curl).

### Step 3 — PostgreSQL + SQLAlchemy + Alembic
**Ziele**: Persistenzschicht & Migrationen, Compose mit DB.

- Compose um **db** (Postgres 16-alpine) erweitert (Volume `pgdata`).
- SQLAlchemy-Model `Task`, Alembic-Migrationen, `entrypoint.sh` führt `alembic upgrade head` aus.
- **Health-/Smoke-Test** erfolgreich:
  ```bash
  curl -s http://localhost:8080/health
  curl -s -X POST http://localhost:8080/api/v1/tasks -H 'Content-Type: application/json' -d '{"title":"Persistenter Task","priority":"high"}'
  curl -s http://localhost:8080/api/v1/tasks
  ```

**Besondere Fixes in Step 3**:
- **Python-Modulpfad**:
  - Fehler: `ModuleNotFoundError: No module named 'app'`
  - Fix: `PYTHONPATH=/app` gesetzt (Compose-Env bzw. im Container), Projektstruktur geklärt.
- **Alembic Logging**:
  - Fehler: `KeyError: 'formatters'`
  - Fix: `alembic.ini` mit gültiger `[loggers]/[handlers]/[formatters]`-Sektion ergänzt.
- **Alembic DB-URL**:
  - Fehler: `KeyError: 'url'` beim Lesen von `alembic.ini`
  - Fix: `sqlalchemy.url` oder Runtime-URL via Env/DATABASE_URL korrekt gesetzt.
- **ENUM-Duplikate**:
  - Fehler: `psycopg.errors.DuplicateObject: type "task_status" already exists`
  - Ursache: implizites `CREATE TYPE` durch `sa.Enum(...)` beim Tabellen-Create.
  - Fix: Migration auf **idempotente** ENUM-Erzeugung umgebaut:
    ```sql
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
        CREATE TYPE task_status AS ENUM ('open','doing','done');
      END IF;
    END $$;
    ```
    und Spalten verwenden `postgresql.ENUM(name='task_status', create_type=False)`.

### Step 4 — Angular Dev in Docker + Proxy
**Ziele**: Frontend-Grundlage, Live-Reload, Proxy zu API.

- Angular-App im Ordner `ui/` erstellt.
  - Hinweis: Korrekte CLI-Initialisierung ist
    - `npm create @angular@latest ui -- --routing --style=scss --skip-git --strict`
    - **oder** `npx -y @angular/cli@latest new ui --routing --style=scss --skip-git --strict`
    - (Fehlerfall war: `npm create @angular/cli@latest …` → 404)
- `ui/Dockerfile.dev` + `ui/proxy.conf.json` (`/api` → `http://api:8080`).
- Compose-Service **ui** ergänzt (Port 4200, Volume-Mount + persistente `node_modules` im Container).
- Frontend erreichbar: `http://localhost:4200` (Angular-Willkommensseite).

---

## Typische Fehler & Lösungen (Chronik)

1) **Docker-CLI in zsh nicht gefunden**
   - Symptome: `which -a docker` → not found; `com.docker.cli` Pfad passte nicht.
   - Fix: Pfad korrigiert bzw. `/Applications/Docker.app/Contents/Resources/bin` in `PATH` und/oder Desktop starten.

2) **Registry-Auth / Credential Helper**
   - Fehler: `error getting credentials - docker-credential-desktop not found`
   - Workaround: Basisimages manuell ziehen (`docker pull python:3.12-slim`) und anschließend Build.

3) **Alembic-Probleme (s. Step 3 oben)**
   - `ModuleNotFoundError: app`
   - `KeyError: 'formatters'`
   - `KeyError: 'url'`
   - `DuplicateObject: type "task_status"` → ENUM-Handling idempotent + `create_type=False`

4) **Git-Repo versehentlich entfernt**
   - Ursache: `rsync -a --delete SOURCE/ ./` ohne `--exclude='.git'`.
   - Fix: Repo neu initialisiert, Commits/Tags erneut erstellt; Merkhilfe siehe unten.

5) **Alte Git-Version**
   - `git init -b main` schlug fehl.
   - Fix: Homebrew-Installation `brew install git` + `brew link git`, Version jetzt `2.51.0`.

6) **Angular-CLI Aufruf**
   - Falscher Befehl verursachte 404 im npm-Registry-Request.
   - Fix: `npm create @angular@latest …` oder `npx @angular/cli@latest new …` verwenden.

---

## Start (aktueller Stand, Step 4)

```bash
cp .env.example .env
docker compose up --build
```

- Angular: `http://localhost:4200`
- Swagger: `http://localhost:8080/docs`
- Health: `http://localhost:8080/health`

**Root-404 ist normal** (kein Handler auf `/`). Optionaler Redirect in `api/app/main.py`:
```python
from fastapi.responses import RedirectResponse
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
```

---

## Projektstruktur (Kurzüberblick)

```
.
├─ api/
│  ├─ app/                 # FastAPI Code (Router, Schemas, DB, Services)
│  ├─ alembic/             # Migrationen
│  ├─ alembic.ini
│  ├─ Dockerfile
│  ├─ entrypoint.sh
│  └─ requirements.txt
├─ ui/                     # Angular App (Docker Dev)
│  ├─ proxy.conf.json
│  └─ Dockerfile.dev
├─ compose.yaml            # db + api + ui
├─ .env.example            # Beispiel-Env
├─ .env                    # (NICHT committen)
└─ docs/                   # Spezifikationen & Architektur
```

---

## Git: Vorgehen & Merkhilfen

- **Repo neu initialisieren** (falls nötig):
  ```bash
  rm -rf .git
  git init -b main
  ```

- **Stände einspielen** (Beispiel mit rsync):
  ```bash
  rsync -a --delete --exclude='.git' /pfad/zu/stepX/ ./
  git add . && git commit -m "stepX: ..."
  git tag -a stepX -m "Step X"
  ```

- **Upstream setzen & pushen**:
  ```bash
  git remote add origin https://github.com/oliverkarst/TaskMgr-VibeCode-ChatGPT5.git
  git push -u origin main
  git push origin --tags
  ```

- **Pager beenden**: `q` in `git log` (Standard-Pager `less`).

---

## Nächste Schritte (Step 5 ff.)

- **Step 5**: Angular-UI mit API-Anbindung (Liste, Anlegen, Bearbeiten, Löschen).
- **Step 6**: AuthN/AuthZ (z. B. JWT, Basic RBAC).
- **Step 7**: CI (GitHub Actions), Container-Registry (GHCR), optional Preview-Deploy.
- **Step 8**: Prod-Build Angular (ng build), Nginx-Container für statische Auslieferung, CORS/Proxy für Prod.
- **Step 9**: Skalierung: `replicas`, Healthchecks, DB-Tuning / Connection-Pool, evtl. Helm/K8s.

---

## Troubleshooting (Kurzreferenz)

- **DB resetten**: `docker compose down -v && docker compose up --build`
- **Port belegt**:
  - API: `8080:8080` → `8081:8080`
  - UI: `4200:4200` → `4300:4200`
- **Angular Dependencies zicken**:
  ```bash
  docker compose stop ui
  docker volume rm $(docker volume ls -q | grep node_modules) 2>/dev/null || true
  docker compose up --build ui
  ```

---

## Danksagung / Methodik

Die Umsetzung erfolgte „VibeCoding“-artig in kleinen, überprüfbaren Schritten. Probleme wurden unmittelbar behoben und dokumentiert. So bleibt das Projekt stets lauffähig und verständlich.
