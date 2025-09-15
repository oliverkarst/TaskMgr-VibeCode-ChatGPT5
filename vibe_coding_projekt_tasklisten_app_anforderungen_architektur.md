# Projekt: Tasklisten‑App (ToDo) – Fachliche Anforderungen & Architektur (v1)

## 1) Ziel & Kontext
Eine kleine, aber „realistische“ Referenz‑Applikation, um **VibeCoding** im Alltag zu erproben – mit klarem Scope, sauberer API, Container‑Betrieb und skalierbarem Deployment. Der Fokus liegt auf Architektur‑Disziplin (Testbarkeit, Observability, Security), während KI‑Assistenz (VibeCoding) für Bootstrapping und Routine‑Codierung genutzt wird – **mit Guardrails**.

## 2) Fachlicher Scope
- **User verwalten ihre persönlichen Aufgaben** („Tasks“).
- Aufgaben haben Titel, Beschreibung, Status, Fälligkeitsdatum, Priorität, Tags.
- CRUD: anlegen, lesen (listen + details), ändern, löschen.
- Filter/Suche (Status, Fälligkeit, Tag, Textsuche).
- Optional: wiederkehrende Tasks, Anhänge (Links), einfache Subtasks.
- Optional: Team‑Kontext (Multi‑Tenant: Organisation → Nutzer → Listen → Tasks).

## 3) Primäre Use Cases
1. **Task anlegen** (Pflichtfelder: Titel; optional: Beschreibung, Fälligkeit, Priorität, Tags).
2. **Task aktualisieren** (Teil‑Updates via PATCH).
3. **Task löschen** (Soft‑Delete optional).
4. **Tasks listen & filtern** (Pagination, Sortierung, Filter).
5. **Task Details ansehen**.
6. **Auth**: Registrieren/Anmelden; Session/Token erneuern; Passwort zurücksetzen.

## 4) Nicht‑funktionale Anforderungen (NFR)
- **Sicherheit**: JWT mit Rolling Tokens, RBAC (user, admin), OWASP Top 10.
- **Skalierbarkeit**: stateless Backend; DB Readiness; horizontales Scaling via K8s.
- **Zuverlässigkeit**: Idempotente Endpunkte (POST‑Dedup optional), Migrationsstrategie.
- **Beobachtbarkeit**: strukturierte Logs, Tracing (OpenTelemetry), Metriken (Prometheus), Health/Readiness‑Probes.
- **Testbarkeit**: Contract‑Tests gegen OpenAPI; E2E via Playwright; Unit/Integration.
- **Portabilität**: jeder Dienst in eigenem Container; lokale Orchestrierung via Docker Compose.
- **Compliance**: DSGVO‑konforme Datenhaltung, Audit‑Trail (optional Events).

## 5) API (OpenAPI‑First)
Base: `/api/v1`

**Auth**
- `POST /auth/register` – Account anlegen
- `POST /auth/login` – Token erhalten
- `POST /auth/refresh` – Access Token erneuern
- `POST /auth/logout`

**Tasks**
- `GET /tasks` – Liste (Query: `status`, `dueBefore`, `dueAfter`, `tag`, `q`, `page`, `size`, `sort`)
- `POST /tasks` – anlegen (Body: `title`, `description?`, `dueAt?`, `priority?`, `tags?`)
- `GET /tasks/{id}` – Details
- `PATCH /tasks/{id}` – Teil‑Update
- `DELETE /tasks/{id}` – löschen

**Tags** (optional)
- `GET /tags` | `POST /tags` | `DELETE /tags/{id}`

Konventionen: Problem+JSON Fehlerobjekte; RFC7807; konsistente Fehlercodes; ETag/If‑Match optional.

## 6) Datenmodell (relational)
- **users**(id, email UNIQUE, password_hash, created_at)
- **task_lists**(id, owner_user_id, title, created_at)  *optional*
- **tasks**(id, list_id FK→task_lists, title, description, status ENUM[open, doing, done], priority ENUM[low, normal, high], due_at, created_at, updated_at, deleted_at NULL)
- **tags**(id, owner_user_id, name)
- **task_tags**(task_id FK, tag_id FK) – M:N
- **tenants**(id, name) *optional*, **members**(tenant_id, user_id, role)

Indexes: (tasks.list_id, status), (tasks.due_at), Full‑Text Index auf title/description (DB‑abhängig).

