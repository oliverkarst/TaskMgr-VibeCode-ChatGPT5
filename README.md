# VibeCoding Tasks – FastAPI + Angular (Backend Step 3: PostgreSQL)

Dieses Projekt ist eine lernfreundliche Referenz-App, um **VibeCoding** im Alltag auszuprobieren – mit sauberer Architektur, OpenAPI-First und Container-Betrieb.

Bis zu diesem Stand war es von Step2 zu Step3 notwendig mehrere Bugfixes durch ChatGPT vornehmen zu lassen. Insgesamt wurde 5 mal falscher Code erzeugt. Erst danach funktionierte der Code.

## Komponenten
- **API (FastAPI, Python 3.12)** – CRUD für Tasks, OpenAPI, Alembic-Migrationen
- **DB (PostgreSQL 16)** – Persistenz, Migrations
- **Docs** – Spezifikationen & Architektur

> Frontend (Angular) folgt in einem separaten Schritt. Hier konzentrieren wir uns auf das Backend mit echter Persistenz.

## Quickstart
```bash
unzip vibecoding-tasks-fastapi-angular-step3.zip
cd vibecoding-tasks-fastapi-angular-step3
cp .env.example .env   # optional anpassen
docker compose up --build
```

- Swagger UI: http://localhost:8080/docs
- Health: http://localhost:8080/health

## Beispiel-Requests
```bash
curl -s -X POST http://localhost:8080/api/v1/tasks   -H 'Content-Type: application/json'   -d '{"title":"Erster persistenter Task","priority":"high","tags":["demo","vc"]}' | jq

curl -s "http://localhost:8080/api/v1/tasks?page=1&size=10" | jq

TASK_ID=$(curl -s http://localhost:8080/api/v1/tasks | jq -r '.items[0].id')
curl -s "http://localhost:8080/api/v1/tasks/$TASK_ID" | jq

curl -s -X PATCH "http://localhost:8080/api/v1/tasks/$TASK_ID"   -H 'Content-Type: application/json'   -d '{"status":"doing"}' | jq

curl -i -X DELETE "http://localhost:8080/api/v1/tasks/$TASK_ID"
```

## Technische Details
- **SQLAlchemy 2.0 ORM** (sync) + **psycopg 3**
- **Alembic**: automatische Migrationen beim Start (`entrypoint.sh`)
- **PostgreSQL**: Healthcheck, `pgdata` Volume
- **OpenAPI**: `docs/specs/tasks.yaml`

## Struktur
```
.
├─ api/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ db.py
│  │  ├─ models.py
│  │  └─ schemas.py
│  ├─ alembic/
│  │  ├─ versions/0001_initial.py
│  │  └─ env.py
│  ├─ alembic.ini
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ entrypoint.sh
├─ docs/
│  └─ specs/tasks.yaml
├─ compose.yaml
├─ .env.example
└─ README.md
```

## Nächste Schritte
- **Step 4: Angular-Frontend** (Scaffold & CRUD)
- Optional: Observability (OTEL, Prometheus), CI/CD.
