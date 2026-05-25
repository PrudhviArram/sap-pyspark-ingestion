# Databricks Serverless Notebook
# 'spark' is automatically available — no changes needed for that

import sys, os, yaml
from datetime import datetime

# ── Load framework from DBFS (uploaded by GitHub Actions) ────
# On serverless we use /dbfs/ prefix to access DBFS files
DBFS_FRAMEWORK = '/dbfs/FileStore/sap_framework'
if DBFS_FRAMEWORK not in sys.path:
    sys.path.insert(0, DBFS_FRAMEWORK)

# ── Install pyyaml if not present (serverless safe-guard) ────
try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyyaml', '-q'])
    import yaml

from framework.ingestion import get_ingester

# ── Load config ───────────────────────────────────────────────
CONFIG_PATH = '/dbfs/FileStore/sap_framework/config/settings.yaml'
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

source_base = cfg['storage']['source_base']
target_base = cfg['storage']['target_base']
date_folder = datetime.now().strftime('%Y%m%d')

print(f'Source : {source_base}/{date_folder}/')
print(f'Target : {target_base}/{date_folder}/')
print(f'Date   : {date_folder}')
print()

# ── Run ingestion ─────────────────────────────────────────────
results = []
for ds in cfg['datasets']:
    for fmt in ds['formats']:
        src = f"{source_base}/{date_folder}/{ds['name']}.{fmt}"
        tgt = f"{target_base}/{date_folder}/{ds['name']}/{fmt}"
        try:
            ingester = get_ingester(fmt, spark, cfg['ingestion'])
            df = ingester.ingest(src, tgt)
            rows = df.count()
            results.append({'name': ds['name'], 'fmt': fmt, 'rows': rows, 'ok': True})
            print(f"  ✓  {ds['name']}.{fmt:<5}  {rows:>5} rows")
        except Exception as e:
            results.append({'name': ds['name'], 'fmt': fmt, 'rows': 0, 'ok': False, 'err': str(e)})
            print(f"  ✗  {ds['name']}.{fmt:<5}  FAILED: {e}")

# ── Summary ───────────────────────────────────────────────────
ok_count   = sum(1 for r in results if r['ok'])
fail_count = sum(1 for r in results if not r['ok'])
total_rows = sum(r['rows'] for r in results)

print()
print('=' * 45)
print(f'  Datasets succeeded : {ok_count}')
print(f'  Datasets failed    : {fail_count}')
print(f'  Total rows loaded  : {total_rows:,}')
print('=' * 45)