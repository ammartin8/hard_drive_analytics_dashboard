import os
from datetime import timedelta, datetime
from pathlib import Path
import requests
import pandas as pd
import zipfile
import pyarrow as pa
import pyarrow.parquet as pq
from airflow.sdk import dag, task
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
import shutil
import tempfile    # For creating sandbox directories
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# === Configuration & Type Hints ===
dtype = {
    "serial_number": "string",
    "model": "string",
    "capacity_bytes": "Int64",
    "failure": "Int64",
    "datacenter": "string",
    "cluster_id": "Int64",
    "vault_id": "Int64",
    "pod_id": "Int64",
    "pod_slot_num": "float64",
    "is_legacy_format": "boolean",
    "smart_5_normalized": "float64",
    "smart_5_raw": "float64", 
    "smart_187_normalized": "float64",
    "smart_187_raw": "float64", 
    "smart_188_normalized": "float64",
    "smart_188_raw": "float64",
    "smart_197_normalized": "float64",
    "smart_197_raw": "float64",
    "smart_198_normalized": "float64",
    "smart_198_raw": "float64"
}

parse_dates = ["date"]

# Path Constants
DATA_ROOT = "./data"
ZIP_DIR = os.path.join(DATA_ROOT, "zip")
CSV_DIR = os.path.join(DATA_ROOT, "source_csv")
PQ_DIR = os.path.join(DATA_ROOT, "pq")

# GCP Configuration (Define these in your .env file or docker-compose.yml)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")  # Optional
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-bucket-name")   # Replace with actual bucket name
GCP_CONN_ID = "gcp"  # Must match the connection ID from Airflow database


BUCKET_NAME = GCS_BUCKET_NAME
DESTINATION_BLOB_NAME = "raw_data"

default_args = {
    "start_date": datetime(2026, 1, 1)
}

# Data process ranges -- YOU MAY ADJUST START AND END DATES HERE TO EXPAND OR LIMIT DATA PROCESSING
YR_START = 2024
YR_END = 2024
QTR_START = 1
QTR_END = 4

YEARS = range(YR_START, YR_END + 1)
QTERS = range(QTR_START, min(QTR_END, 4) + 1)

iterations = [(year, qtr) for year in YEARS for qtr in QTERS]


