# TaskMgr-VibeCode-ChatGPT5 — Step 4 (API + Angular Dev in Docker)

Eine kleine Tasks/ToDo-App als Lernprojekt mit **FastAPI (Python)**, **PostgreSQL** und **Angular**.  
**Step 4** ergänzt ein dockerisiertes Angular-Frontend (mit Live-Reload) und Proxy auf das Backend.

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

## Voraussetzungen

- Docker Desktop (Compose v2)
- Keine lokale Node/Python-Installation nötig (optional für VS Code Komfort)

---

## Schnellstart

```bash
# .env anlegen (falls noch nicht vorhanden)
cp .env.example .env

# Alle Services bauen & starten
docker compose up --build
```

- Angular: http://localhost:4200  
- Swagger UI: http://localhost:8080/docs  
- Health: http://localhost:8080/health

### Smoke-Tests (Backend)
```bash
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/api/v1/tasks   -H 'Content-Type: application/json'   -d '{"title":"Persistenter Task","priority":"high"}'
curl -s http://localhost:8080/api/v1/tasks
```

---

## Wichtige Endpunkte

- **Swagger UI**: `http://localhost:8080/docs`
- **OpenAPI JSON**: `http://localhost:8080/openapi.json`
- **Health**: `GET /health`
- **Tasks API (Beispiele)**  
  - `GET /api/v1/tasks` (Liste, mit Pagination)  
  - `POST /api/v1/tasks` (Task anlegen)  
  - `GET /api/v1/tasks/{id}`  
  - `PATCH /api/v1/tasks/{id}`  
  - `DELETE /api/v1/tasks/{id}`

Im Frontend (Step 5) greifen wir auf **`/api/...`** zu — der Dev-Proxy leitet ins Backend.

---

## Projektstruktur (Step 4)

```
.
├─ api/                      # FastAPI-Anwendung (Dockerized)
│  ├─ app/                   # Code (Routers, Schemas, DB, Services)
│  ├─ alembic/               # Migrationen
│  ├─ alembic.ini
│  ├─ Dockerfile
│  ├─ entrypoint.sh
│  └─ requirements.txt
├─ ui/                       # Angular-App (Docker Dev)
│  ├─ proxy.conf.json        # Proxy /api → http://api:8080
│  └─ Dockerfile.dev
├─ compose.yaml              # db + api + ui
├─ .env.example              # Beispiel-Env
├─ .env                      # (nicht eingecheckt)
└─ docs/                     # Spezifikationen, Architektur-Notizen
```

---

## Compose-Services (Auszug)

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-tasksdb}
      POSTGRES_USER: ${POSTGRES_USER:-tasks}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-tasks}
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-tasks} -d ${POSTGRES_DB:-tasksdb}"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    environment:
      LOG_LEVEL: info
      DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg://tasks:tasks@db:5432/tasksdb}
      PYTHONPATH: /app
    depends_on:
      db:
        condition: service_healthy
    ports: ["8080:8080"]
    command: ["/bin/sh", "-c", "./entrypoint.sh"]

  ui:
    build:
      context: ./ui
      dockerfile: Dockerfile.dev
    working_dir: /usr/src/app
    command: >
      sh -c "npm ci &&
             npm run start -- --host 0.0.0.0 --port 4200 --proxy-config proxy.conf.json"
    environment:
      CHOKIDAR_USEPOLLING: "true"
    ports: ["4200:4200"]
    volumes:
      - ./ui:/usr/src/app
      - /usr/src/app/node_modules
    depends_on:
      - api

volumes:
  pgdata:
```

---

## Environment

Standardwerte sind in `compose.yaml`/`api` bereits gesetzt.  
Du kannst `DATABASE_URL` in `.env` überschreiben:

```ini
# .env
POSTGRES_DB=tasksdb
POSTGRES_USER=tasks
POSTGRES_PASSWORD=tasks
DATABASE_URL=postgresql+psycopg://tasks:tasks@db:5432/tasksdb
```

> **Achtung:** `.env` niemals committen (ist in `.gitignore`).

---

## Häufige Probleme & Tipps

- **Port belegt**  
  - API: ändere Mapping `8080:8080` → z. B. `8081:8080`  
  - UI: ändere `4200:4200` → z. B. `4300:4200`

- **DB „verschmutzt“ / Migrationsfehler**  
  ```bash
  docker compose down -v   # Vorsicht: löscht DB-Volume!
  docker compose up --build
  ```

- **Angular Dependency-Cache spinnt**  
  ```bash
  docker compose stop ui
  docker volume rm $(docker volume ls -q | grep node_modules) 2>/dev/null || true
  docker compose up --build ui
  ```

- **Root 404 in API**  
  `GET /` ist nicht belegt → nutze `/docs` oder `/health`.  
  Optionaler Redirect:
  ```python
  from fastapi.responses import RedirectResponse
  @app.get("/", include_in_schema=False)
  def root():
      return RedirectResponse(url="/docs")
  ```

---

## Versionierung (Tags)

- `step1` – Projektgerüst, FastAPI + Docker  
- `step2` – In-Memory CRUD + OpenAPI  
- `step3` – PostgreSQL + Alembic, Fixes, Smoketest grün  
- **`step4` – Angular Dev in Docker (dieser Stand)**

Erstellen (falls noch nicht erfolgt):
```bash
git add .
git commit -m "step4: Angular-Frontend (Docker dev, Live-Reload, Proxy)"
git tag -a step4 -m "Step 4"
git push && git push --tags
```

---

## Nächste Schritte

**Step 5**: Angular-UI mit API-Anbindung (Liste, Anlegen, Bearbeiten, Löschen) — dank Proxy einfach via `/api/v1/tasks`.
