#!/usr/bin/env bash
# ============================================================
# Run Alembic DB migrations against Cloud SQL via Cloud Run Job
# Usage: bash deploy/migrate.sh
# ============================================================
set -euo pipefail

PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/nutrimind-backend:latest"

echo "🗄️  Running database migrations..."

gcloud run jobs create nutrimind-migrate \
  --image="$IMAGE" \
  --region="$REGION" \
  --command="alembic" \
  --args="upgrade,head" \
  --set-secrets=DATABASE_URL=nutrimind-db-url:latest,SECRET_KEY=nutrimind-secret-key:latest \
  --service-account="nutrimind-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --vpc-connector=nutrimind-vpc-connector \
  --quiet 2>/dev/null || \
gcloud run jobs update nutrimind-migrate \
  --image="$IMAGE" \
  --region="$REGION" \
  --quiet

gcloud run jobs execute nutrimind-migrate \
  --region="$REGION" \
  --wait

echo "✅ Migrations complete"