# === DAG Definition ===
@dag(
    schedule=None, # Manual runs only
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        'owner': 'airflow',
    },
    max_active_tasks=4, 
    max_active_runs=1
)
def data_etl_dag_v2():
    @task(max_active_tis_per_dag=4)
    def download_data(year, qtr):
        """
        Fetches quarterly hard drive data archives from Backblaze.
        Returns the absolute path to the downloaded ZIP file via XCom.
        """
        # Ensure directory exists
        download_dir = os.path.join(ZIP_DIR)
        os.makedirs(download_dir, exist_ok=True)
        base_url = "https://f001.backblazeb2.com/file/Backblaze-Hard-Drive-Data" # prod source
        # base_url = "https://github.com/ammartin8/hard_drive_analytics_dashboard/releases/download/hd_2025_Q1" # dev source
        file_suffix = "data_Q"+f"{qtr}_{year}"

        # Construct URL and Filename
        zip_url = f"{base_url}/{file_suffix}.zip"
        zip_filename = os.path.basename(zip_url) or 'archive.zip'
        zip_path = os.path.join(download_dir, zip_filename)
        
        # Download the file
        print(f"Downloading {zip_url} to {zip_path}...")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"[SUCCESS] {zip_path} downloaded successfully!")
        
        return zip_path 

    @task(max_active_tis_per_dag=2)
    def extract_data_v2(input_file_zip_path, extract_to): # extract_to would be CSV_DIR
        if not os.path.exists(input_file_zip_path):
            raise FileNotFoundError(f"ZIP file not found: {input_file_zip_path}")
        
        # 1. Create a temporary sandbox directory
        temp_dir = tempfile.mkdtemp(prefix='safe_extract_')
        print(f"[+] Created temp sandbox: {temp_dir}")
        
        moved_files = []

        try:
            with zipfile.ZipFile(input_file_zip_path, 'r') as z:
                # Extract to the temporary safe dir first
                if not z.namelist():
                    raise ValueError("ZIP file is empty or invalid.")
                
                # Extract all contents to temporary directory
                print(f"[i] Extracting to sandbox...")
                z.extractall(path=temp_dir)
                
                # 2. Move valid contents to target when needed
                for root, dirs, files in os.walk(temp_dir):
                    # Skip MACOSX metafile processing
                    if '__MACOSX' in root:
                        continue

                    relative_path = os.path.relpath(root, temp_dir)
                    
                    # Ensure relative path is not empty and doesn't contain '..' 
                    if relative_path == '.' or '..' not in relative_path:
                        dest_root = os.path.join(extract_to, relative_path)
                        os.makedirs(dest_root, exist_ok=True)

                        for file in files:
                            # Skip MACOS metadata files
                            if file.startswith('__') or file.endswith('.DS_Store'):
                                continue
                            
                            # Only process CSV files
                            if not file.endswith(".csv"):
                                continue

                            src_file = os.path.join(root, file)
                            try:
                                dest_pth = dest_root + "/" + file
                                
                                shutil.move(src_file, dest_root + "/" + file)
                                print(f'File: {file} moved to {dest_root}')
                                moved_files.append(dest_pth)

                            except Exception as e:
                                print(f"Failed to move {file}: {e}")
            shutil.rmtree(temp_dir)
            print(f"[-] Sandbox removed.")
            sorted_moved_files = sorted(moved_files)

            return sorted_moved_files

        except Exception as e:
            print(f"An error occurred: {e}")

    @task(max_active_tis_per_dag=1)
    def convert_csv_to_parquet(csv_file_paths):
        """Converts each CSV file to Parquet format using pandas."""
        parquet_files = []
        
        # Create empty dataframe with selected column names
        print("Creating empty data frame with selected columns\n")
        first_file = csv_file_paths[0]

        df = pd.read_csv(first_file
        , nrows=1 # need at least one row to capture proper date types
        , dtype=dtype
        , parse_dates=parse_dates
        ).head(0) # prevent any records from being read as we want df empty with headers only
        print(f"[i]: Schema data types:\n {df.dtypes}\n")

        col_to_keep = []
        for col in df.columns:
            if col in dtype or col in parse_dates:
                col_to_keep.append(col)
        print("[i]: Empty dataframe created!\n")

        print(f"[i]: Columns to extract from source csv: {col_to_keep}\n")

        for csv_path in csv_file_paths:
            if not os.path.exists(csv_path):
                continue
                
            # Read CSV with proper dtypes
            try:
                df = pd.read_csv(
                    csv_path,
                    dtype=dtype,
                    parse_dates=parse_dates,
                    usecols=col_to_keep
                )

                # Generate Parquet filename
                base_name = os.path.basename(csv_path)
                name_without_ext = os.path.splitext(base_name)[0]
                pq_filename = f"{name_without_ext}.parquet"
                pq_path = os.path.join(PQ_DIR, pq_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(pq_path), exist_ok=True)
                
                # Write to Parquet
                df.to_parquet(
                    pq_path,
                    engine='pyarrow',
                    compression='snappy'
                )
                
                parquet_files.append(pq_path)

            except Exception as e:
                print(f"Error converting {csv_path}: {e}")
                continue

        print(f"[i]: Successfully converted {len(parquet_files)} files")
        return parquet_files


    @task(max_active_tis_per_dag=2)
    def upload_to_gcs(parquet_file_paths, year, qtr):
        """Uploads Parquet files to GCS bucket."""
        if not parquet_file_paths:
            print("No files to upload!")
            return

        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)

        # Checking dtypes before upload
        print(f"[i]: Sample parquet dtypes being uploaded:\n {pd.read_parquet(parquet_file_paths[0]).head(3)}\n")

        uploaded_files = []
        for pq_file in parquet_file_paths:
            DESTINATION_BLOB_NAME = f"raw_data/{year}/Q{qtr}/" + os.path.basename(pq_file)
            hook.upload(
                bucket_name=BUCKET_NAME,
                object_name=DESTINATION_BLOB_NAME, # "raw_data/year/qtr + file name"
                filename=pq_file
            )
            uploaded_files.append(pq_file)
            # Optional cleanup
            os.remove(pq_file)

        print(f"[i]: Successfully uploaded {len(uploaded_files)} files")

    print("=" * 60)
    print("Starting ETL Pipeline")
    print("=" * 60)
    try:
        for year, qtr in iterations:
            print(f"\n{'='*40} Processing {year} Q{qtr} {'='*40}")

            data = download_data(year, qtr)
            files = extract_data_v2(data, CSV_DIR)
            parquet_files = convert_csv_to_parquet(files)
            upload_to_gcs(parquet_files, year, qtr)

    except Exception as e:
        print(f"An error has occurred: {e}")
data_etl_dag_v2()