import click
from glob import glob
import os
import pandas as pd
from pathlib import Path
import pyarrow.parquet as pq
import pyspark
from pyspark.sql.functions import date_format, to_date, datediff, col, unix_timestamp, max
from pyspark.sql import SparkSession
from pyspark.sql import types
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
    
    if os.path.exists(zip_path):
        print(f"File already exist! File saved here: {zip_path}\n")
        return zip_path
    else:
        print(f"Downloading {zip_url} to {zip_path}...")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"{zip_path} is downloaded!")
        return zip_path


def unzip_and_load_to_postgres(input_file, con, target_table):
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
    zip_path_year = input_file.split('/')[-1].split('_')[-1].split('.')[0] # outputs year
    base_dir_name = input_file.split('/')[-1].split('.')[0] # outputs data_{qtr}_{year}

    extract_dir=f"./data/source_csv/{zip_path_year}"
    os.makedirs(extract_dir, exist_ok=True)

    # Validate input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}.")
    
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        # # Check if any csv files exist first
        existing_files = os.listdir(f'{extract_dir}/{base_dir_name}')[0]
    
        if len(existing_files) > 0:
            print(f"CSV files already exist in: {extract_dir}/{base_dir_name}")
        else:
            # Extract all files to the specified extract directory
            # List contents (optional check)
            print(f"Extracting the following contents: {zip_ref.namelist()} \n")
            zip_ref.extractall(extract_dir)
            print(f"A total of {len(zip_ref.namelist())} file(s) extracted to: {extract_dir}\n")
        
        
    # Create empty dataframe with selected column names
    first_file = f"{extract_dir}/{zip_ref.namelist()[0]}"

    df = pd.read_csv(first_file
    , nrows=0
    , dtype=dtype
    , parse_dates=parse_dates)
    col_to_keep = []

    for col in df.columns:
        if col in dtype or col in parse_dates:
            col_to_keep.append(col)

    print(f"Columns to extract from source csv: {col_to_keep}\n")

    # Extract csv directory name and list of files
    csv_dir = first_file.split('/')[-2] # outputs path to where csv files are located

    files = sorted(os.listdir(f"{extract_dir}/{csv_dir}"))

    # Store data in postgres db
    first = True
    for file in files[:3]:
        if first:
            df = pd.read_csv(f"{extract_dir}/{csv_dir}/{file}"
                , dtype=dtype
                , parse_dates=parse_dates
                , usecols=col_to_keep
                ).head(0)
            df.to_sql(name=target_table, index=False, con=con, if_exists='replace')
            print(f"Table created with the following schema: \n {pd.io.sql.get_schema(df, name=target_table, con=con)}\n")
            first = False
        
        df = pd.read_csv(f"{extract_dir}/{csv_dir}/{file}"
            , dtype=dtype
            , parse_dates=parse_dates
            , usecols=col_to_keep
            )
        df.to_sql(name=target_table, index=False, con=con, if_exists='append')
        print(f"Loaded {len(df)} records from file: {file}")

    return {
        'year': zip_path_year,
        'base_dir_name': base_dir_name,
        'csv_dir': csv_dir,
        'extract_dir': extract_dir
    }

def convert_data_to_parquet(year=None, extract_dir=None, csv_dir=None, base_dir_name=None):
    # Initialize Spark Session
    spark = SparkSession.builder \
        .master("local[8]") \
        .config("spark.ui.port", "4040") \
        .appName('hard_drive_spark_app') \
        .config("spark.driver.bindAddress", "localhost") \
        .config("spark.local.ip", "127.0.0.1") \
        .getOrCreate()


    # Setting up path directories for reading and writing files
    # Parquet output directory
    pq_output_dir=f"./data/pq/{year}/{base_dir_name}"
    os.makedirs(pq_output_dir, exist_ok=True)

    # Source csv directory
    csv_path = f"{extract_dir}/{csv_dir}"


    # Spark schema
    df_spark_schema = types.StructType([
    types.StructField("date", types.TimestampType(), True),
    types.StructField("serial_number", types.StringType(), True),
    types.StructField("model", types.StringType(), True),
    types.StructField("capacity_bytes", types.IntegerType(), True),
    types.StructField("failure", types.IntegerType(), True),
    types.StructField("datacenter", types.StringType(), True),
    types.StructField("cluster_id", types.IntegerType(), True),
    types.StructField("vault_id", types.IntegerType(), True),
    types.StructField("pod_id", types.IntegerType(), True),
    types.StructField("pod_slot_num", types.DoubleType(), True),
    types.StructField("is_legacy_format", types.BooleanType(), True),
    types.StructField("smart_5_normalized", types.DoubleType(), True),
    types.StructField("smart_5_raw", types.DoubleType(), True),
    types.StructField("smart_187_normalized", types.DoubleType(), True),
    types.StructField("smart_187_raw", types.DoubleType(), True),
    types.StructField("smart_188_normalized", types.DoubleType(), True),
    types.StructField("smart_188_raw", types.DoubleType(), True),
    types.StructField("smart_197_normalized", types.DoubleType(), True),
    types.StructField("smart_197_raw", types.DoubleType(), True),
    types.StructField("smart_198_normalized", types.DoubleType(), True),
    types.StructField("smart_198_raw", types.DoubleType(), True)
    ])

    try:
        # Read all csv files in csv path to spark df
        print(f"Reading csv files from: {csv_path}")
        df_spark = spark.read \
        .option("header", "true") \
            .schema(df_spark_schema) \
                .csv(f'{csv_path}')

        print(f"There are {df_spark.count()} records found.\n")
        print(f"Snapshot of file shown below: \n {df_spark.show(5)}\n")

        # Writing parquet file to desination
        df_spark.write.parquet(pq_output_dir, mode="overwrite")
        spark.stop()
    except Exception as err:
        print(f"An error has occured: {err}")


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='hard_drive_db', help='PostgreSQL database name')
@click.option('--target-table', default='hard_drive_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    # Create postgres database connection
    url = f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(url)
    print("Postgres connection created!\n")

    # for year in range(2024, 2026):
    # Download data and save file path to variable
    download_data_path = download_data(year=2025, qtr=1)

    # Takes file path and unzips files from download file path
    result = unzip_and_load_to_postgres(input_file=download_data_path, con=engine, target_table=target_table)
    
    convert_data_to_parquet(year=result['year'], extract_dir=result['extract_dir'], csv_dir=result['csv_dir'], base_dir_name=result['base_dir_name'])

if __name__ == '__main__':
    run()