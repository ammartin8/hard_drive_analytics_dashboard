# 📊 Project Plan: Storage Drive Analytics Dashboard

### 🚧 Status: <span style="color: #dfa018ff;">Work in Progress</span>

> **Project Title**: Storage Drive Analytics Dashboard  
> **Dataset Source**: Backblaze Storage Drive Data  
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
5. How to Run - Installation and execution guide.

---

## 📌 Project Overview

**Problem Statement**

Everyday users, including photographers, home lab enthusiasts, and small business owners, rely on consumer-grade storage drives they cannot afford to replace frequently. Data loss can result from the unpredictable failure of specific drive models, causing catastrophic data loss and financial damage. Currently, consumers purchase storage based on marketing specifications such as speed and capacity rather than empirical evidence regarding real-world longevity.

**Solution**

This project bridges the gap between enterprise telemetry and consumer accessibility by processing daily health snapshots from Backblaze to extract, transform, and visualize granular S.M.A.R.T. data. S.M.A.R.T stands for Self-Monitoring, Analysis, and Reporting Technology and is a monitoring system included in hard drives that reports on various attributes of the state of a given drive. Each drive includes S.M.A.R.T. metrics that report internal infomation about the drive. The resulting dashboard identifies which models maintain performance over time and highlights brands with high failure rates.

<img src="./docs/images/main_dashboard_image.png">

*Figure 1: Main dashboard view*


<img src="./docs/images/dashboard_demo.gif">

*Figure 2: Simple dashboard interactive demo*

**Target Audience**

The data benefits:
- Creators & Photographers: Who need reliable archival storage but can't rely solely on volatile system drives.
- Home Lab Enthusiasts: Building their first NAS and needing to know which drives survive the long haul before establishing redundancy.
- Small Businesses: Seeking secure data retention without enterprise-grade IT budgets.
- Casual Users: Anyone wanting peace of mind that their personal digital collection will last.

**Roadmap & Project Status (Important Note)**

*This project currently represents a Minimum Viable Product (MVP). Due to the upcoming expiration of my Google Cloud trial credits, my plan is to pivot this project towards open-source or free as well as self-hosted infrastructure to ensure long-term sustainability and accessibility. In addition, due to restricted time on completing this project in cloud, the emphasis on this project is more on building the data platform compared to the analytics. I'm hoping to further enhance the analytics proportion of project at future date.*

**The Goal**

To provide access to drive reliability data, shifting users from passive trust in marketing claims to active, evidence-based hardware selection. The project ingests, processes, transforms, and visualizes Backblaze's storage drive failure dataset.

**Dashboard Components**

The dashboard displays the following metrics and visualizations:
- **KPI Metric 1**: Most Recent Active Drives
- **KPI Metric 2**: Total Failed Drives 
- **Visual Chart 1**: Distribution of hard drive failure rates by manufacturer (categorical).  
- **Visual Chart 2**: Active and failed storage drive trends over time (stacked bar chart).
- **Table 1**: List of models, total drives, failed drives, and failure rate by quarter

The pipeline is **batch-oriented**, orchestrated via Apache Airflow (Docker container), with Python-based ETL tasks and dbt for transformations. BigQuery stores final star schema tables, and Streamlit provides the interactive dashboard. Infrastructure is provisioned via Terraform and containerized using Docker.

---

## 📦 Dataset & Scope

- **Source**: Backblaze Hard Drive Data
- **Format**: CSV (multiple files)  
- **Columns of Interest**:  
  - `model` (manufacturer)   
  - `failure_indicator`     
- **Scope**:  
  - Focus on failure trends and manufacturer reliability.  
  - Time range: 2024–2025 (as available).
  - Data cleaning: handle missing values, standardize dates, deduplicate.

---

## 🔄 Architecture & Data Flow

