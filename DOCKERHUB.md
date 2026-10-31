# Whoops

Whoops imports your Whoop data (cycles, sleep, recovery, workouts) into
PostgreSQL or MySQL.

## Features
- Manual and scheduled imports (APScheduler)
- Automatic OAuth2 token refresh
- REST API (`/api/v1/whoop/...`) for cycles, sleep, recovery, workouts,
  user profile and body measurements
- Web UI for authorization and scheduling

## Quick start

```bash
docker run -d --name whoops --network host \
  -e CLIENT_ID="<your-whoop-client-id>" \
  -e CLIENT_SECRET="<your-whoop-client-secret>" \
  -e REDIRECT_URI="http://localhost:5000/callback" \
  -e SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://whoops:whoops@127.0.0.1:5432/whoop_data" \
  -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  docker.io/<user>/whoops:latest
```

Then open http://localhost:5000/authorize to grant access.

## Image details
- Base: python:3.15-alpine
- Entrypoint: `python -m src.main` (waitress, port 5000)
- Required env vars: CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
  SQLALCHEMY_DATABASE_URI, SECRET_KEY

## Links
- Source: https://github.com/szpaczyna/whoops
- Helm chart: https://github.com/szpaczyna/rpi-k3s/tree/main/cluster/helm/whoops
