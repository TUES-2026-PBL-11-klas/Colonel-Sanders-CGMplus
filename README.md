# Colonel-Sanders-CGMplus Local Dev

This repository is currently configured for local development with only core runtime components:

- GTFS service
- Auth service
- Auth Postgres database
- NGINX ingress controller

No local observability stack is included in this mode (no Prometheus, Grafana, Loki, or Promtail).

## Local Architecture

- [docker-compose.yaml](docker-compose.yaml): starts the local stack
- [ops/local/nginx/nginx.conf](ops/local/nginx/nginx.conf): ingress routing rules
- [services/gtfs](services/gtfs): GTFS service source and Docker build
- [services/auth-new](services/auth-new): Auth service source and Docker build

## Ports

- `8080` -> ingress entrypoint (all API traffic should go through this)
- `5432` -> used internally by `auth-db` container (not published to host)
- `5000` -> used internally by `gtfs` and `auth` containers (not published to host)

Only `8080` is exposed on the host machine.

## Local Routes Through Ingress

All requests should go to `http://localhost:8080`.

- `/auth/*` -> Auth service
- `/users/*` -> Auth service
- `/health/auth` -> Auth health check (`/health`)
- `/api/v1/*` -> GTFS service
- `/health/` -> GTFS health check
- `/` -> GTFS root/docs route

## Environment Variables

Create a root `.env` file (not committed) with at least:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `JWT_SECRET`

Example values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=auth_db
JWT_SECRET=local-dev-jwt-secret
```

## Run Local Dev

```bash
docker compose up --build -d
```

## Verify

- `http://localhost:8080/health/` should return GTFS health
- `http://localhost:8080/health/auth` should return Auth health

## Stop

```bash
docker compose down
```

To also remove the auth database volume:

```bash
docker compose down -v
```