```mermaid
flowchart TD
    A[Raw Data: Backblaze CSVs] --> B["Data Ingestion via Airflow"]
    B --> C["Extract Transform Load ETL Operations via Airflow"]
    C --> D["Data Lake: Processed Parquet in GCS"]
    D --> E["dbt Transformations: Star Schema on BigQuery"]
    E --> F["Data Warehouse Layer (BigQuery)"]
    F --> G["Streamlit Dashboard"]
    
    G --> H["Tile 1: Manufacturer Failure Rates"]
    G --> I["Tile 2: Failure Trends Over Time"]

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

## How to Run the Project
Follow these steps to deploy, run, and visualize your Storage Drive Analytics Dashboard Using Google Cloud.

1. Prerequisites
    - A valid Google Cloud Platform (GCP) account
    - A Google Cloud Service Account with the following assigned role accesses:
        - BigQuery Admin
        - Storage Admin
        - Storage Object Admin
    - gcloud CLI installed and authenticated (gcloud auth application-default login).
    - Git (to clone this repository).
    - Docker CLI and Docker Compose installed
    - Terraform installed

> Note: Since the original development environment was done on a Ubuntu/Debian Desktop Linux, you may need to adjust certain commands or file path structures if you are using a different operating system. In addition, the templates provided assume you will save Google credentials in .google/credentials and navigate to specific folders as instructed.

2. Clone the Repository
    - `git clone https://github.com/ammartin8/hard_drive_analytics_dashboard.git`
    - `cd hard_drive_analytics_dashboard`

3. Configure Secrets & Environment
    - In the project root folder (hard_drive_failure_analytics_dashboard/), rename the .env.example file to `.env`
    - Edit the .env file by assigning your google project ID, and google cloud bucket environment variables. You can cahnage the airflow environment variables as well. Be sure to recall the `AIRFLOW_USER` and `AIRFLOW_PASSWORD` values as you'll need them to log into the Airflow UI.
    - Create a `.google/credentials` directory in the project root folder `hard_drive_failure_analytics_dashboard/` and export your service account key you created in Google Cloud Platform as a json file and store it in the following directory in your project project folder:
    ```
    hard_drive_failure_analytics_dashboard <---- project root folder
    ├── .google
    │   ├── credentials
    │   │   └── google_credentials.json
    ```

Note: Since the `docker-compose.yaml` references your service account as `google_credentials.json`, you should save your service account key with the same name; otherwise, you will need to update the name as referenced in the `docker-compose.yaml` file

4. Infrastructure Provisioning
    - This project uses Terraform to provision GCS buckets, BigQuery datasets, and the Airflow container environment.

### Navigate to the terraform directory
`cd ./terraform`

### Create a variables.tf file and populate the default fields as needed
Go to the [example.variables.tf](./terraform/example.variables.tf) file, rename the file to `variables.tf` and update the file by adding your project id, storage bucket name, and change location/region if needed.

### Initialize Terraform providers
Run `terraform init`

### Apply infrastructure code to create GCS and BigQuery resources
- Run `terraform plan` to double check that the assigned values and resources are correct.
- After verifying run `terraform apply` and enter yes to provision resources.


>Note: This will create a bucket in data-lake and dataset in BigQuery.

5. Trigger Data Ingestion

#### Airflow Instructions

The pipeline is batch-oriented. Run the Airflow DAG to download and process data:
1. Make sure you are in the project root directory first: `hard_drive_failure_analytics_dashboard/`
2. Make sure the following directories exists, if not please create them: 
    - ./airflow/config 
    - ./airflow/dags 
    - ./airflow/logs 
    - ./airflow/plugins

Setup should look similar to such:
```
hard_drive_failure_analytics_dashboard <-------project root directory
└── airflow
    ├── config
    ├── dags
    ├── logs
    └── plugins
```

>Note: On **Linux**, the quick-start needs to know your host user id and needs to have group id set to `0`. Otherwise the files created in `dags`, `logs`, `config` and `plugins` will be created with `root` user ownership. You have to make sure to configure them for the docker-compose:

To get your user id, run `id -u` in your terminal to get your user ID, then update `AIRFLOW_UID` in your .env file with that number.

For other operating systems, you may get a warning that AIRFLOW_UID is not set, but you can safely ignore it. You can also manually add the assigned value below in the .env file to get rid of the warning:

