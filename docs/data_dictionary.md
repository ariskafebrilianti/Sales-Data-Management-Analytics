# Data Dictionary

## Sales Data Management & Analytics System

**Document Version:** 1.0  
**Dataset:** Sales_dataset.csv  
**Source Records:** 2,823 transaction records  
**Profiling Date:** 10 November 2026

---

## 1. Dataset Overview

The dataset contains 2,823 transaction records covering the period from January 4, 2023, to December 1, 2025.

| Attribute           |                    Value |
| ------------------- | -----------------------: |
| Transaction records |                    2,823 |
| Unique customers    |                       92 |
| Unique products     |                      109 |
| Product categories  |                        7 |
| Cities              |                       73 |
| Countries           |                       19 |
| Date range          | 2023-01-04 to 2025-12-01 |

One additional summary row was identified and excluded from the transaction records. An entirely empty column (`Unnamed: 18`) was also identified and excluded from the cleaned dataset.

## 2. Source Data Dictionary

| Source Column              | Business Definition                                        | Target Data Type | Transformation / Validation                                                     |
| -------------------------- | ---------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------- |
| CUSTOMER_CODE              | Unique source code associated with each transaction record | VARCHAR          | Retain as source transaction identifier; business meaning requires confirmation |
| CUSTOMER_NAME              | Customer name                                              | VARCHAR          | Used to identify customer records                                               |
| QUANTITY_ORDERED           | Number of units ordered                                    | INTEGER          | Must be a positive whole number                                                 |
| MSRP                       | Manufacturer's suggested retail price                      | NUMERIC(12,2)    | Must be non-negative                                                            |
| Estimated Cost Price (50%) | Estimated product cost, calculated as 50% of MSRP          | NUMERIC(12,2)    | Retain as an estimate, not actual cost                                          |
| Selling price              | Selling price per unit                                     | NUMERIC(12,2)    | Must be non-negative                                                            |
| SALES                      | Total sales value of the transaction                       | NUMERIC(14,2)    | Retain original source value                                                    |
| Profit per unit            | Profit estimate per unit                                   | NUMERIC(12,2)    | Retain original source value                                                    |
| Total profit / loss        | Total estimated profit or loss for the transaction         | NUMERIC(14,2)    | Retain original source value                                                    |
| Status                     | Transaction profitability classification                   | VARCHAR          | Allowed values: Profit, Loss                                                    |
| ORDER_DATE                 | Transaction order date                                     | DATE             | Parse using `%A, %d %B %Y`                                                      |
| MONTH                      | Month derived in the source dataset                        | VARCHAR          | Derive                                                                          |
