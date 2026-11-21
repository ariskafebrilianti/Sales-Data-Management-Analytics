# Data Dictionary

## Sales Data Management & Analytics System

| Document Information       | Details             |
| -------------------------- | ------------------- |
| Document Version           | 1.1                 |
| Last Updated               | 21 November 2026    |
| Source Dataset             | `Sales_dataset.csv` |
| Source Transaction Records | 2,823               |

---

## 1. Dataset Overview

The original source dataset contains 2,823 transaction records covering the period from January 4, 2023, to December 1, 2025.

| Attribute              |                    Value |
| ---------------------- | -----------------------: |
| Imported source rows   |                    2,824 |
| Transaction records    |                    2,823 |
| Summary rows excluded  |                        1 |
| Source columns         |                       18 |
| Unique customers       |                       92 |
| Unique products        |                      109 |
| Product categories     |                        7 |
| Cities                 |                       73 |
| Countries              |                       19 |
| Transaction date range | 2023-01-04 to 2025-12-01 |

The source file contains one summary row labeled `Total`, which is excluded from transaction-level processing. An empty unnamed column is also excluded during ingestion.

**Scope note:** These figures describe the original source dataset only. They do not include manually entered transactions or Faker-generated synthetic transactions added later.

---

## 2. Source Data Dictionary

The following table describes the original source fields and their mapping into the staging and normalized database structures.

| Source Column                | Business Definition                              | Target Data Type | Transformation / Validation                                                                     |
| ---------------------------- | ------------------------------------------------ | ---------------- | ----------------------------------------------------------------------------------------------- |
| `CUSTOMER_CODE`              | Unique code associated with a source transaction | TEXT             | Mapped to `transactions.source_transaction_code`; not used as the customer primary key          |
| `CUSTOMER_NAME`              | Customer name                                    | TEXT             | Trimmed and matched together with city and country                                              |
| `QUANTITY_ORDERED`           | Number of units ordered                          | INTEGER          | Must be a positive whole number                                                                 |
| `MSRP`                       | Manufacturer's suggested retail price            | NUMERIC(12,2)    | Loaded into `products.msrp`; must be non-negative                                               |
| `Estimated Cost Price (50%)` | Estimated product cost per unit                  | NUMERIC(12,2)    | Based on the 50% MSRP assumption; not verified actual procurement cost                          |
| `Selling price`              | Selling price per unit                           | NUMERIC(12,2)    | Must be greater than zero                                                                       |
| `SALES`                      | Total sales value of the transaction             | NUMERIC(14,2)    | Converted to numeric and retained from the source                                               |
| `Profit per unit`            | Estimated profit or loss per unit                | NUMERIC(12,2)    | Converted to numeric and retained from the source; may be negative                              |
| `Total profit / loss`        | Total estimated transaction profit or loss       | NUMERIC(14,2)    | Converted to numeric and retained from the source; may be negative                              |
| `Status`                     | Transaction profitability classification         | TEXT             | Allowed values: `Profit`, `Loss`                                                                |
| `ORDER_DATE`                 | Transaction order date                           | DATE             | Parsed and normalized into a PostgreSQL DATE value                                              |
| `MONTH`                      | Month value provided in the source               | TEXT             | Used for date consistency validation; not stored separately in the normalized transaction table |
| `YEAR`                       | Year value provided in the source                | TEXT             | Used for date consistency validation; not stored separately in the normalized transaction table |
| `PRODUCT`                    | Product category                                 | TEXT             | Mapped to `products.product_category`                                                           |
| `PRODUCT_CODE`               | Product identifier in the source catalog         | TEXT             | Mapped to `products.product_code`                                                               |
| `CITY`                       | Customer city                                    | TEXT             | Trimmed and used in customer matching                                                           |
| `COUNTRY`                    | Customer country                                 | TEXT             | Trimmed and used in customer matching                                                           |
| `DEALSIZE`                   | Transaction deal size classification             | TEXT             | Allowed values: `Small`, `Medium`, `Large`                                                      |

**Important:** `CUSTOMER_CODE` is retained as a source transaction reference. The customer identity in the normalized database is based on `customer_name`, `city`, and `country`.

---

## 3. Database Schema Dictionary

The database uses a normalized relational structure consisting of a raw staging table and three core tables: `customers`, `products`, and `transactions`.

### 3.1. `raw_sales_staging`

**Purpose:** Stores imported source records in raw text format before validation and transformation.

