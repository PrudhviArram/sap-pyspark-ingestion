#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
DATE_FOLDER=$(date +"%Y%m%d")
DATA_DIR="$PROJECT_DIR/data/$DATE_FOLDER"
DBFS_SOURCE="dbfs:/FileStore/sap_data/$DATE_FOLDER"

GREEN="\033[0;32m"; RED="\033[0;31m"; NC="\033[0m"
log()  { echo -e "${GREEN}[$(date +%T)]${NC} $1"; }
fail() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

log "=== SAP Ingestion Pipeline (Serverless) — $DATE_FOLDER ==="

# Step 1: Generate SAP data files
log "Step 1: Generating SAP data..."
cd "$PROJECT_DIR"
python data_generator/sap_data_generator.py || fail "Data generation failed"
log "Data files ready in: $DATA_DIR"

# Step 2: Upload data to Databricks DBFS
log "Step 2: Uploading data to DBFS..."
databricks fs mkdirs "$DBFS_SOURCE" 2>/dev/null || true
for f in "$DATA_DIR"/*; do
  log "  uploading $(basename $f)..."
  databricks fs cp "$f" "$DBFS_SOURCE/$(basename $f)" --overwrite
done
log "Upload complete → $DBFS_SOURCE"

# Step 3: Push code to GitHub
cd "$PROJECT_DIR"
if [[ $(git status --porcelain) ]]; then
  log "Step 3: Pushing code to GitHub..."
  git add -A
  git commit -m "auto: pipeline run $DATE_FOLDER"
  git push origin dev
  log "GitHub Actions will auto-deploy to Databricks"
else
  log "Step 3: No code changes to push"
fi

# Step 4: Trigger serverless notebook
log "Step 4: Submitting notebook to Serverless compute..."
: "${DATABRICKS_HOST:?Set DATABRICKS_HOST in .env}"
: "${DATABRICKS_TOKEN:?Set DATABRICKS_TOKEN in .env}"

RESPONSE=$(curl -s -X POST "$DATABRICKS_HOST/api/2.1/jobs/runs/submit" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "run_name": "sap_ingest_'"$DATE_FOLDER"'",
    "notebook_task": {
      "notebook_path": "/Shared/sap_ingestion/run_ingestion"
    },
    "environments": [{
      "environment_key": "default",
      "spec": {
        "client": "1",
        "dependencies": ["pyyaml"]
      }
    }]
  }')

RUN_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('run_id','ERROR: '+str(d)))")
log "Notebook submitted — Run ID: $RUN_ID"
log ""
log "=== Pipeline complete! Date: $DATE_FOLDER | Run: $RUN_ID ==="