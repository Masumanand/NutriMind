#!/usr/bin/env bash
# ============================================================
# NutriMind AI — GCP Setup Script
# Run once to provision all required GCP infrastructure.
# Usage: bash deploy/setup.sh
# ============================================================
set -euo pipefail

# ── CONFIG — edit these before running ──────────────────────
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
DB_INSTANCE="nutrimind-postgres"
DB_NAME="nutrimind"
DB_USER="nutrimind"
VPC_CONNECTOR="nutrimind-vpc-connector"
BACKEND_SA="nutrimind-backend"

# ── Secrets — set these as env vars before running ──────────
# export OPENAI_API_KEY="sk-..."
# export DB_PASSWORD="..."
# export SECRET_KEY="..."
# export MONGO_URL="mongodb+srv://..."
# export WEATHER_API_KEY="..."
# ────────────────────────────────────────────────────────────

echo "🚀 Setting up NutriMind AI on GCP project: $PROJECT_ID"

# 1. Set project
gcloud config set project "$PROJECT_ID"

# 2. Enable required APIs
echo "📡 Enabling GCP APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  vpcaccess.googleapis.com \
  redis.googleapis.com \
  --quiet

# 3. Create service account for backend
echo "👤 Creating service account..."
gcloud iam service-accounts create "$BACKEND_SA" \
  --display-name="NutriMind Backend Service Account" \
  --quiet || echo "Service account already exists"

SA_EMAIL="$BACKEND_SA@$PROJECT_ID.iam.gserviceaccount.com"

# Grant Cloud SQL client role
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/cloudsql.client" --quiet

# Grant Secret Manager accessor role
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor" --quiet

# 4. Create Cloud SQL (PostgreSQL 15)
echo "🗄️  Creating Cloud SQL instance (this takes ~5 min)..."
gcloud sql instances create "$DB_INSTANCE" \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region="$REGION" \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --quiet || echo "SQL instance already exists"

gcloud sql databases create "$DB_NAME" \
  --instance="$DB_INSTANCE" --quiet || echo "Database already exists"

gcloud sql users create "$DB_USER" \
  --instance="$DB_INSTANCE" \
  --password="${DB_PASSWORD:-changeme}" --quiet || echo "User already exists"

# Get Cloud SQL connection name
SQL_CONN=$(gcloud sql instances describe "$DB_INSTANCE" \
  --format="value(connectionName)")
echo "Cloud SQL connection: $SQL_CONN"

DB_URL="postgresql+asyncpg://$DB_USER:${DB_PASSWORD:-changeme}@/$DB_NAME?host=/cloudsql/$SQL_CONN"

# 5. Create Memorystore Redis
echo "📦 Creating Memorystore Redis..."
gcloud redis instances create nutrimind-redis \
  --size=1 \
  --region="$REGION" \
  --redis-version=redis_7_0 \
  --quiet || echo "Redis instance already exists"

REDIS_IP=$(gcloud redis instances describe nutrimind-redis \
  --region="$REGION" --format="value(host)")
REDIS_URL="redis://$REDIS_IP:6379"
echo "Redis IP: $REDIS_IP"

# 6. Create VPC Serverless Connector (for Cloud Run → Redis/SQL)
echo "🔌 Creating VPC connector..."
gcloud compute networks vpc-access connectors create "$VPC_CONNECTOR" \
  --region="$REGION" \
  --range=10.8.0.0/28 \
  --quiet || echo "VPC connector already exists"

# 7. Store secrets in Secret Manager
echo "🔐 Storing secrets..."
store_secret() {
  local name=$1
  local value=$2
  echo -n "$value" | gcloud secrets create "$name" \
    --data-file=- --quiet 2>/dev/null || \
  echo -n "$value" | gcloud secrets versions add "$name" \
    --data-file=- --quiet
  # Grant access to backend SA
  gcloud secrets add-iam-policy-binding "$name" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor" --quiet
}

store_secret "nutrimind-openai-key"   "${OPENAI_API_KEY:-placeholder}"
store_secret "nutrimind-secret-key"   "${SECRET_KEY:-change-me-in-production}"
store_secret "nutrimind-db-url"       "$DB_URL"
store_secret "nutrimind-mongo-url"    "${MONGO_URL:-mongodb://localhost:27017/nutrimind}"
store_secret "nutrimind-redis-url"    "$REDIS_URL"
store_secret "nutrimind-weather-key"  "${WEATHER_API_KEY:-placeholder}"

# 8. Grant Cloud Build access to deploy Cloud Run
CB_SA="$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$CB_SA" \
  --role="roles/run.admin" --quiet
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$CB_SA" \
  --role="roles/iam.serviceAccountUser" --quiet

echo ""
echo "✅ GCP infrastructure setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update MONGO_URL secret with your MongoDB Atlas connection string"
echo "  2. Update OPENAI_API_KEY secret with your real key"
echo "  3. Run: gcloud builds submit --config=deploy/cloudbuild.yaml ."
echo "  4. Run database migrations: see deploy/migrate.sh"
