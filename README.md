[![Python](https://img.shields.io/badge/python-3.15-blue?style=flat-square)](https://www.python.org/downloads/release/python-3150/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
# Whoops

Whoops is a simple Flask application that imports your Whoop data into a PostgreSQL or MySQL database.  

**Features:**

- Manual and daily imports.
- Automatic API token refresh.

## Requirements

- Docker (or a Kubernetes cluster)
- A Whoop API **Client ID** and **Client Secret** from the [Whoop Developer Dashboard](https://developer-dashboard.whoop.com/)

> [!NOTE]
> The redirect URL configured for your Whoop app must match the URL where Whoops will run (e.g., `http://localhost:5000/callback`).

> [!NOTE]
> `SECRET_KEY` is required and must be provided via the environment. Generate one with:
> ```bash
> python -c 'import secrets; print(secrets.token_hex(32))'
> ```

# Getting Started

Example Docker compose file and kubernetes manifests are provided in the [templates](https://github.com/kryoseu/whoops/tree/main/templates) section, which also include how to install a database along with Whoops, in case you don't have one yet.

## With Docker

Using Docker compose:

```yaml
services:
  whoops:
    image: docker.io/szpaczyn/whoops:latest
    container_name: whoops
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      CLIENT_ID: "<your-whoop-client-id-here"
      CLIENT_SECRET: "<your-whoop-client-secret-here"
      REDIRECT_URI: "http://localhost:5000/callback"
      SQLALCHEMY_DATABASE_URI: "postgresql+psycopg2://whoops:whoops@127.0.0.1:5432/whoop_data"
      SECRET_KEY: "<a-long-random-string>"
    restart: unless-stopped
```

or Docker run:

```bash
docker run -d \
  --name whoops \
  --network host \
  -e CLIENT_ID="<your-whoop-client-id>" \
  -e CLIENT_SECRET="<your-whoop-client-secret>" \
  -e REDIRECT_URI="http://localhost:5000/callback" \
  -e SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://whoops:whoops@127.0.0.1:5432/whoop_data" \
  -e SECRET_KEY="<a-long-random-string>" \
  docker.io/szpaczyn/whoops:latest
```

`--network host` publishes port 5000 on every interface of the host. Block it with a firewall, or use the compose file above.

Update `SQLALCHEMY_DATABASE_URI` depending on your database:

- PostgreSQL: `postgresql+psycopg2://<user>:<password>@<host>:5432/whoop_data`
- MySQL: `mysql+pymysql://<user>:<password>@<host>:3306/whoop_data`

# Kubernetes (Helm)

For Kubernetes deployments, use the Helm chart in the
[rpi-k3s](https://github.com/szpaczyna/rpi-k3s) repository:
`cluster/helm/whoops`. `templates/kubernetes.yaml` is a plain-manifest version
of the same chart: a `whoops-env` Secret, Service, Deployment and Gateway API
`HTTPRoute`.

# Usage

> [!NOTE]
> OAuth tokens and the daily import time are persisted in the database, so
> restarting the application does not require re-authorization or
> rescheduling. Tokens are refreshed automatically before they expire.

> [!NOTE]
> Whoops has no login. Anyone who can reach port 5000 can read your data and link the app to a different Whoop account. Keep it on localhost, or put it behind a reverse proxy or Ingress that requires authentication.

1. Navigate to [http://localhost:5000/authorize](http://localhost:5000/authorize) to authorize Whoops to access your Whoop data.
2. Navigate to [http://localhost:5000](http://localhost:5000) to set when import job runs, disable it, or trigger a manual import.

> [!TIP]
> The scheduled daily import fetches the last `INCREMENTAL_IMPORT_DAYS` days
> (default 7, override with `FLASK_INCREMENTAL_IMPORT_DAYS`) and updates records
> that Whoop rescored. "Import Now" fetches the full history.

# Visualizing Your Data

## Whoops UI (Recommended for a Simple Setup)

For a lightweight, purpose-built UI to explore your Whoop metrics, you can use [whoops-ui](https://github.com/kryoseu/whoops-ui).

`whoops-ui` retrieves data directly from `whoops` or the Whoop API and provides a clean web interface for exploring and visualizing your data, including support for custom graphs and dashboards—without requiring Grafana.

## Grafana

If you have [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) installed, you can import the provided [dashboard](https://grafana.com/grafana/dashboards/25022-whoops-recovery-sleep-insights/) to visualize your Whoop data.

<img width="1249" height="1222" alt="260317_11h15m30s_screenshot" src="https://github.com/user-attachments/assets/b726578d-9b30-472b-a51f-249d2ddb84cc" />


Thank you for your support! 💛

## Star History

<a href="https://www.star-history.com/?repos=kryoseu%2Fwhoops&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=kryoseu/whoops&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=kryoseu/whoops&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=kryoseu/whoops&type=date&legend=top-left" />
 </picture>
</a>
