# Data Quality Assessment Report

## End-to-End Sales Data Management & Analytics System

| Document Information | Details                                                |
| -------------------- | ------------------------------------------------------ |
| Document Version     | 1.0                                                    |
| Last Updated         | 21 November 2026                                       |
| Source Dataset       | `Sales_dataset.csv`                                    |
| Assessment Type      | Initial Profiling, Data Validation, and Reconciliation |

---

## 1. Executive Summary

A Data Quality Assessment (DQA) was performed on the original sales dataset before loading the records into the normalized PostgreSQL database.

The assessment covered dataset structure, completeness, numeric data conversion, duplicate detection, date validation, customer and product consistency, business rule validation, and source-to-transaction reconciliation.

The original dataset contained 2,824 imported rows and 19 detected columns. After excluding one aggregate summary row and one empty unnamed column, 2,823 transaction records and 18 usable source fields remained.

Most structural and validation checks passed. Financial reconciliation identified differences between source-level totals and transaction-level calculations. These differences were investigated and documented rather than silently adjusted.

## 2. Dataset Overview

| Metric                     |     Result |
| -------------------------- | ---------: |
| Imported source rows       |      2,824 |
| Detected columns           |         19 |
| Empty unnamed columns      |          1 |
| Aggregate summary rows     |          1 |
| Usable transaction records |      2,823 |
| Usable source fields       |         18 |
| Unique customers           |         92 |
| Unique products            |        109 |
| Product categories         |          7 |
| Cities                     |         73 |
| Countries                  |         19 |
| Transaction start date     | 2023-01-04 |
| Transaction end date       | 2025-12-01 |

The source dataset includes one summary row labeled `Total`. It contains aggregated values rather than an individual transaction and is excluded from transaction-level processing.

The empty column `Unnamed: 18` is also excluded from the working dataset.

**Scope:** These metrics describe the original source dataset and exclude subsequent manual transactions and Faker-generated synthetic records.

## 3. Initial Data Quality Findings

The initial investigation identified the following issues:

| Finding               | Description                                                    | Treatment                                   |
| --------------------- | -------------------------------------------------------------- | ------------------------------------------- |
| Aggregate summary row | One row contains `Total` rather than an individual transaction | Excluded from transaction-level processing  |
| Empty column          | `Unnamed: 18` contains no useful data                          | Excluded                                    |
| Column formatting     | Some column names contain unnecessary spaces or tab characters | Standardized in the working copy            |
| Numeric formatting    | Numeric fields use European number formatting                  | Converted into numeric data types           |
| Invalid summary date  | The aggregate row contains `#VALUE!` in `ORDER_DATE`           | Summary row excluded before date validation |
| Estimated cost        | Cost values follow a 50% MSRP assumption                       | Retained and documented as an estimate      |

The original raw dataset was preserved. Cleaning and transformation activities were performed on a working copy.

## 4. Completeness and Data Type Validation

Seven numeric fields were identified for conversion:

- `QUANTITY_ORDERED`
- `MSRP`
- `Estimated Cost Price (50%)`
- `Selling price`
- `SALES`
- `Profit per unit`
- `Total profit / loss`

The numeric conversion process successfully converted the validated transaction fields to numeric types without introducing missing values.

Customer name completeness was also checked across the 2,823 transaction records.

### Assessment Results

| Check                                           | Result                 |
| ----------------------------------------------- | ---------------------- |
| Numeric field conversion                        | Successful             |
| Numeric conversion errors                       | 0                      |
| Missing values introduced by numeric conversion | 0                      |
| Customer names after normalization              | 2,823 non-null records |
| Quantity values                                 | Whole numbers          |

## 5. Duplicate Assessment

Duplicate checks were performed at both full-row and customer-product combination levels.

| Validation                              | Result |
| --------------------------------------- | -----: |
| Duplicate full transaction rows         |      0 |
| Duplicate customer-product combinations |      0 |

No duplicate full transaction records or duplicate customer-product combinations were identified in the cleaned transaction dataset.

Repeated customer or product appearances across different transactions are valid and are not treated as duplicates.

## 6. Date Validation

The order date field was parsed using the source date format and compared against the source month and year fields.

The initial month comparison identified formatting differences because the source used abbreviated month names, while the parsed date values initially used full month names.

The month values were subsequently normalized to a consistent abbreviated format before final validation.

### Final Date Validation Results

| Validation                           | Invalid Records |
| ------------------------------------ | --------------: |
| Invalid dates                        |               0 |
| Month mismatches after normalization |               0 |
| Year mismatches                      |               0 |

### Validated Date Range

- Minimum order date: 2023-01-04
- Maximum order date: 2025-12-01

All 2,823 transaction records passed the final date validation checks.

## 7. Numeric and Business Rule Validation

### 7.1. Quantity Validation

| Metric                       | Result |
| ---------------------------- | -----: |
| Minimum quantity             |      6 |
| Maximum quantity             |     97 |
| Non-integer quantity records |      0 |

All quantity values were whole numbers within the observed range.

### 7.2. Status Validation

Transaction status was compared against the classification derived from total profit or loss.

| Metric               | Result |
| -------------------- | -----: |
| Records tested       |  2,823 |
| Matching records     |  2,823 |
| Non-matching records |      0 |

The final status validation achieved a 100% match with the source classification.

### 7.3. Product Consistency

Product codes were checked for inconsistent product category assignments.