| Column                        | PostgreSQL Data Type | Constraints / Description                        |
| ----------------------------- | -------------------- | ------------------------------------------------ |
| `staging_id`                  | BIGINT               | Primary key, generated identity                  |
| `import_batch_id`             | UUID                 | NOT NULL, defaults to `gen_random_uuid()`        |
| `source_row_number`           | INTEGER              | Original source row reference                    |
| `customer_code`               | TEXT                 | Raw customer code / source transaction reference |
| `customer_name`               | TEXT                 | Raw customer name                                |
| `quantity_ordered`            | TEXT                 | Raw quantity                                     |
| `msrp`                        | TEXT                 | Raw MSRP                                         |
| `estimated_cost_price_50_pct` | TEXT                 | Raw estimated cost                               |
| `selling_price`               | TEXT                 | Raw selling price                                |
| `sales`                       | TEXT                 | Raw sales value                                  |
| `profit_per_unit`             | TEXT                 | Raw unit profit or loss                          |
| `total_profit_loss`           | TEXT                 | Raw total profit or loss                         |
| `status`                      | TEXT                 | Raw transaction status                           |
| `order_date`                  | TEXT                 | Raw order date                                   |
| `month`                       | TEXT                 | Source month                                     |
| `year`                        | TEXT                 | Source year                                      |
| `product`                     | TEXT                 | Source product category                          |
| `product_code`                | TEXT                 | Source product code                              |
| `city`                        | TEXT                 | Customer city                                    |
| `country`                     | TEXT                 | Customer country                                 |
| `deal_size`                   | TEXT                 | Source deal size                                 |
| `imported_at`                 | TIMESTAMPTZ          | NOT NULL, defaults to `NOW()`                    |

**Key constraint:**

- `uq_staging_batch_row`: UNIQUE (`import_batch_id`, `source_row_number`).

Raw source fields are stored as TEXT to preserve the imported representation before ETL conversion and validation.

### 3.2. `customers`

**Purpose:** Stores unique customer identities based on customer name and geographic information.

| Column          | PostgreSQL Data Type | Constraints / Description       |
| --------------- | -------------------- | ------------------------------- |
| `customer_id`   | BIGINT               | Primary key, generated identity |
| `customer_name` | TEXT                 | NOT NULL                        |
| `city`          | TEXT                 | NOT NULL                        |
| `country`       | TEXT                 | NOT NULL                        |

**Key constraint:**

- `uq_customer_identity`: UNIQUE (`customer_name`, `city`, `country`).

Customer records are matched using the combination of name, city, and country.

### 3.3. `products`

**Purpose:** Stores the product catalog and product category information.

| Column             | PostgreSQL Data Type | Constraints / Description       |
| ------------------ | -------------------- | ------------------------------- |
| `product_id`       | BIGINT               | Primary key, generated identity |
| `product_code`     | TEXT                 | NOT NULL, UNIQUE                |
| `product_category` | TEXT                 | NOT NULL                        |
| `msrp`             | NUMERIC(12,2)        | NOT NULL, CHECK (`msrp >= 0`)   |

Each product is identified by its unique product code.

### 3.4. `transactions`

**Purpose:** Stores transaction-level sales information and links customers with products.

| Column                    | PostgreSQL Data Type | Constraints / Description                                                         |
| ------------------------- | -------------------- | --------------------------------------------------------------------------------- |
| `transaction_id`          | BIGINT               | Primary key, generated identity                                                   |
| `source_transaction_code` | TEXT                 | NOT NULL, UNIQUE                                                                  |
| `customer_id`             | BIGINT               | NOT NULL, foreign key to `customers.customer_id`                                  |
| `product_id`              | BIGINT               | NOT NULL, foreign key to `products.product_id`                                    |
| `order_date`              | DATE                 | NOT NULL                                                                          |
| `quantity_ordered`        | INTEGER              | NOT NULL, CHECK (`quantity_ordered > 0`)                                          |
| `estimated_cost_per_unit` | NUMERIC(12,2)        | NOT NULL, CHECK (`estimated_cost_per_unit >= 0`)                                  |
| `selling_price`           | NUMERIC(12,2)        | NOT NULL, CHECK (`selling_price > 0`)                                             |
| `sales`                   | NUMERIC(14,2)        | NOT NULL, CHECK (`sales >= 0`)                                                    |
| `profit_per_unit`         | NUMERIC(12,2)        | NOT NULL                                                                          |
| `total_profit_loss`       | NUMERIC(14,2)        | NOT NULL                                                                          |
| `status`                  | TEXT                 | NOT NULL, CHECK (`status IN ('Profit', 'Loss')`)                                  |
| `deal_size`               | TEXT                 | NOT NULL, CHECK (`deal_size IN ('Small', 'Medium', 'Large')`)                     |
| `created_at`              | TIMESTAMPTZ          | Nullable, defaults to `NOW()` for new records; added through a database migration |