## 7) Architekturübersicht
- **Frontend**: Angular 17 (Standalone Components) *oder* React/Next.js (TS). Auth via JWT; UI: Tabellen/Filter; Offline‑ready (PWA optional).
- **Backend**: Node.js **NestJS** *oder* Python **FastAPI**. OpenAPI‑First, JWT, Swagger‑UI, zod/pydantic‑Validation.
- **DB**: PostgreSQL 16.
- **Infra**: Docker Compose (dev); K8s (kind/minikube) + Helm (prod‑like). Reverse Proxy via Traefik oder Nginx Ingress.
- **Observability**: OTEL Collector, Prometheus, Grafana, Loki (optional).
- **CI/CD**: GitHub Actions: Lint, Test, Build Images, SBOM + Trivy Scan, Push, Helm‑Lint, Deploy to kind.

## 8) Container & Ports (Compose)
- `frontend` (Port 5173/4200 → 80 hinter Proxy)
- `api` (Port 8080)
- `db` (postgres:5432)
- `otel-collector` (4317/4318)
- `prometheus`, `grafana` (optional)
- `reverse-proxy` (Traefik/Nginx) – TLS‑Term., Routing `/` → Frontend, `/api` → Backend

## 9) Sicherheits‑Guardrails
- Secrets via `.env` + Docker Secrets; niemals im Repo.
- Input‑Validation an API‑Boundary; Rate‑Limiting; CORS‑Policy.
- SQL‑Migrations via Prisma/Knex/Alembic; Least‑Privilege‑DB‑User.
- SBOM (syft) + Vulnerability Scan (grype/trivy) im CI.

## 10) Tests & Qualität
- **Contract**: Prism/Microcks gegen OpenAPI.
- **Unit/Integration**: Jest (NestJS) oder PyTest (FastAPI) + Testcontainers (DB echt).
- **E2E/UI**: Playwright (Login, CRUD‑Flows, Filter, Fehlerfälle).
- **Load/Smoke**: k6 minimal.

## 11) VibeCoding‑Workflow (praktisch)
- **Prompt‑Vorlage** (DevSpec → Code):
  1. *Ziel/Feature*: „Implementiere `POST /tasks` mit Validierung, Fehlerformat RFC7807, Idempotency‑Key“
  2. *Architekturregeln*: Layering, DTOs, Repo‑Pattern; keine Hard‑coded‑Secrets; Logging auf INFO.
  3. *Akzeptanzkriterien*: Response‑Codes, Tests existieren/grün.
  4. *Definition of Done*: Lint ok, Tests grün, OpenAPI aktualisiert, CI grün.
- **„Trust but Verify“**: AI erzeugt Code; Mensch prüft über Tests, Contracts und Laufzeitverhalten – kein „Accept All“ in prod‑nahen Branches.

## 12) Deployment‑Strategie
- **Dev**: `docker compose up` – alles lokal.
- **Stage/Prod‑like**: kind/minikube + Helm Charts; HPA (CPU/Requests), PodDisruptionBudget, Rolling Updates; Postgres via StatefulSet (oder gemanagter Dienst in echt).
- **Config**: 12‑Factor; ENV‑Variablen; getrennte Values pro Umgebung.

## 13) Observability‑MVP
- Request‑Tracing: OpenTelemetry SDK → OTEL‑Collector → (Jaeger/Tempo)
- Metriken: HTTP Latenz/Fehlerquote; DB‑Latenz; Queue (optional).
- Logs: strukturierte JSON‑Logs; Correlation‑IDs.

## 14) Roadmap (inkrementell)
1. OpenAPI‑Spec `tasks.yaml` + Contract‑Tests.
2. Backend‑Skeleton (NestJS/FastAPI) + `/tasks` CRUD gegen Postgres + Migrations.
3. Frontend Liste/Details/CRUD + Auth‑Flow.
4. Observability‑MVP + CI/CD Pipeline + Container Security.
5. Team/Multi‑Tenant + Audit‑Trail (Event‑Sourcing optional).
6. Optional: Webhooks, Import/Export (CSV), PWA, Offline‑Sync.

## 15) Stretch‑Varianten (falls mehr „Wumms“ gewünscht)
- **Kanban‑Boards** mit Swimlanes & WIP‑Limits; Drag&Drop.
- **Reminder‑Service** (Cron/Queues) für Fälligkeiten mit E‑Mail/WebPush.
- **AI‑Features** bewusst & begrenzt: Smart‑Parsing natürlicher Sprache → Task ("Morgen 9 Uhr Kundentermin, Prio hoch, Tag #Sales").
- **Enterprise‑Twist**: RBAC je Tenant, Audit‑Events, Export für BI (Parquet/S3), Policy‑Enforcement (OPA).

---
**Entscheidung offen**: Stack‑Option A) NestJS + Angular; Option B) FastAPI + React/Next.js. Beides TS‑freundlich; wähle nach Lernziel. Für schnelle API‑Produktivität ist FastAPI sehr angenehm; für TS‑End‑to‑End ist NestJS + Angular stringent.