```
AIRFLOW_UID=50000
```

Now you can run the airflow image:
`docker compose up -d`

This process will do the following: 
- build a custom lighter version docker build for airflow
- Install uv python package manager
- Create virtual environment
- Install python dependencies based on uv.lock file

> Note: Sometimes the airflow docker build seems fails for some reason, try to rerun and it should build successfully. In addition, upon first run, it may take time for the docker containers to all be started. The hard_drive_analytics_dashboard-airflow-init-1 container typically can take up to 5-10 minutes to start depending on compute resources.


## Airflow ETL Process
<img src="./docs/images/airflow_ui_example.png">

*Figure 3: Airflow web interface showing task instances and DAG dependencies.*

Once airflow docker image is up and running, head to `http://localhost:8080` and login to airflow using the assigned credentials in your .env file. Once logged in go to The left sidebar and click `Admin` then `Connections`. To run data_etl_v2 pipeline, you must set up a Google Cloud connection in airflow UI first.
- Select `Add Connection`
- In the Connection ID enter: `gcp`
- In Connection Type search for `Google Cloud` and select it
- Select `Extra Fields` and in `Keyfile Path` section, input file path to your google credentials: `/.google/credentials/google_credentials.json`
- Go to bottom of form and click `Save`
- Test your connection by going to far right and clicking the line-chart symbol (next to edit button). The connection turns green you connected! If not, double check to make sure you have the correct file path to your google_credential.json file as referenced in the docker container.
- In the left sidebar, go to `Dags` > click on `data_etl_v2` workflow > then click on `Trigger` play button in top-right corner of UI > and select `Single Run`. 

>**Special Note & Considerations:** The data_etl_v2.py is currently set to download only 1 zip file `2025 Q4 data only (unzipped ~12 GB of data)!` Extracting all 2024 & 2025 years would be unzipped ~87.3 GB of data. Depending on compute resources run can take time (for me it was 5-7 mins for 1 year of data on a local machine). 
>
>If you have limited resources I would recommend keeping to just downloading one file just for demo testing. Otherwise, you can update the [data_etl_v2.py](./airflow/dags/data_etl.py) file in the airflow/dags folder and update `YR_START`, `YR_END`, and `QTR_START` and `QTR_END` data fields to pull more data.
>
>*For reference on a laptop with 15 GB of RAM and 12 cores CPU, took 26 minutes to download 2 full years of data.

The etl process is downloading zip file from source > extract zip file > converting to parquet > then loading to GCS.

## BigQuery Process
- Verify that files are loaded in your Google Cloud Storage bucket.
- In BigQuery Studio open to new blank SQL query page then update, copy/paste and run the following SQL commands in BigQuery to create your source datasets: [BigQuery_SQL_Cmd.sql](docs/BigQuery_SQL_Cmd.sql)

> **Partition Strategy**
>
> The materialized source table is set to be partition by combination of year and month. Since the dashboard is currently setup to report by month or quarter it seems to make sense to set up to partition by year_month that way, the partition sizes are not too big or too small and it will be easy to query the data by month, quarter, and year as they will likely be the most common filters used.

## dbt Process
1. In terminal go to dbt folder: `cd dbt`
2. If your virtual env folder hasn't be created yet run `uv run dbt --version` (this will install all packages into your virtual environment and check the dbt version). Upon completion, the dbt version should output in command line. 
3. Two ways to run dbt commands (choose one as either way works the same):
    - (Option 1) Use .venv virtual environment and run dbt commands as normal. 
        1. activate .venv environment: `source ../.venv/bin/activate`
    - (Option 2) Always add `uv run` before running any dbt commands
4. Make sure you in the dbt folder (`cd dbt`), run `source ../../.env` to import environment variables from project root

> Note: You  may get a error message in your dbt_project.yml file stating dbt configuration is invalid. You can safely ignore this error since this is likely due to dbt not recognizing that dbt is installed in a virtual environment instead of the local machine.