| Validation                             | Result |
| -------------------------------------- | -----: |
| Unique product codes                   |    109 |
| Product codes with multiple categories |      0 |

No product-code-to-category inconsistencies were identified.

### 7.4. Customer Consistency

Customer names were checked for inconsistent geographic assignments.

| Validation                        | Result |
| --------------------------------- | -----: |
| Customers with multiple cities    |      0 |
| Customers with multiple countries |      0 |

The observed customer records maintained consistent city and country assignments.

## 8. Financial Reconciliation

Financial reconciliation was conducted at two levels:

1. Transaction totals compared with the aggregate summary row.
2. Individual transaction calculations compared with source financial fields.

### 8.1. Transaction Totals vs. Source Summary

The aggregate summary row was retained separately for reconciliation after being excluded from transaction-level analysis.

| Metric            | Finding                                                          |
| ----------------- | ---------------------------------------------------------------- |
| Total quantity    | Matches the source summary at 99,067 units                       |
| Total sales       | Calculated transaction sales exceed the source summary by 6.80   |
| Total profit/loss | Calculated transaction profit exceeds the source summary by 5.90 |

The quantity reconciliation matched exactly. Small differences remained in the sales and profit totals.

### 8.2. Transaction-Level Formula Reconciliation

Sales and profit values were compared against calculations derived from quantity, selling price, and profit per unit.

The refined reconciliation identified:

| Metric      | Total Difference | Rows with Differences | Maximum Absolute Difference |
| ----------- | ---------------: | --------------------: | --------------------------: |
| Sales       |          -229.20 |                 1,341 |                        4.20 |
| Profit/Loss |          -195.20 |                 1,341 |                        4.20 |

The differences were retained for investigation and were not overwritten during initial profiling.

### 8.3. Unit Profit Validation

Unit profit was compared against selling price minus estimated cost per unit.

| Metric                      | Result |
| --------------------------- | -----: |
| Rows with differences       |     11 |
| Total difference            |  -1.10 |
| Maximum absolute difference |   0.10 |

The observed differences are consistent with the need to account for source financial precision and rounding behavior.

### 8.4. Selling Price Precision Validation

The initial standard price rounding test did not reproduce every source selling price.

Further investigation showed that the source values were consistent when implied unit prices were calculated using decimal arithmetic and `ROUND_HALF_UP` to one decimal place.

| Metric                    | Result |
| ------------------------- | -----: |
| Transactions tested       |  2,823 |
| Matching transactions     |  2,823 |
| Non-matching transactions |      0 |

The final decimal half-up validation achieved a 100% match.

This finding informed the project's financial calculation and rounding implementation.

## 9. Data Preparation and Cleaning Decisions

The following preparation decisions were applied:

1. Preserve the original raw dataset.
2. Exclude the aggregate summary row from transaction-level processing.
3. Remove the empty unnamed column from the working dataset.
4. Standardize source column names.
5. Convert European-formatted numeric values into appropriate numeric types.
6. Parse and normalize order dates.
7. Validate month and year consistency.
8. Validate customer and product reference consistency.
9. Reconcile transaction totals against the source summary.
10. Retain unexplained financial differences for documentation rather than silently adjusting source values.

These decisions support traceability between the original source data, cleaned transaction records, and the normalized database.

## 10. Data Quality Limitations and Assumptions

### 10.1. Estimated Cost

The estimated cost per unit is based on 50% of MSRP.

This is a dataset assumption, not independently verified procurement or production cost.

### 10.2. Currency

The original dataset does not explicitly identify its currency.

Dashboard values use USD ($) formatting for presentation purposes only. No currency conversion or independent currency verification has been performed.

### 10.3. Financial Precision

Small source-to-calculation differences were identified during reconciliation.

The final rounding investigation reproduced all 2,823 source selling prices using decimal half-up rounding. Other transaction-level financial differences remain documented and are not silently corrected.

### 10.4. Deal Size Classification

The source contains three deal-size categories:

- Small
- Medium
- Large

The categories are retained as provided by the source. Their underlying quantity thresholds have not been independently established.

## 11. Overall Assessment

The original dataset passed the final structural, date, quantity, status, customer consistency, and product consistency checks.

The assessment also identified source-level and transaction-level financial differences that require transparent documentation.

| Assessment Area                         | Final Result            |
| --------------------------------------- | ----------------------- |
| Dataset structure                       | Valid after preparation |
| Summary row handling                    | Completed               |
| Numeric conversion                      | Successful              |
| Duplicate full rows                     | 0 found                 |
| Duplicate customer-product combinations | 0 found                 |
| Quantity validation                     | Passed                  |
| Date validation                         | Passed                  |
| Status validation                       | 2,823 of 2,823 matched  |
| Customer geographic consistency         | Passed                  |
| Product category consistency            | Passed                  |
| Quantity reconciliation                 | Exact match             |
| Financial reconciliation                | Differences documented  |
| Final selling price precision test      | 2,823 of 2,823 matched  |

**Conclusion:** The cleaned transaction dataset was suitable for subsequent ETL processing and relational database loading, with the identified financial reconciliation differences and source assumptions retained as documented limitations.

---

## 12. Related Project Documentation

- `README.md` – Project overview, features, installation, and usage.
- `docs/data_dictionary.md` – Source fields, database tables, relationships, and business rules.
- `docs/erd.md` – Entity relationship diagram.
- `notebooks/01_data_profiling.ipynb` – Initial data profiling and quality assessment.
