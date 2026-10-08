# Event Relay

> A FastAPI backend for managing multi-channel notification delivery workflows.

Event Relay is designed to manage user notifications across delivery channels
with explicit delivery states, retries, traceability and asynchronous
processing capabilities.

## Current stack

- **FastAPI** — REST API and dependency management
- **Pydantic** — request and response validation
- **SQLAlchemy** — persistence layer
- **SQLite** — local relational database during the first iterations

## Architecture

The project follows a **feature-oriented modular monolith**. Each feature is
organized around explicit responsibilities:

```text
src/app/
├── api/            # API versioning and route composition
├── db/             # Engine, sessions and ORM base
├── users/          # User models, schemas, services and routes
├── schedules/      # Schedule models, schemas, services and routes
├── notifications/  # Notification domain and delivery lifecycle (in progress)
├── exceptions/     # Shared exception handling
└── main.py         # Application composition and lifespan
```

HTTP concerns stay in routers, business rules belong in services, and database
mapping remains in models. The platform is structured to support external
delivery providers, retry policies, SQS workers, authentication, Docker,
testing and database migrations.

## Run locally

```bash
uv sync
uv run fastapi dev src/app/main.py
```

The API is then available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Delivery lifecycle

The notification module models queueing, active processing, scheduled retries,
terminal failures, successful delivery, cancellation and retry traceability.
Asynchronous queue processing will be integrated through SQS workers.

---

Built for reliable notification delivery.
