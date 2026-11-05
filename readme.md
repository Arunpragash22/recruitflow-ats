# RecruitFlow ATS

**A containerized Applicant Tracking System (ATS) built with FastAPI, PostgreSQL, Docker Compose, and GitHub Actions.**

RecruitFlow ATS is a small recruitment workflow application developed as a Platform Engineer take-home exercise. Its primary purpose is to demonstrate repeatable application packaging, service orchestration, persistent data storage, automated integration testing, and a foundation for cloud deployment—not to provide a production-ready recruitment platform.

> **Deployment status:** The local Docker Compose environment and GitHub Actions CI have been verified. Add the public Railway URL below only after the deployment has been completed and tested.
>
> **Live demo:** `https://<YOUR-RAILWAY-DOMAIN>` *(replace after deployment)*
>
> **Repository:** [Arunpragash22/recruitflow-ats](https://github.com/Arunpragash22/recruitflow-ats) *(private repository; access requires an invitation)*

## 1. Features

- View candidates in a browser-based dashboard.
- Add candidates with a name and applied position.
- Search candidates by name or position.
- Update application status: **Applied**, **Screening**, **Interview**, **Hired**, or **Rejected**.
- Retrieve candidate data through a JSON API.
- Store candidate records persistently in PostgreSQL.
- Run the application and database as separate Docker Compose services.
- Run automated HTTP integration tests with Pytest and HTTPX.
- Build and test the application through GitHub Actions.

**Scope:** This is a demonstration application. It currently has no authentication, authorization, audit trail, or applicant-data privacy workflow. Do not use real candidate personal data or expose it publicly without appropriate protections.

## 2. Technology stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python, FastAPI | Web routes and JSON API |
| Templates | Jinja2, HTML | Server-rendered dashboard |
| Persistence | PostgreSQL 17 | Relational candidate storage |
| ORM | SQLAlchemy | Database mapping and queries |
| Database driver | Psycopg | PostgreSQL connectivity |
| Packaging | Docker | Reproducible application image |
| Orchestration | Docker Compose | Local application/database lifecycle |
| Tests | Pytest, HTTPX | HTTP integration checks |
| CI | GitHub Actions | Automated build and test on push/PR |
| Hosting (planned) | Railway | Hosted application and PostgreSQL |

## 3. Architecture

### Local development

```text
Browser / HTTP client
        |
        | http://127.0.0.1:8000
        v
+-------------------------------+
| Docker Compose: web service   |
| FastAPI + Jinja2 + SQLAlchemy |
+-------------------------------+
        |
        | DATABASE_URL
        | db:5432 (internal network)
        v
+-------------------------------+
| Docker Compose: db service    |
| PostgreSQL 17                 |
+-------------------------------+
        |
        v
Named Docker volume: postgres_data
```

The application and database communicate on Docker Compose's internal network. The application connects using the service hostname `db`, not `localhost`. The PostgreSQL port does not need to be published to the host for the containerized application to use it.

### Planned Railway deployment

```text
Public URL -> Railway FastAPI service -> Railway PostgreSQL service
                       |
                       +-- DATABASE_URL environment variable

GitHub push/PR -> GitHub Actions -> Docker build + integration tests
```

**CI and deployment are distinct:** the current GitHub Actions workflow validates the application; it does not itself deploy to Railway. If Railway's GitHub integration is enabled, Railway handles deployments from the connected repository independently. Configure branch and deployment settings explicitly.

## 4. Repository structure

```text
recruitflow-ats/
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
├── templates/
│   └── dashboard.html       # Dashboard template
├── tests/
│   └── test_app.py          # HTTP integration tests
├── .dockerignore            # Exclusions from Docker build context
├── .env.example             # Example configuration (no secrets)
├── .gitignore               # Exclusions from Git
├── Dockerfile               # FastAPI container image
├── compose.yaml             # Web + PostgreSQL services
├── database.py              # SQLAlchemy engine and session
├── main.py                  # FastAPI routes and application lifecycle
├── models.py                # Candidate ORM model
└── requirements.txt         # Application dependencies
```

A `README.md` is added as project documentation. Additional assets or configuration files may be introduced as the project evolves.

## 5. Prerequisites

For the recommended containerized setup:

- Git
- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux)
- An available local TCP port **8000**

Python is not required on the host to run the application through Docker Compose. To run the integration tests directly on the host, install Python and the test dependencies separately.

## 6. Run locally with Docker Compose

### 6.1 Clone the repository

```bash
git clone https://github.com/Arunpragash22/recruitflow-ats.git
cd recruitflow-ats
```

Because the repository is private, GitHub authentication and repository access are required.

### 6.2 Create environment configuration

Copy the example file:

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Edit `.env` and set a strong, unique local database password:

```dotenv
POSTGRES_PASSWORD=replace_with_a_strong_local_password
```

Never commit `.env` or production credentials. `.env.example` must contain only example values.

### 6.3 Start the services

```bash
docker compose up --build -d
```

Check their status:

```bash
docker compose ps
```

The `db` service should report **healthy** and the `web` service should report **running**.

