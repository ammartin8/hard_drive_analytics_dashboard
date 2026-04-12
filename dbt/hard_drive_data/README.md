# Hard Drive Failure Analytics & Telemetry

This dbt project ingests raw hard drive telemetry data from the `hard_drive_dataset`, transforms it into intermediate fact tables, and constructs mart-level reporting views for failure analysis. It supports monitoring of drive health (S.M.A.R.T attributes) and historical failure trend analysis by manufacturer, quarter, and cluster.

## Quick Start

### Prerequisites
- **Python 3.9+**
- **dbt CLI** installed locally (`pip install dbt-core`)
- Access to the underlying BigQuery dataset (`hard_drive_dataset`) via service account or GCP credentials.

### Installation & Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hard_drive_failure_analytics_dashboard
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   # If using dbt via virtual environment
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   pip install -r requirements_dev.txt
   ```
3. Configure credentials:
   Create a file named `~/.dbt/profiles.yml` (or point to one in the project root) with your BigQuery credentials.

4. Verify Installation:
    Run a dry-run of dbt to ensure it connects successfully:
    ```bash
    dbt debug
    ```

### Running the Project
**1. Sync dbt Packages**
This command reads your packages.yml file and downloads all required plugins (e.g., dbt-bigquery, dbt-utils) to your local .dbt_packages folder. Run this first time.
    ```bash
    dbt deps
    ```
**2. Run all data transformations:**
   ```bash
   dbt run --full-refresh
   ```

**3. Validate data quality tests (uniqueness, null checks):**
   ```bash
   dbt test
   ```

**4. Generate documentation:**
   ```bash
   dbt docs generate && dbt docs serve
   ```

### Key Commands
- **Selectively build a model:** `dbt run --select +mart.reporting.latest_quarterly_drive_trends_per_manufacturer`
- **Debug connection issues:** `dbt debug`

## 📊 Data Dictionary & Schema Overview

| Layer | Description | Key Metrics/Columns |
| :--- | :--- | :--- |
| **Staging** | Raw ingestion from data source | `date`, `smart_{num}_raw` |
| **Intermediate** | Cleaned & enriched with derived fields (e.g., `capacity_gigabytes`). | `unique_device_event_id`, `report_date` |
| **Mart** | Aggregated views for reporting. | `failure_rate` (monthly/quarterly), `failed_drives_per_manufacturer` |

## 🔐 Access & Credentials
- **Source System:** BigQuery Project ID: `<your-project-id>`
- **Dataset Name:** `hard_drive_dataset`
- **Permissions Required:**
  - `BigQuery.DataViewer` (for reading raw sources)
  - `BigQuery.DataEditor` (if writing to warehouse)
  - Service Account credentials are stored in `.dbt/profiles.yml`.

## 🤝 Contact & Support
- **Data Engineer:** [ammartin8](https://github.com/ammartin8)
- **Issue Tracking:** GitHub Issues

## 🛠️ Technical Notes
- **Adapter:** `bigquery`
- **Database Engine:** Google Cloud Platform (BigQuery)
- **Default Refresh Strategy:** Quarterly batch processing
- **Testing:** Models include `unique_device_event_id` uniqueness constraints and not null checks.

## 📚 Additional Resources
- [dbt Docs](https://docs.getdbt.com/)
- [Google BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
