# NutriMind AI — GCP Deployment Guide

Complete guide to deploying NutriMind AI on Google Cloud Platform using Cloud Run, Cloud SQL, and Memorystore.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloud Run (Frontend)                    │
│                  nutrimind-frontend:3000                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────┐
│                      Cloud Run (Backend)                     │
│                   nutrimind-backend:8000                     │
└──────┬──────────┬──────────┬──────────────────────────────┘
       │          │          │
       │          │          └─────► Secret Manager
       │          │                  (API keys, DB passwords)
       │          │
       │          └────────────────► MongoDB Atlas
       │                             (food logs, social posts)
       │
       ├─────────────────────────► Cloud SQL (PostgreSQL 15)
       │                            (users, habits, weights)
       │
       └─────────────────────────► Memorystore (Redis 7)
                                    (sessions, cache, streaks)
```

---

## Prerequisites

1. **GCP Project** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **MongoDB Atlas** account (free tier works): https://www.mongodb.com/cloud/atlas
4. **OpenAI API key**: https://platform.openai.com/api-keys
5. **Weather API key** (optional): https://openweathermap.org/api

---

## Step 1: Initial Setup

```bash
# Clone and navigate
cd nutrimind-ai

# Login to GCP
gcloud auth login
gcloud auth application-default login

# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

---

## Step 2: Configure MongoDB Atlas

1. Create a free cluster at https://cloud.mongodb.com/
2. Create a database user
3. Whitelist IP: `0.0.0.0/0` (for Cloud Run)
4. Get connection string (looks like `mongodb+srv://user:pass@cluster.mongodb.net/nutrimind`)
5. Export it:

```bash
export MONGO_URL="mongodb+srv://user:password@cluster.mongodb.net/nutrimind"
```

---

## Step 3: Set Required Secrets

```bash
# OpenAI API key (REQUIRED)
export OPENAI_API_KEY="sk-proj-..."

# JWT secret (generate a random 32-char string)
export SECRET_KEY="$(openssl rand -hex 32)"

# Database password (generate a random password)
export DB_PASSWORD="$(openssl rand -base64 24)"

# Weather API key (optional)
export WEATHER_API_KEY="your-openweathermap-key"
```

---

## Step 4: Run Infrastructure Setup

This creates Cloud SQL, Memorystore Redis, VPC connector, service accounts, and stores secrets.

```bash
# Edit deploy/setup.sh — set your PROJECT_ID at the top
nano deploy/setup.sh

# Make executable
chmod +x deploy/*.sh

# Run setup (takes ~10 minutes)
bash deploy/setup.sh
```

**What this creates:**
- Cloud SQL PostgreSQL 15 instance (`nutrimind-postgres`)
- Memorystore Redis 7 instance (`nutrimind-redis`)
- VPC Serverless Connector (`nutrimind-vpc-connector`)
- Service account (`nutrimind-backend@PROJECT_ID.iam.gserviceaccount.com`)
- 6 secrets in Secret Manager (API keys, DB URLs)

---

## Step 5: Build and Deploy

```bash
# Submit build to Cloud Build (takes ~5 minutes)
gcloud builds submit --config=deploy/cloudbuild.yaml .
```

This will:
1. Build backend Docker image
2. Build frontend Docker image
3. Push both to Container Registry
4. Deploy backend to Cloud Run
5. Deploy frontend to Cloud Run

---

## Step 6: Run Database Migrations

```bash
# Edit deploy/migrate.sh — set your PROJECT_ID
nano deploy/migrate.sh

# Run migrations
bash deploy/migrate.sh
```

---

## Step 7: Seed Food Database

```bash
# Edit deploy/seed.sh — set your PROJECT_ID
nano deploy/seed.sh

# Seed database with sample foods
bash deploy/seed.sh
```

---

## Step 8: Get Your URLs

```bash
# Backend URL
gcloud run services describe nutrimind-backend \
  --region=us-central1 \
  --format="value(status.url)"

# Frontend URL
gcloud run services describe nutrimind-frontend \
  --region=us-central1 \
  --format="value(status.url)"
```

Visit the frontend URL to access NutriMind AI!

---

