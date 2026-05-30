# OurNeZt Deploy

Deployment assets for the OurNeZt stack:
- `OurNeZt-core` (gRPC backend)
- `OurNeZt-web` (Gin web app)
- PostgreSQL

This repo now supports:
- Local development with Docker Compose
- Kubernetes deployment with one unified Helm chart (`charts/ournezt`)

## Structure

```text
.
|-- .env.example
|-- docker-compose.yml
`-- charts
    `-- ournezt
```

`charts/ournezt` is the chart for deploying the full stack.

## Local Development (Docker Compose)

The compose file builds app images from sibling repos:
- `../OurNeZt-core`
- `../OurNeZt-web`

### 1) Configure env

```powershell
Set-Location E:\OurNeZt\02-Apps\OurNeZt-deploy
Copy-Item .env.example .env
```

### 2) Start full stack

```powershell
docker compose up -d --build
```

### 3) Check logs

```powershell
docker compose logs -f postgres core web
```

### 4) Access app

- Web: `http://localhost:8080`
- Core gRPC: `localhost:50051`
- Postgres: `localhost:5432`

### 5) Stop

```powershell
docker compose down
```

## Kubernetes (Unified Helm Chart)

Main chart: `charts/ournezt`

### 1) Create prod values

Example `values-prod.yaml`:

```yaml
global:
  appEnv: production

postgres:
  auth:
    database: ournezt
    username: ournezt
    password: "replace-with-strong-password"
  persistence:
    enabled: true
    storageClassName: "standard"
    size: 50Gi

core:
  image:
    repository: ghcr.io/<org>/ournezt-core
    tag: v0.1.0
  runMigrations: "true"
  bootstrap:
    enabled: false

web:
  image:
    repository: ghcr.io/<org>/ournezt-web
    tag: v0.1.0
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: app.example.com
        paths:
          - path: /
            pathType: Prefix
```

### 2) Install / upgrade

```bash
helm upgrade --install ournezt ./charts/ournezt \
  --namespace ournezt \
  --create-namespace \
  -f values-prod.yaml
```

### 3) Optional secrets pattern

For postgres password, use a pre-created secret:

```yaml
postgres:
  auth:
    existingSecret: ournezt-postgres-secret
    passwordKey: POSTGRES_PASSWORD
```

```bash
kubectl -n ournezt create secret generic ournezt-postgres-secret \
  --from-literal=POSTGRES_PASSWORD='<strong-password>'
```

For bootstrap admin password:

```yaml
core:
  bootstrap:
    enabled: true
    adminEmail: admin@example.com
    adminDisplayName: Admin
    existingSecret: ournezt-core-bootstrap
    passwordKey: BOOTSTRAP_ADMIN_PASSWORD
```

```bash
kubectl -n ournezt create secret generic ournezt-core-bootstrap \
  --from-literal=BOOTSTRAP_ADMIN_PASSWORD='<strong-password>'
```
