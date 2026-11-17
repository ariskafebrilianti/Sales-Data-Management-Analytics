# End-to-End Sales Data Management & Analytics System

An end-to-end sales data management and analytics project built with Python, PostgreSQL, SQL, and Streamlit. This project demonstrates how raw sales data can be transformed into a structured relational database, validated through an ETL workflow, and presented through an interactive transaction management application and analytics dashboard.

## Project Overview

This project was developed to simulate a structured sales data management workflow, from raw data ingestion to business performance analysis.

The system combines data profiling, data quality assessment, relational database design, ETL processing, SQL analytics, transaction input, transaction history, and an interactive dashboard.

## Key Features

### 1. Data Profiling & Quality Assessment

- Explored the source dataset using Python and Pandas.
- Assessed missing values, duplicates, invalid records, and data consistency.
- Validated dates, numeric fields, product mappings, and transaction status.
- Reconciled transaction-level source data against database records.

### 2. Relational Database Design

Implemented a PostgreSQL database using Supabase with four main tables:

- `raw_sales_staging`: stores imported source records.
- `customers`: stores normalized customer information.
- `products`: stores product codes, categories, and MSRP.
- `transactions`: stores structured sales transactions with customer and product relationships.

### 3. ETL & Data Validation

- Imports raw CSV data into the staging table.
- Applies data type conversion and validation.
- Loads customer, product, and transaction records into normalized tables.
- Uses database constraints and foreign keys to maintain data integrity.
- Performs source-to-target reconciliation.

### 4. Transaction Management Application

Built with Streamlit:

- Select existing customers and products.
- Enter transaction date, quantity, selling price, and deal size.
- Generate unique transaction references automatically.
- Validate required inputs before saving.
- Store valid transactions in PostgreSQL.

### 5. Transaction History

- View stored transactions.
- Search by transaction reference, customer name, or product code.
- Filter transactions by Profit/Loss status and deal size.
- Review transaction details from the database.

### 6. Interactive Analytics Dashboard

Built with Streamlit and Plotly, including:

- Executive Overview: sales, profit/loss, profit margin, transaction, customer, product, and quantity KPIs.
- Monthly Sales Trend.
- Product Performance.
- Customer Performance.
- Geographic Sales Performance.
- Deal Size Performance.

Dashboard data is cached for up to five minutes and can be refreshed manually.

## Dataset

| Attribute            | Description                  |
| -------------------- | ---------------------------- |
| Source file          | `Sales_dataset.csv`          |
| Format               | CSV, semicolon-delimited     |
| Imported source rows | 2,824                        |
| Transaction records  | 2,823                        |
| Summary rows         | 1                            |
| Usable source fields | 18                           |
| Transaction period   | January 2023 – December 2025 |
| Unique customers     | 92                           |
| Unique product codes | 109                          |
| Product categories   | 7                            |
| Cities               | 73                           |
| Countries            | 19                           |

The source file contains one summary row in addition to the transaction records. The summary row is excluded from the normalized transaction table. An empty unnamed column is also removed during ingestion.

### Transaction-Level Summary

| Metric             |        Value |
| ------------------ | -----------: |
| Total Transactions |        2,823 |
| Total Quantity     |       99,067 |
| Total Sales        | 8,291,713.60 |
| Total Profit/Loss  | 3,293,041.70 |
| Profit Margin      |       39.71% |

**Note:** The source currency unit has not been independently confirmed. Financial values are therefore presented without assuming a specific currency.

## Important Data Assumptions

- **Estimated Cost Price:** The estimated cost is based on 50% of MSRP. It is an assumption from the source dataset, not actual procurement or operating cost data.
- **Customer Identifier:** `CUSTOMER_CODE` is unique at the transaction level and is stored as a source transaction reference, not treated as a customer identifier.
- **Customer Records:** Customer entities are identified using customer name and location information.
- **Source Summary:** Transaction-level records are used as the reporting baseline. The original summary row does not exactly reconcile with the detailed transaction totals.
- **Profitability:** Profit and profit margin are calculated using the estimated cost assumption and should not be interpreted as audited company profit.

## Analytical SQL Views

The project uses six SQL views to support dashboard reporting:

1. `vw_sales_kpis`
2. `vw_monthly_sales`
3. `vw_product_performance`
4. `vw_customer_performance`
5. `vw_geographic_sales`
6. `vw_deal_size_performance`

## Technology Stack

| Area            | Tools                 |
| --------------- | --------------------- |
| Programming     | Python                |
| Data Processing | Pandas, NumPy         |
| Database        | PostgreSQL, Supabase  |
| Database Access | SQLAlchemy, psycopg   |
| Data Analysis   | SQL, Jupyter Notebook |
| Application     | Streamlit             |
| Visualization   | Plotly                |
| Version Control | Git, GitHub           |

## Project Structure

```text
Sales-Data-Management-Analytics/
│
├── .github/
│   └── workflows/
│
├── app/
│   ├── pages/
│   │   ├── 1_Transaction_History.py
│   │   └── 2_Analytics_Dashboard.py
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── rejected/
│
├── docs/
│
├── notebooks/
│
├── sql/
│
├── src/
│   ├── load_staging.py
│   └── test_db_connection.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

The raw source dataset and environment configuration are kept locally and are excluded from version control.

## Getting Started

### Prerequisites

- Python
- A Supabase PostgreSQL database
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/ariskafebrilianti/Sales-Data-Management-Analytics.git

cd Sales-Data-Management-Analytics
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv

source .venv/Scripts/activate
```

For Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
DB_HOST=your_supabase_host
DB_PORT=5432
DB_NAME=postgres
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Replace the placeholder values with your own Supabase PostgreSQL connection details.

**Never commit the `.env` file or expose database credentials.**

### 5. Prepare the Database

Execute the SQL scripts in the `sql/` directory to create the required database structures, populate the normalized tables, and create the analytical views.

### 6. Prepare the Source Dataset

Place the source CSV file at:

```text
data/raw/Sales_dataset.csv
```

The raw dataset is not included in this repository.

### 7. Import the Source Data

After the staging table and database connection are ready, run:

```bash
python src/load_staging.py
```

The script validates the source structure, checks the expected row count and summary row, generates an import batch identifier, and loads the source records into `raw_sales_staging`.

Complete the remaining ETL steps using the SQL scripts in the `sql/` directory before launching the application.

### 8. Run the Streamlit Application

```bash
streamlit run app/streamlit_app.py
```

The application provides three pages:

- Transaction Input
- Transaction History
- Analytics Dashboard

## Testing & Validation

Manual application testing has been performed to verify:

- Streamlit application startup and database connectivity.
- Transaction form validation.
- Successful transaction insertion.
- Database calculation and data integrity.
- Transaction History visibility and filtering.
- QA transaction cleanup.
- Dashboard refresh and KPI consistency.

The original transaction dataset was restored after QA testing.

## Project Status

**Core implementation and manual application testing completed.**

The project includes data profiling, a normalized PostgreSQL database, ETL processing, SQL analytical views, a Streamlit transaction management application, transaction history, and an interactive analytics dashboard.

Documentation and portfolio presentation are being finalized.

## Disclaimer

This is an educational portfolio project developed for data analytics and data management learning purposes. The estimated cost calculation is based on a 50% MSRP assumption and does not represent actual business cost data.
