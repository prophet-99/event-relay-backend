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

## Docker environments

All environments run the same three application processes: the FastAPI API,
the outbox publisher and the notification-delivery worker. Copy `.env.example`
to `.env` and provide your LocalStack token and JWT secret before using the
development or QA environments.

### Development

Development mounts `src/` for FastAPI reload, exposes the API on port 8000 and
exposes LocalStack only on `127.0.0.1:4566`.

```bash
docker compose -f docker-compose-dev.yml up --build
```

Check the API at [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health).
Its SQLite data is stored in the `dev-sqlite` Docker volume.

### QA

QA runs an immutable application image, FastAPI on port 8000, both workers and
an internal LocalStack/SQS instance. It uses a SQLite volume separate from
development and intentionally does not expose LocalStack to the host.

```bash
docker compose -f docker-compose-qa.yml up --build
docker compose -f docker-compose-qa.yml down --volumes
```

### Production

Production does not include LocalStack. The deployment environment must supply
`AWS_REGION`, `SQS_QUEUE_URL`, `JWT_SECRET_KEY` and AWS credentials through its
normal credential provider or the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
and optional `AWS_SESSION_TOKEN` environment variables. SQLite remains in the persistent
`prod-sqlite` volume only until the PostgreSQL migration phase.

```bash
docker compose -f docker-compose-prod.yml up --build -d
docker compose -f docker-compose-prod.yml logs -f
```

Do not commit `.env` or deployment secrets. Stop an environment with its
matching `docker compose -f <file> down` command.

### SQS integration-test isolation

The existing SQS integration tests use the queue configured in the process
environment. Do not run them against a live development stack, whose delivery
worker consumes from that queue. Until the dedicated pytest queue is introduced
in the test-coverage phase, run those tests against an isolated LocalStack
instance and queue.

## Delivery lifecycle

The notification module models queueing, active processing, scheduled retries,
terminal failures, successful delivery, cancellation and retry traceability.
Asynchronous queue processing will be integrated through SQS workers.

---

Built for reliable notification delivery.
