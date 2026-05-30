# OurNeZt Deploy

Deployment assets for OurNeZt infrastructure.

Current scope:
- PostgreSQL for local development (`docker compose`)
- PostgreSQL for production Kubernetes (`helm`)

`OurNeZt-deploy` is a solid name and aligns with your Phase 1 plan.  
If you ever want a broader infra name later, `OurNeZt-infra` is the natural alternative.

## Structure

```text
.
├── .env.example
├── docker-compose.yml
└── charts
    └── ournezt-postgres
```

## Local Dev (Docker Compose)

1. Create env file:

```powershell
Set-Location E:\OurNeZt\02-Apps\OurNeZt-deploy
Copy-Item .env.example .env
```

2. Start PostgreSQL:

```powershell
docker compose up -d postgres
```

3. Verify:

```powershell
docker compose ps
docker compose logs -f postgres
```

4. Stop:

```powershell
docker compose down
```

## Production (Helm)

### 1) Create a values file for prod secrets and storage

Example `values-prod.yaml`:

```yaml
postgres:
  database: ournezt
  username: ournezt
  password: "replace-with-strong-password"

persistence:
  enabled: true
  storageClassName: "standard"
  size: 50Gi

resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2
    memory: 2Gi
```

### 2) Install / upgrade

```bash
helm upgrade --install ournezt-postgres ./charts/ournezt-postgres \
  --namespace ournezt \
  --create-namespace \
  -f values-prod.yaml
```

### 3) Recommended secret approach (instead of plaintext in values)

Use a pre-created Kubernetes Secret and reference it:

```yaml
postgres:
  existingSecret: ournezt-postgres-secret
  passwordKey: POSTGRES_PASSWORD
```

Then create the secret:

```bash
kubectl -n ournezt create secret generic ournezt-postgres-secret \
  --from-literal=POSTGRES_PASSWORD='<strong-password>'
```
