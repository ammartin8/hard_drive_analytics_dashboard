import click
from glob import glob
import os
import pandas as pd
import pyarrow.parquet as pq
import requests
from sqlalchemy import create_engine
import zipfile


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
    "smart_5_normalized": "float64",  # SMART attribute (normalized value)
    "smart_5_raw": "float64", # Raw SMART value
    "smart_187_normalized": "float64",
    "smart_187_raw": "float64",
    "smart_188_normalized": "float64",
    "smart_188_raw": "float64",
    "smart_197_normalized": "float64",
    "smart_197_raw": "float64",
    "smart_198_normalized": "float64",
    "smart_198_raw": "float64"
}

parse_dates = [
    "date"
]


# Helper Functions
def download_data(year=2025, qtr=1):
    """
    Fetches quarterly hard drive data archives from Backblaze based on year and quarter. 

    Automatically creates the local directory if missing and uses streaming transfer 
    to handle large files efficiently. Returns the absolute path to the downloaded ZIP file.

    Args:
        year (int): Collection year (default: 2025).
        qtr (int): Quarter number (1-4) (default: 1).

    Returns:
        str: Absolute path string to the downloaded ZIP file.
    """
    # Ensure ../data/zip folder exists
    download_dir='./data/zip'
    os.makedirs(download_dir, exist_ok=True)

    # Define base url
    base_url = "https://f001.backblazeb2.com/file/Backblaze-Hard-Drive-Data"

    # File structure
    file_suffix = "data_Q"+f"{qtr}_{year}"

    zip_url = f"{base_url}/{file_suffix}.zip"
    # Get filename from URL path
    zip_filename = zip_url.split('/')[-1] or 'archive.zip'

    # Download zip file from URL and save to download_dir
    zip_path = os.path.join(download_dir, zip_filename)
    
    print(f"Downloading {zip_url} to {zip_path}...")
    response = requests.get(zip_url, stream=True)
    response.raise_for_status()  # Raise HTTPError for bad responses
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"{zip_path} is downloaded!")
    return zip_path


def unzip_file(input_file):
    """
    Extracts ZIP file contents to a date-based directory under ../data/source_csv/.

    Automatically derives year from filename (format: data_Q{qtr}_{year}.zip) and 
    creates matching extraction folder. Validates file existence before processing.
    Uses zipfile.ZipFile with extractall() for efficient bulk extraction of CSV files.

    Args:
        input_file (str): Absolute path string to ZIP archive (default uses last download).
        
    Returns:
        None: Extracts directly to filesystem. Prints progress info.

    Raises:
        FileNotFoundError: If input file path does not exist.

    Notes:
        - Filename MUST follow pattern: data_Q{qtr}_{year}.zip for year extraction
        - Raises error if ZIP contents contain unsupported or corrupt entries
    """
    # Extract year and qtr from zip_path to create folder names
    zip_path_year = input_file.split('/')[-1].split('_')[-1].split('.')[0]

    # Ensure extract directory exists
    extract_dir=f"./data/source_csv/{zip_path_year}"
    os.makedirs(extract_dir, exist_ok=True)
    
    # Validate input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        # List contents (optional check)
        print("Contents:", zip_ref.namelist())
        
        # Extract all files to the specified extract directory
        zip_ref.extractall(extract_dir)
        print(f"A total of {len(zip_ref.namelist())} file(s) extracted.") 
        print(f"Extracted to: {extract_dir}")


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='hard_drive_db', help='PostgreSQL database name')
@click.option('--target-table', default='hard_drive_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    # Ingestion logic here
    
    # Download data and save file path to variable
    download_data_path = download_data(year=2025, qtr=1)

    # Takes file path and unzips files from download file path
    unzip_file(input_file=download_data_path)


if __name__ == '__main__':
    run()