### 6.4 Open the application

- Dashboard: <http://127.0.0.1:8000/>
- Candidate API: <http://127.0.0.1:8000/api/candidates>
- Health endpoint: <http://127.0.0.1:8000/health>
- API documentation: <http://127.0.0.1:8000/docs>

Use fictional names and positions when testing.

### 6.5 View logs

```bash
docker compose logs -f web
```

For database logs:

```bash
docker compose logs -f db
```

### 6.6 Stop or restart

```bash
docker compose down
docker compose up -d
```

The named PostgreSQL volume remains in place, so candidate records survive ordinary container removal and recreation.

**Data-loss warning:** Do **not** use `docker compose down -v` unless you intentionally want to remove the project's named volumes and their stored database data.

## 7. Database configuration and persistence

The application reads its connection string from the `DATABASE_URL` environment variable. `compose.yaml` supplies a URL using the Docker service hostname:

```text
postgresql+psycopg://atsuser:${POSTGRES_PASSWORD}@db:5432/recruitflow
```

Here, `db` is the Compose service name and `5432` is the database's internal port. The password is provided by the local `.env` file rather than hardcoded in source code.

The current FastAPI application initializes missing tables with SQLAlchemy `Base.metadata.create_all()` during startup. This is sufficient for a small demonstration but **is not a substitute for versioned database migrations**. A production evolution should introduce Alembic migrations.

### Inspect stored candidates

```bash
docker compose exec db psql -U atsuser -d recruitflow -c "SELECT id, name, position, status FROM candidates;"
```

### Persistence verification performed

Two test candidate records remained available after executing `docker compose down` followed by `docker compose up -d`. This confirms that the local Compose configuration retains PostgreSQL data across normal container recreation.

## 8. Application endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Render the candidate dashboard; optional `search` query parameter |
| POST | `/candidates/add` | Create a candidate using form fields `name` and `position` |
| POST | `/candidates/{candidate_id}/status` | Update candidate status using form field `status` |
| GET | `/api/candidates` | Return candidate records as JSON |
| GET | `/health` | Return a basic application health response |
| GET | `/docs` | Display FastAPI's interactive API documentation |

The `/health` endpoint currently reports application process health; it does not perform a database readiness query. A more robust production readiness endpoint should check database connectivity.

## 9. Automated testing

The repository contains HTTP integration tests in `tests/test_app.py`. They run against a **running application** at `http://127.0.0.1:8000`.

The current tests cover:

1. Health endpoint returns HTTP 200 and expected JSON.
2. Dashboard returns HTTP 200.
3. Candidate API returns HTTP 200 and a JSON list.
4. Invalid candidate status returns HTTP 400.

### Run tests locally

Start Docker Compose first:

```bash
docker compose up -d
```

Install the testing dependencies in a Python environment:

```bash
python -m pip install pytest httpx
```

Then run:

```bash
python -m pytest tests/ -v
```

**Verified local result:** 4 tests passed.

**Testing limitations:** The current tests do not cover candidate creation, status updates with valid values, authorization, concurrent access, or migrations. They depend on an externally running application and are not isolated unit tests. Expanding the suite with a dedicated test database and fixtures is recommended.

## 10. GitHub Actions continuous integration

The workflow is defined in `.github/workflows/ci.yml` and runs on repository pushes and pull requests, with manual execution also available.

The pipeline:

1. Checks out the repository.
2. Creates temporary CI environment configuration.
3. Builds and starts the FastAPI and PostgreSQL containers using Docker Compose.
4. Installs Python and the HTTP test dependencies.
5. Runs `pytest` against the running application.
6. Collects container logs if a step fails.
7. Stops containers after execution.

**Verified result:** The initial GitHub Actions workflow completed successfully on branch `main` for commit `4e80295` (approximately 35 seconds).

This is a **CI pipeline**, not a complete deployment pipeline: deployment to Railway is configured separately. To strengthen release safety, production deployment should be gated on successful CI and appropriate review/approval rules.

## 11. Railway deployment (complete after deploying)

> This section describes the intended setup. Do not mark the application as deployed or publish a demo URL until the live service has been tested.

### 11.1 Create the project

1. Sign in to Railway and create a project.
2. Add a PostgreSQL service.
3. Add an application service from the private GitHub repository `Arunpragash22/recruitflow-ats`.
4. Configure the application to build from the existing `Dockerfile`.

### 11.2 Configure environment variables

Set `DATABASE_URL` in the application service using a Railway reference to the PostgreSQL service's connection details. SQLAlchemy with Psycopg expects the driver form:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Do not paste real passwords into this README or Git. Confirm the precise variable reference and connection scheme in Railway's dashboard before deployment.

The Dockerfile currently starts Uvicorn on port `8000` and binds to `0.0.0.0`. Configure Railway's service networking/public domain to route traffic to the correct application port, and verify the deployed `/health` endpoint.

### 11.3 Validate the live deployment

After Railway reports the service as running:

