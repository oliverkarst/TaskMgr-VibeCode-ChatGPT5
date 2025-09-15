# VibeCoding Tasks – Step 1 (Backend minimal)

Dies ist ein minimales Starter-Setup für das Backend mit FastAPI in Docker. Ziel: **/health** läuft in einem Container.

## Voraussetzungen
- Docker Desktop / Docker Engine
- Docker Compose v2 (`docker compose`)

## Start
```bash
docker compose up --build
# oder im Hintergrund
# docker compose up -d --build
```

Danach:
- OpenAPI/Swagger UI: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

## Nächste Schritte (geplant)
- Step 2: OpenAPI-First für /tasks (Schema + Endpunkte)
- Step 3: Persistenz (PostgreSQL) + Migrations
- Step 4: Angular-Frontend Scaffold + simple CRUD
```

