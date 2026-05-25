# sap-pyspark-ingestion
Learning project to create a reusable pyspark framework to ingest json/tsv/csv files from adls blob storage and automating it to push to Databricks.  

sap-pyspark-ingestion/
├── .github/workflows/ 
  │ 
  └── deploy_to_databricks.yml ← auto-deploys on every git push 
├── data_generator/ 
  │ 
  └── sap_data_generator.py ← generates fake SAP files 
├── framework/ 
  │ ├── ingestion/ 
  │ │
    ├── base_ingester.py ← shared logic for all formats 
  │ │
    ├── json_ingester.py ← reads JSON files 
  │ │ 
    ├── csv_ingester.py ← reads CSV files 
  │ │ 
    └── tsv_ingester.py ← reads TSV files 
│ └── utils/ 
  │ 
  └── adls_utils.py ← Azure ADLS helper 
├── notebooks/ 
  │ 
  └── run_ingestion.py ← main notebook on Databricks 
├── scripts/ 
  │ 
  └── trigger.sh ← VM shell script orchestrator 
├── config/ 
  │ 
  └── settings.yaml ← all settings in one place 
  └── requirements.txt