- Open the public URL and confirm the dashboard loads.
- Open `/health` and `/api/candidates`.
- Add **fictional** test candidate data and verify it is stored in hosted PostgreSQL.
- Restart/redeploy the application and verify the test data remains available.
- Check deployment logs for database or startup errors.
- Confirm that access protection is in place before using any real applicant information.

**Live URL:** `https://<YOUR-RAILWAY-DOMAIN>` *(replace with the actual URL)*

**Deployment status:** Pending verification.

## 12. Security and privacy

Security decisions already reflected in the local setup include:

- Database credentials are supplied through environment variables rather than committed source code.
- `.env` and the local Python virtual environment are excluded from Git.
- The Docker application runs under a non-root user.
- The PostgreSQL service communicates over the internal Compose network without requiring a host-exposed database port.
- Form status updates reject unknown status values.

**Important limitations:**

- The application has **no authentication or role-based access control**.
- It does not currently enforce user-level access to candidate data.
- The basic health check does not verify the database.
- It does not include rate limiting, an audit log, backup/restore automation, or a data-retention policy.
- The demonstration CI configuration uses temporary test credentials; production secrets must be managed through the hosting platform.

Until access controls and privacy safeguards are implemented, use only fictional candidate data. A public URL alone is not evidence of production readiness.

## 13. Design decisions and trade-offs

### FastAPI

FastAPI provides a lightweight Python web framework, simple routing, validation, and built-in API documentation. It keeps the sample application small so attention can be focused on packaging and deployment.

### PostgreSQL and SQLAlchemy

PostgreSQL provides persistent relational storage. SQLAlchemy separates database operations from HTTP routes and provides a clear path toward more structured data access. For simplicity, the initial schema is created at startup; versioned migrations are future work.

### Docker and Docker Compose

Docker packages application dependencies into a repeatable runtime. Compose defines the application/database relationship, networking, health-based startup ordering, and named persistent volume in a single file. This reduces manual setup and improves reproducibility for reviewers.

### GitHub Actions

CI validates the containerized application in a fresh runner environment rather than relying only on local machine state. The current checks provide a useful baseline, but stronger coverage and deployment gating are needed for production.

### Railway (planned)

Railway is intended to host the application and PostgreSQL with environment-based configuration. This simplifies demonstration deployment while preserving separation between the web and database services. Hosting costs, resource limits, backups, and operational controls should be reviewed against the selected Railway plan.

## 14. Assumptions

- The system is a small demonstration with one candidate table and a limited set of statuses.
- Candidate names and positions used during evaluation are fictional.
- The local deployment is run using Docker Compose.
- A single application instance is sufficient for the exercise.
- The repository remains private and access is explicitly granted to the reviewer.
- Public deployment is for evaluation, not real recruitment operations.

## 15. Known limitations and future improvements

| Area | Current limitation | Recommended improvement |
|---|---|---|
| Access | No login or authorization | Add authentication and role-based permissions |
| Schema | Startup table creation | Add Alembic migrations |
| Testing | Four basic HTTP checks | Add CRUD, failure, security, and persistence tests with isolated fixtures |
| Health | Process-only health endpoint | Add database readiness check |
| Observability | Container logs | Add structured logging, metrics, and alerting |
| Operations | No documented backups | Add automated backups and restore tests |
| Delivery | CI and hosting separate | Gate deployment on successful CI |
| Privacy | No retention or audit controls | Add retention policy, audit events, and privacy protections |
| Reliability | Single-instance demonstration | Define scaling and recovery requirements |

## 16. Troubleshooting

**Application does not start:**

```bash
docker compose ps
docker compose logs web --tail=100
```

Check that the database is healthy and that the `DATABASE_URL` uses `db:5432` inside Docker Compose.

**Database table is missing:**

Check application startup logs and verify that the ORM model is imported before SQLAlchemy initializes the schema. Avoid manually deleting database volumes during troubleshooting.

**Candidate records disappear after restart:**

Check whether the application uses SQLAlchemy rather than an in-memory Python list, and confirm the Compose PostgreSQL volume is retained.

**Tests fail with connection errors:**

Ensure Docker Compose is running and the dashboard is accessible at `http://127.0.0.1:8000` before running the host-based HTTP tests.

**GitHub Actions fails:**

Open the failed workflow step, inspect its logs, and check Docker build output, environment variables, service health, and test connectivity.

## 17. Reviewer quick start

```bash
git clone https://github.com/Arunpragash22/recruitflow-ats.git
cd recruitflow-ats
cp .env.example .env
# Edit .env to set a strong POSTGRES_PASSWORD
docker compose up --build -d
```

Open <http://127.0.0.1:8000/>. To run tests, install `pytest` and `httpx` in a local Python environment and execute:

```bash
python -m pytest tests/ -v
```

To stop the application without removing its stored database records:

```bash
docker compose down
```

---

**Project:** RecruitFlow ATS  
**Repository:** [github.com/Arunpragash22/recruitflow-ats](https://github.com/Arunpragash22/recruitflow-ats)  
**Purpose:** Platform Engineer take-home assignment  
**Status:** Local application and CI verified; Railway deployment pending confirmation.