**Additional notes:**

- `created_at` is used to track when a transaction is inserted into the database.
- Historical transactions may have NULL `created_at` values because the column was added after the original transaction load.
- An index named `idx_transactions_created_at` supports recent transaction monitoring.

---

## 4. Entity Relationships

The normalized database contains the following relationships:

| Parent Table | Parent Key    | Child Table    | Foreign Key   | Relationship |
| ------------ | ------------- | -------------- | ------------- | ------------ |
| `customers`  | `customer_id` | `transactions` | `customer_id` | One-to-many  |
| `products`   | `product_id`  | `transactions` | `product_id`  | One-to-many  |

Each transaction references one customer and one product.

A customer may have multiple transactions, and a product may appear in multiple transactions.

---

## 5. Business Rules and Data Assumptions

### 5.1. Quantity and Pricing

- Quantity ordered must be a positive whole number.
- Selling price must be greater than zero.
- MSRP must be non-negative.
- Estimated cost per unit must be non-negative.
- Sales must be non-negative.

### 5.2. Financial Calculations

The project uses the following estimated financial calculations:

**Estimated Cost per Unit**

`MSRP × 50%`

**Profit per Unit**

`Selling Price − Estimated Cost per Unit`

**Sales**

`Selling Price × Quantity Ordered`

**Total Profit/Loss**

`Profit per Unit × Quantity Ordered`

Financial calculations are rounded to two decimal places using the project's decimal rounding logic.

The 50% MSRP cost is an analytical assumption. It does not represent independently verified procurement or production cost.

### 5.3. Transaction Classification

**Status:**

- `Profit`: Total profit/loss is greater than or equal to zero.
- `Loss`: Total profit/loss is below zero.

**Deal Size:**

Allowed values are:

- `Small`
- `Medium`
- `Large`

The database enforces the allowed values but does not define quantity-based thresholds for deal size.

### 5.4. Currency Disclaimer

The original dataset does not explicitly specify its currency.

Financial values in the dashboard use USD ($) formatting for presentation purposes only. No currency conversion has been performed, and the source currency has not been independently verified.

---

## 6. ETL Mapping Summary

| Source Data                  | Target Table   | Target Column             |
| ---------------------------- | -------------- | ------------------------- |
| `CUSTOMER_CODE`              | `transactions` | `source_transaction_code` |
| `CUSTOMER_NAME`              | `customers`    | `customer_name`           |
| `CITY`                       | `customers`    | `city`                    |
| `COUNTRY`                    | `customers`    | `country`                 |
| `PRODUCT_CODE`               | `products`     | `product_code`            |
| `PRODUCT`                    | `products`     | `product_category`        |
| `MSRP`                       | `products`     | `msrp`                    |
| `ORDER_DATE`                 | `transactions` | `order_date`              |
| `QUANTITY_ORDERED`           | `transactions` | `quantity_ordered`        |
| `Estimated Cost Price (50%)` | `transactions` | `estimated_cost_per_unit` |
| `Selling price`              | `transactions` | `selling_price`           |
| `SALES`                      | `transactions` | `sales`                   |
| `Profit per unit`            | `transactions` | `profit_per_unit`         |
| `Total profit / loss`        | `transactions` | `total_profit_loss`       |
| `Status`                     | `transactions` | `status`                  |
| `DEALSIZE`                   | `transactions` | `deal_size`               |

The ETL process uses customer name, city, and country to resolve customer references, and product code to resolve product references.

Source date, month, and year values are validated during data quality processing. The normalized transaction table stores the canonical order date as a DATE field.

---

## 7. Data Scope and Limitations

- The original source dataset contains 2,823 transaction records after excluding its summary row.
- Manually entered transactions are stored in the same normalized transaction table.
- Synthetic Faker transactions are generated separately for local testing and are not automatically inserted into the production database.
- Financial values rely on the source dataset and the estimated 50% MSRP cost assumption.
- Dashboard currency formatting does not establish the original source currency.
