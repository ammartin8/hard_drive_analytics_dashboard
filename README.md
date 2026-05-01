# 📊 Project Plan: Storage Drive Analytics Dashboard

### 🔧 Status: Beta Version Complete

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
## About Me

### 🚀 Ready for a Data Engineering Challenge!
Hello 🌎️! I'm Amah! I am passionate about building scalable, reliable, and efficient data systems that empower business intelligence. This project demonstrates my ability to handle the full lifecycle of data—from ingestion to production deployment on GCP.

### 👋🏿 Connect With Me
LinkedIn: [Linkedin Profile](https://www.linkedin.com/in/amahmartin) \
GitHub: [Github Profile](https://github.com/ammartin8)


---

## 📖 Table of Contents

1. [Project Overview](#project-overview)
2. [Dataset & Scope](#dataset--scope)
3. [Architecture & Data Flow](#architecture--data-flow)
4. [Technology Stack](#technology-stack)  
5. [How to Run - Installation and Execution Guide](#how-to-run-the-project)

---

## Project Overview

**Problem Statement**

Everyday users, including photographers, home lab enthusiasts, and small business owners, rely on consumer-grade storage drives that they cannot afford to replace frequently. Data loss can result from the unpredictable failure of specific drive models, causing catastrophic data loss and financial damage. Currently, consumers purchase storage based on marketing specifications such as speed and capacity rather than empirical evidence regarding real-world longevity.

**Solution**

This project bridges the gap between enterprise telemetry and consumer accessibility by processing daily health snapshots from Backblaze to extract, transform, and visualize granular S.M.A.R.T. data. S.M.A.R.T stands for Self-Monitoring, Analysis, and Reporting Technology and is a monitoring system included in hard drives that reports on various attributes of the state of a given drive. Based on reported experience from Backblaze, they have found the following five SMART attributes indicate impending disk drive failure:
- SMART 5: Reallocated_Sector_Count
- SMART 187: Reported_Uncorrectable_Errors
- SMART 188: Command_Timeout
- SMART 197: Current_Pending_Sector_Count
- SMART 198: Offline_Uncorrectable

Backblaze counts a drive as **failed** when it is removed from a storage pod and replaced because it has **1) totally stopped working**, or **2) because it has shown evidence of failing soon**

The resulting dashboard identifies which models maintain performance over time and highlights brands with high failure rates.

**Target Audience**

The data benefits:
- Creators & Photographers: Who need reliable archival storage but can't rely solely on volatile system drives.
- Home Lab Enthusiasts: Building their first NAS and needing to know which drives survive the long haul before establishing redundancy.
- Small Businesses: Seeking secure data retention without enterprise-grade IT budgets.
- Casual Users: Anyone wanting peace of mind that their personal digital collection will last.

**The Goal**

To provide access to drive reliability data, shifting users from passive trust in marketing claims to active, evidence-based hardware selection. The project ingests, processes, transforms, and visualizes Backblaze's storage drive failure dataset.

**Dashboard Components**

The dashboard displays the following metrics and visualizations:
- **KPI Metric 1**: Most Recent Active Drives
- **KPI Metric 2**: Total Failed Drives 
- **Visual Chart 1**: Distribution of hard drive failure rates by manufacturer (categorical).  
- **Visual Chart 2**: Active and failed storage drive trends over time (stacked bar chart).
- **Table 1**: List of models, total drives, failed drives, and failure rate by quarter

<img src="./docs/images/main_dashboard_image.png">

*Figure 1: Main dashboard view*


<img src="./docs/images/dashboard_demo.gif">

*Figure 2: Dashboard interactive demo*

The pipeline is **batch-oriented**, orchestrated via Apache Airflow (Docker container), with Python-based ETL tasks and dbt for transformations. BigQuery stores final star schema tables, and Streamlit provides the interactive dashboard. Infrastructure is provisioned via Terraform and containerized using Docker.

---

## Dataset & Scope

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

## Architecture & Data Flow

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

## Technology Stack

| Layer              | Technology             | Purpose                                                                 |
|--------------------|------------------------|-------------------------------------------------------------------------|
| Cloud              | Google Cloud           | Hosting GCS, BigQuery                         |
| Data Lake          | Google Cloud Storage   | Raw and processed Parquet data storage                                |
| Data Warehouse     | BigQuery               | Optimized storage and querying for dashboard                         |
| ETL & Batch        | Apache Airflow (Python)| ETL jobs via `@dag` and `@task` decorators with Pandas/PyArrow         |
| Transformation     | dbt                    | Define transformations (e.g., star schema)                            |
| Dashboard          | Streamlit              | Interactive UI with multiple tiles tiles                                         |
| Infrastructure     | Terraform              | Provision GCS, BigQuery instances                    |
| Containerization   | Docker                 | Package Airflow + ETL + dbt & streamlit app for reproducibility                  |

---

## How to Run the Project
Follow these steps to deploy, run, and visualize your Storage Drive Analytics Dashboard Using Google Cloud.

1. **Prerequisites**
    - A valid Google Cloud Platform (GCP) account
    - A Google Cloud Service Account with the following assigned role accesses:
        - BigQuery Admin
        - Storage Admin
        - Storage Object Admin
    - `gcloud` CLI installed and authenticated (`gcloud auth application-default login`)
    - Git (to clone this repository)
    - Docker CLI and Docker Compose installed
    - Terraform installed

> **Note**: Since the original development was done on an Ubuntu/Debian Linux desktop, you may need to adjust certain commands or file path structures if you are using a different operating system. In addition, the templates provided assume you will save Google credentials in .google/credentials and navigate to specific folders as instructed.

2. Clone the Repository
    - `git clone https://github.com/ammartin8/hard_drive_analytics_dashboard.git`
    - `cd hard_drive_failure_analytics_dashboard`

3. Configure Secrets & Environment
    - In the project root folder (hard_drive_failure_analytics_dashboard/), rename the `.env.example` file to `.env`
    - Edit the .env file by assigning your google project ID, and google cloud bucket environment variables. You can change the airflow environment variables as well. Be sure to recall the `AIRFLOW_USER` and `AIRFLOW_PASSWORD` values as you'll need them to log into the Airflow UI.
    - Create a `.google/credentials` directory in the project root folder `hard_drive_failure_analytics_dashboard/` and export your service account key you created in Google Cloud Platform as a json file and store it in the following directory in your project project folder:
    ```bash
    hard_drive_failure_analytics_dashboard <---- project root folder
    ├── .google
    │   ├── credentials
    │   │   └── google_credentials.json
    ```

**Note**: Since the `docker-compose.yaml` references your service account as `google_credentials.json`, you should save your service account key with the same name; otherwise, you will need to update the name referenced in the `docker-compose.yaml` file

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


>**Note**: This will create a bucket in data-lake and dataset in BigQuery.

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
```bash
hard_drive_failure_analytics_dashboard <-------project root directory
└── airflow
    ├── config
    ├── dags
    ├── logs
    └── plugins
```

>**Note**: On **Linux**, the quick-start needs to know your host user id and needs to have group id set to `0`. Otherwise the files created in `dags`, `logs`, `config` and `plugins` will be created with `root` user ownership. You have to make sure to configure them for the docker-compose:

To get your user id, run `id -u` in your terminal to get your user ID, then update `AIRFLOW_UID` in your .env file with that number.

For other operating systems, you may get a warning that AIRFLOW_UID is not set, but you can safely ignore it. You can also manually add the assigned value below in the .env file to get rid of the warning:

```bash
AIRFLOW_UID=50000
```

Now you can run the airflow image:
`docker compose up -d`

This process will do the following: 
- build a custom lighter version docker build for Airflow
- Install uv package manager
- Create a virtual environment
- Install python dependencies based on uv.lock file

> **Note**: Sometimes the airflow docker build seems to fail for some reason. Try to rerun and it should build successfully. In addition, upon first run, it may take time for the docker containers to all be started. The hard_drive_analytics_dashboard-airflow-init-1 container typically can take up to 5-10 minutes to start depending on compute resources.


## Airflow ETL Process
<img src="./docs/images/airflow_ui_example.png">

*Figure 3: Airflow web interface showing task instances and DAG dependencies.*

Once airflow docker image is up and running, head to `http://localhost:8080` and login to airflow using the assigned credentials in your .env file. Once logged in, go to The left sidebar and click `Admin` then `Connections`. To run data_etl_v2 pipeline, you must set up a Google Cloud connection in airflow UI first.
- Select `Add Connection`
- In the Connection ID enter: `gcp`
- In Connection Type search for `Google Cloud` and select it
- Select `Extra Fields` and in `Keyfile Path` section input the file path to your google credentials: `/.google/credentials/google_credentials.json` (forward slash should also be included as well)
- Go to the bottom of the form and click `Save`
- Test your connection by going to far right and clicking the line-chart symbol (next to edit button). If the connection turns green you have successfully connected to Google Cloud Platform! If not, double check to make sure you have the correct file path to your google_credential.json file.
- In the left sidebar, go to `Dags` > click on `data_etl_dag_v2` workflow > then click on the `Trigger` play button in top-right corner of UI > and select `Single Run` and click `Trigger` play button again. 

>**Special Note & Considerations:** The `data_etl.py` file is currently set to download only 4 zip files **2025 Q1-Q4 data only** (each unzipped file is a total of ~12 GB of data). Extracting all 2024 & 2025 years and unzipping is ~87.3 GB of data. Depending on compute resources run can take time (for me, it was 5-7 mins for 1 year of data on a local desktop machine). 
>
>If you have limited resources I would recommend keeping to just downloading a few files just for demo testing. Otherwise, you can update the [data_etl.py](./airflow/dags/data_etl.py) file in the airflow/dags folder and update `YR_START`, `YR_END`, and `QTR_START` and `QTR_END` data fields to pull more data.
>
>*For reference on a laptop with 15 GB of RAM and 12 cores CPU, it took 26 minutes to download 2 full years of data and used nearly 70% of RAM and 40% of CPU.

The etl process is downloading zip file from source > extract zip file > converting to parquet > then loading to GCS.

## BigQuery Process
- Verify that files are loaded in your Google Cloud Storage bucket.
- In BigQuery Studio open to new blank SQL query page then update, copy/paste and run the following SQL commands in BigQuery to create your source datasets: [BigQuery_SQL_Cmd.sql](docs/BigQuery_SQL_Cmd.sql)

> **Partition Strategy**
>
> The materialized source table is set to be partition by combination of year and month. Since the dashboard is currently setup to report by month or quarter it seems to make sense to set up to partition by year_month that way, the partition sizes are not too big or too small and it will be easy to query the data by month, quarter, and year as they will likely be the most common filters used.

## dbt Process
1. In terminal go to dbt folder: `cd dbt`
2. If your `.venv` virtual environment folder hasn't been created yet, run `uv run dbt --version` (this will install all packages into your virtual environment and then check the dbt version). Upon completion, the dbt version should output in command line. 
3. There are two ways to run dbt commands (choose one as either way works the same):
    - **(Option 1)** Activate .venv virtual environment and run dbt commands as normal. (Remaining instructions are provided assuming using Option 1)
        1. Activate `.venv` environment by running: `source ../.venv/bin/activate`
    - **(Option 2)** Always add `uv run` before running any dbt commands (ex. `uv run dbt debug`)
4. Make sure you in the dbt folder (`cd dbt`), run `source ../../.env` to import environment variables from project root

> **Note**: You  may get a error message in your dbt_project.yml file stating dbt configuration is invalid. You can safely ignore this error since this is likely due to dbt not recognizing that dbt is installed in a virtual environment instead of the local machine.

>*Additional note: Before running any additional dbt commands go to the [_sources.yml](./dbt/hard_drive_data/models/staging/_sources.yml) file and update the database section by replacing `my-project-id` with your actual project ID: `{{ env_var('GCP_PROJECT_ID', 'my-project-id') }}`.

5. Go to the `example.profiles.yml` in the `dbt/profiles` folder and rename it to profiles.yml. Then update the file by entering your google project ID.

6. Make sure your terminal is in the `dbt/` directory and then run `dbt debug --profiles-dir=./profiles --project-dir=./hard_drive_data` to test if connection is working. If any checks fail, address the issues. Common solutions to issues include:
  - Making sure the project ID is correct in profile.yml
  - Making sure you are running commands while in dbt folder since profile-dir and project-dir references from the `dbt/` folder
  - Making sure your google_credential.json file is in the correct folder and referenced correctly. As an alternative, you can replace the relative path in your `profiles.yml` file and put the absolute file path instead.
  - If you are using Option 2 to run dbt commands, make sure to add `uv run` before the command
7. Run `dbt deps --profiles-dir=./profiles --project-dir=./hard_drive_data` to install dbt packages
8. Run `dbt build --profiles-dir=./profiles --project-dir=./hard_drive_data` to build, test, and create all data models.

Now all data tables are created in your BigQuery dataset.

<img src="./docs/images/dbt-dag.png">

*Figure 4: dbt lineage model overview*

## Locally Running Streamlit App
- In the terminal go to the project root directory: `hard_drive_failure_analytics_dashboard/`
- Run `uv run streamlit run webapp/dashboard_app.py` or `streamlit run webapp/dashboard_app.py` if your virtual environment is active in terminal.
- If you are not automatically redirected, go to `http://localhost:8501`.
- After a few moments of waiting for the data to load, the Storage Drive Analytics Dashboard visualizations should appear.

## And finally, Thank you! 😄
Thank you very much for taking the time to review my project, if you come across any issues or have any questions please feel free to contact me by submitting an [issue](https://github.com/ammartin8/hard_drive_analytics_dashboard/issues) on Github! If you had to run alternative commands due to being on a Mac or Windows operating system, please feel free to submit an issue and I can add instructions in the README.md for others to follow.

## Appendix

### Data Source
Backblaze. (2024-2025). Hard Drive Test Data. Cloud Storage Resources.  
Retrieved [April 14th, 2026], from https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data

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


