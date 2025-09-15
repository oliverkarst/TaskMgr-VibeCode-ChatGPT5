# VibeCoding Tasks – Step 2 (Backend in-memory CRUD)

In diesem Schritt gibt es eine minimal nutzbare Tasks-API mit FastAPI (in-memory), plus OpenAPI-Spezifikation.

## Start
```bash
docker compose up --build
```

## Endpunkte
- Swagger UI: http://localhost:8080/docs
- Health: http://localhost:8080/health
- Liste: GET http://localhost:8080/api/v1/tasks
- Anlegen: POST http://localhost:8080/api/v1/tasks
- Details: GET http://localhost:8080/api/v1/tasks/{id}
- Patch: PATCH http://localhost:8080/api/v1/tasks/{id}
- Löschen: DELETE http://localhost:8080/api/v1/tasks/{id}

## Beispiel-Requests
```bash
# Anlegen
curl -s -X POST http://localhost:8080/api/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Erster Task","description":"Demo","priority":"high"}' | jq

# Liste
curl -s http://localhost:8080/api/v1/tasks | jq

# Einen Task (ID anpassen)
curl -s http://localhost:8080/api/v1/tasks/{id} | jq

# Patch
curl -s -X PATCH http://localhost:8080/api/v1/tasks/{id} \
  -H 'Content-Type: application/json' \
  -d '{"status":"doing"}' | jq

# Delete
curl -i -X DELETE http://localhost:8080/api/v1/tasks/{id}
```

## OpenAPI
Die Spez liegt unter `openapi/tasks.yaml` (für Contract-Tests/Clients).
```

