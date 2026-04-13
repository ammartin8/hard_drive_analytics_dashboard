## 🗂️ Phase-by-Phase Implementation Plan

### **Phase 1: Setup & Infrastructure**
*   Create GCP project and enable APIs (Storage, BigQuery, Compute Engine).
*   Write Terraform code to provision:
    *   GCS bucket (`data-lake`)
    *   BigQuery dataset (`hard_drive`)
    *   Airflow Docker container with PostgreSQL backend
    *   Compute instance for Spark (optional)
*   Dockerize ETL + dbt + Streamlit apps.
*   Set up GitHub Actions for Terraform deployment.

### **Phase 2: Data Ingestion & ETL**
*   Write Python-based Airflow tasks (`data_etl.py`):
    *   Download CSV archives from Backblaze (via GitHub releases).
    *   Extract CSV files to local sandbox.
    *   Convert CSV to Parquet format using `pyarrow`.
    *   Upload Parquet files to GCS bucket via `GCSHook`.
*   Configure Airflow DAG (`data_etl_dag_v2`) for quarterly runs.
*   Validate data in GCS.

### **Phase 3: Data Transformation**
*   Write dbt models:
    *   `stg_drives`: raw Parquet data.
    *   `dim_manufacturer`: deduplicated manufacturer table.
    *   `fact_failures`: aggregated failures by manufacturer + date.
    *   `dim_date`: date dimension (partitioned).
*   Use `dbt run` after ETL completes.
*   Validate schema and data in BigQuery.

### **Phase 4: Dashboard**
*   Build Streamlit app:
    *   Connect to BigQuery via `google-cloud-bigquery`.
    *   Create two tiles:
        1.  Bar chart: Failure rates by manufacturer.
        2.  Line chart: Failures over time.
    *   Add titles, labels, and interactivity.
*   Deploy Streamlit app (via GCP Compute Engine or local Docker).

### **Phase 5: Documentation & Peer Review**
*   Complete README.md with:
    *   Project description.
    *   Architecture diagram.
    *   Setup instructions.
    *   How to run each component.
    *   Evaluation criteria mapping.
*   Prepare 3 peer reviews.