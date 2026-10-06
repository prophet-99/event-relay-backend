# NotifyFlow

> A FastAPI service for managing user notifications and their delivery lifecycle.

NotifyFlow is a learning-driven backend project that evolves from a synchronous
notification flow into an asynchronous, queue-based delivery system.

## Current stack

- **FastAPI** — REST API and dependency management
- **Pydantic** — request and response validation
- **SQLAlchemy** — persistence layer
- **SQLite** — local relational database during the first iterations

## Architecture

The project follows a **feature-oriented modular monolith** with clear
responsibilities inside every feature:

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
mapping remains in models. The next iterations will add external delivery
providers, retries, SQS workers, authentication, Docker, testing and database
migrations.

## Run locally

```bash
uv sync
uv run fastapi dev src/app/main.py
```

The API is then available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Project status

Active development — the notification domain is currently being designed with
delivery states, retries, parent/clone traceability and future SQS support in
mind.

---

Built to learn the Python concepts behind production-oriented FastAPI systems.