## Custom Domain (Optional)

```bash
# Map custom domain to frontend
gcloud run domain-mappings create \
  --service=nutrimind-frontend \
  --domain=app.nutrimind.ai \
  --region=us-central1

# Map custom domain to backend
gcloud run domain-mappings create \
  --service=nutrimind-backend \
  --domain=api.nutrimind.ai \
  --region=us-central1
```

Then update DNS records as instructed by GCP.

---

## Updating Secrets

```bash
# Update OpenAI key
echo -n "sk-new-key" | gcloud secrets versions add nutrimind-openai-key --data-file=-

# Update MongoDB URL
echo -n "mongodb+srv://new-url" | gcloud secrets versions add nutrimind-mongo-url --data-file=-

# Redeploy to pick up new secrets
gcloud run services update nutrimind-backend --region=us-central1
```

---

## Continuous Deployment (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GCP
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v1
      - run: gcloud builds submit --config=deploy/cloudbuild.yaml .
```

Store your service account key in GitHub Secrets as `GCP_SA_KEY`.

---

## Monitoring & Logs

```bash
# View backend logs
gcloud run services logs read nutrimind-backend --region=us-central1 --limit=50

# View frontend logs
gcloud run services logs read nutrimind-frontend --region=us-central1 --limit=50

# Monitor Cloud SQL
gcloud sql operations list --instance=nutrimind-postgres

# Monitor Redis
gcloud redis instances describe nutrimind-redis --region=us-central1
```

---

## Cost Estimate (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run (Backend) | 1M requests, 1GB RAM | ~$10 |
| Cloud Run (Frontend) | 1M requests, 512MB RAM | ~$5 |
| Cloud SQL (db-f1-micro) | Always-on | ~$7 |
| Memorystore Redis (1GB) | Always-on | ~$30 |
| MongoDB Atlas (Free tier) | 512MB | $0 |
| Secret Manager | 6 secrets | ~$0.50 |
| Container Registry | Storage | ~$1 |
| **Total** | | **~$53/month** |

Scale down to zero when idle to reduce costs further.

---

## Troubleshooting

**Backend won't start:**
```bash
# Check logs
gcloud run services logs read nutrimind-backend --region=us-central1 --limit=100

# Common issues:
# - Missing secrets → check Secret Manager
# - Can't connect to Cloud SQL → check VPC connector
# - Can't connect to Redis → check Memorystore IP and VPC
```

**Frontend can't reach backend:**
```bash
# Check NEXT_PUBLIC_API_URL in frontend deployment
gcloud run services describe nutrimind-frontend --region=us-central1 --format=yaml | grep NEXT_PUBLIC_API_URL

# Update if needed
gcloud run services update nutrimind-frontend \
  --region=us-central1 \
  --set-env-vars=NEXT_PUBLIC_API_URL=https://your-backend-url
```

**Database connection issues:**
```bash
# Test Cloud SQL connection
gcloud sql connect nutrimind-postgres --user=nutrimind

# Check VPC connector status
gcloud compute networks vpc-access connectors describe nutrimind-vpc-connector --region=us-central1
```

---

## Cleanup (Delete Everything)

```bash
# Delete Cloud Run services
gcloud run services delete nutrimind-backend --region=us-central1 --quiet
gcloud run services delete nutrimind-frontend --region=us-central1 --quiet

# Delete Cloud SQL
gcloud sql instances delete nutrimind-postgres --quiet

# Delete Redis
gcloud redis instances delete nutrimind-redis --region=us-central1 --quiet

# Delete VPC connector
gcloud compute networks vpc-access connectors delete nutrimind-vpc-connector --region=us-central1 --quiet

# Delete secrets
for secret in nutrimind-openai-key nutrimind-secret-key nutrimind-db-url nutrimind-mongo-url nutrimind-redis-url nutrimind-weather-key; do
  gcloud secrets delete $secret --quiet
done

# Delete service account
gcloud iam service-accounts delete nutrimind-backend@$PROJECT_ID.iam.gserviceaccount.com --quiet
```

---

## Support

- GCP Documentation: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
- Memorystore: https://cloud.google.com/memorystore/docs/redis
