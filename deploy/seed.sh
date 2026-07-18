#!/usr/bin/env bash
# ============================================================
# Seed the food database via a one-off Cloud Run Job
# Usage: bash deploy/seed.sh
# ============================================================
set -euo pipefail

PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/nutrimind-backend:latest"

echo "🌱 Seeding food database..."

gcloud run jobs create nutrimind-seed \
  --image="$IMAGE" \
  --region="$REGION" \
  --command="python" \
  --args="seed_data.py" \
  --set-secrets=DATABASE_URL=nutrimind-db-url:latest \
  --service-account="nutrimind-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --vpc-connector=nutrimind-vpc-connector \
  --quiet 2>/dev/null || \
gcloud run jobs update nutrimind-seed \
  --image="$IMAGE" \
  --region="$REGION" \
  --quiet

gcloud run jobs execute nutrimind-seed \
  --region="$REGION" \
  --wait

echo "✅ Seed complete"