>*Additional note: Before running any additional dbt command go the [_sources.yml](./dbt/hard_drive_data/models/staging/_sources.yml) file and update the database section by entering your project ID where it states: `{{ env_var('GCP_PROJECT_ID', 'my-project-id') }}`. Unfortunately due to my Google Cloud trial expiring, I did not have time to figure out why the project ID would not import automatically. 😔

5. Run `dbt debug --profiles-dir=./profiles --project-dir=./hard_drive_data` to test if connection is working. If checks failed address issues. Common solutions to issues include:
  - Make sure the project ID is correct in profile.yml
  - Make sure you are running commands while in dbt folder since profile-dir and project-dir references from the `dbt/` folder
  - Make sure your google_credential.json file is in correct folder. As alternative you can replace the relative path in your `profile.yml` file and put the absolute file path instead.
6. Run `dbt deps --profiles-dir=./profiles --project-dir=./hard_drive_data` or `uv run dbt deps --profiles-dir=./profiles --project-dir=./hard_drive_data` to install dbt packages
7. Run `dbt build --profiles-dir=./profiles --project-dir=./hard_drive_data` or `uv run dbt build --profiles-dir=./profiles --project-dir=./hard_drive_data` to build, test, and create all data models

<img src="./docs/images/dbt-dag.png">

*Figure 4. dbt lineage model overview*

## Locally Running Streamlit App
- In the terminal go to the project root directory: `hard_drive_failure_analytics_dashboard/`
- Run `uv run streamlit run webapp/dashboard_app.py` or `streamlit run webapp/dashboard_app.py` if your virtual environment is active in terminal.
- If you are not automatically redirected, go to `http://localhost:8501`.
- After a few moments, the Storage Drive Analytics Dashboard visualizations should appear.

## And finally, Thank you! 😄
Thank you very much for taking the time to review my project, if you came across any issues or have any questions please feel free to contact me by submitting an [issue](https://github.com/ammartin8/hard_drive_analytics_dashboard/issues) on Github! If found you had to run alternative commands due to being Mac or Windows, please feel free to submit an issue and I can add instructions in the README.md for others to follow.

## Appendix

### Complete Project Directory Structure
```bash
hard_drive_failure_analytics_dashboard
├── .google
│   ├── credentials
│   │   └── google_credentials.json
├── airflow
│   ├── config
│   │   └── airflow.cfg
│   ├── dags
│   │   └── data_etl.py
│   ├── Dockerfile
├── ├── logs
│   └── plugins
├── dbt
│   └── hard_drive_data
│       ├── analyses
│       │   ├── datacenter_list_review.sql
│       │   ├── failure_attrs_review.sql
│       │   ├── model_cnt_review.sql
│       │   └── model_list_review.sql
│       ├── dbt_project.yml
│       ├── macros
│       ├── models
│       │   ├── intermediate
│       │   │   ├── int_fct_drive_add_cols.sql
│       │   │   └── schema.yml
│       │   ├── mart
│       │   │   ├── dim_date.sql
│       │   │   ├── dim_device_inventory.sql
│       │   │   ├── fct_drive_health_snapshots.sql
│       │   │   ├── reporting
│       │   │   │   ├── latest_quarterly_drive_trends_per_manufacturer.sql
│       │   │   │   ├── monthly_fail_rates.sql
│       │   │   │   ├── quarterly_fail_drives_per_manufacturer.sql
│       │   │   │   └── schema.yml
│       │   │   └── schema.yml
│       │   └── staging
│       │       ├── _sources.yml
│       │       └── stg_hard_drive_data.sql
│       ├── package-lock.yml
│       ├── packages.yml
│       ├── README.md
│       ├── seeds
│       │   └── 2026_04_11_model_manufacturer_lookup.csv
│       ├── snapshots
│       └── tests
├── .env
├── docker-compose.yaml
├── Dockerfile
├── docs
│   ├── IMPLEMENTATION_GUIDE.md
│   └── BigQuery_SQL_Cmd.sql
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── terraform
│   ├── main.tf
│   ├── terraform.tfstate.backup
│   └── variables.tf
├── uv.lock
└── webapp
    ├── dashboard_app.py
    └── styles.css
```