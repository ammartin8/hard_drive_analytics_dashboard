# 📊 Project Plan: Data Drive Failure Analytics Dashboard

### 🚧 Status: <span style="color: #dfa018ff;">Work in Progress</span>

> **Project Title**: Data Drive Failure Analytics Dashboard  
> **Dataset Source**: Backblaze Hard Drive Data  
> **Cloud Provider**: Google Cloud Platform (GCP)  
> **Data Lake**: Google Cloud Storage (GCS)  
> **Data Warehouse**: BigQuery  
> **ETL & Batch Processing**: Apache Airflow (Python)
> **Data Transformation**: dbt (Python + SQL)  
> **Orchestration**: Apache Airflow (Python) (Docker Container)
> **Dashboard**: Streamlit  
> **Infrastructure as Code**: Terraform  
> **Containerization**: Docker  

---

## 📖 Table of Contents

1. Project Overview  
2. Dataset & Scope  
3. Architecture & Data Flow
4. Technology Stack  
5. Phase-by-Phase Implementation Plan  


---

## 📌 Project Overview

This project will ingest, process, transform, and visualize Backblaze’s hard drive failure dataset to build a dashboard that displays:

- **Tile 1**: Distribution of hard drive failure rates by manufacturer (categorical).  
- **Tile 2**: Failure trends over time (temporal line chart).

The pipeline will be **batch-oriented**, orchestrated via Apache Airflow (Docker container), with Python-based ETL tasks and dbt for transformations. BigQuery stores final star schema tables, and Streamlit provides the interactive dashboard. Infrastructure is provisioned via Terraform and containerized using Docker.

---

## 📦 Dataset & Scope

- **Source**: Backblaze Hard Drive Data
- **Format**: CSV (multiple files)  
- **Columns of Interest**:  
  - `model` (manufacturer)  
  - `failure_date`  
  - `failure_indicator`  
  - `smart_attrs`   
- **Scope**:  
  - Focus on failure trends and manufacturer reliability.  
  - Time range: 2023–2025 (as available).  
  - Data cleaning: handle missing values, standardize dates, deduplicate.

---

## 🔄 Architecture & Data Flow

```mermaid
flowchart TD
    A[Raw Data: Backblaze CSVs] --> B[Ingestion to GCS via Airflow + Local Python Scripts]
    B --> C[Airflow Orchestration (Docker Container)]
    C --> D[Extract, Transform, Load Operations]
    D --> E[Upload Parquet to GCS Data Lake]
    E --> F[dbt Transformations: Star Schema on BigQuery]
    F --> G[BigQuery Storage Layer]
    G --> H[Streamlit Dashboard]
    H --> I[Tile 1: Manufacturer Failure Rates]
    H --> J[Tile 2: Failure Trends Over Time]
```

> **Notes**:  
> - **GCS** serves as the data lake (raw and processed Parquet).  
> - **Apache Airflow** orchestrates all ETL tasks within a Docker container.
> - **Airflow Tasks**: download_data(), extract_data(), convert_csv_to_parquet(), upload_to_gcs()
> - **dbt** runs transformations for star schema generation in BigQuery.
> - **BigQuery** stores final star schema tables.  
> - **Streamlit** pulls data from BigQuery via `google-cloud-bigquery` Python client.

---

## 🛠️ Technology Stack

| Layer              | Technology             | Purpose                                                                 |
|--------------------|------------------------|-------------------------------------------------------------------------|
| Cloud              | Google Cloud           | Hosting GCS, BigQuery, Compute Engine, Airflow                         |
| Data Lake          | Google Cloud Storage   | Raw and processed Parquet data storage                                |
| Data Warehouse     | BigQuery               | Optimized storage and querying for dashboard                         |
| ETL & Batch        | Apache Airflow (Python)| ETL jobs via `@dag` and `@task` decorators with Pandas/PyArrow         |
| Transformation     | dbt                    | Define transformations (e.g., star schema)                            |
| Dashboard          | Streamlit              | Interactive UI with two tiles                                         |
| Infrastructure     | Terraform              | Provision GCS, BigQuery, Airflow, compute instances                    |
| Containerization   | Docker                 | Package Airflow + ETL + dbt apps for reproducibility                  |

---

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
*   Use `dbt run` triggered from Airflow after ETL completes.
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