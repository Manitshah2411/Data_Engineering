# Enterprise-Style Metadata-Driven Data Warehouse (PostgreSQL + Python)

## 📌 Project Overview

This project demonstrates how **enterprise-grade data warehouses** are built using **metadata-driven, incremental ETL pipelines** instead of naive full reloads.

The focus is not on ingestion tools or streaming, but on **warehouse-side correctness**, including:

* Incremental loading using watermarks
* Safe and controlled UPSERT logic
* Metadata-driven orchestration
* SQL-first transformations with Python orchestration
* Fully re-runnable and idempotent pipelines

This project closely mimics **real production data engineering patterns**.

---

## 📊 Dataset

### Olist Brazilian E-commerce Dataset

Key challenges identified and handled:

* `customer_id` is not a real customer identifier → `customer_unique_id` used instead
* `order_item_id` is not globally unique → composite keys required
* No explicit quantity column → implicit quantity = 1
* Dataset is cleaner than production → complexity added through design

---

## 🏗️ Architecture Overview

```flowchart
Raw CSVs
   ↓
Cleaned CSVs (Pandas)
   ↓
PostgreSQL Warehouse
   ↓
Facts & Aggregates (SQL)
   ↓
Metadata-Controlled Execution
```

**Design philosophy:**

* Python → orchestration, validation, control
* SQL → transformations & aggregations
* PostgreSQL → analytical warehouse

---

## 🧱 Warehouse Schema Design

### Dimensions

* **dim_customers** (grain: one row per customer)
* **dim_orders** (grain: one row per order)
* **dim_products** (grain: one row per product)

### Facts

* **fact_order_items** (grain: one row per order-item)

### Aggregated Facts

* **fact_daily_sales** (grain: one row per day)
* **fact_product_performance** (grain: one row per product)
* **fact_category_performance** (grain: one row per category)
* **fact_customer_lifecycle** (grain: one row per customer)

All tables include:

* Proper primary & foreign keys
* NOT NULL constraints
* Numeric precision
* Enterprise-style schema separation

---

## 🔁 Incremental Loading Strategy

Incremental logic is implemented using **watermarks** stored in metadata tables.

Each pipeline:

1. Reads the last successful watermark
2. Processes only new data
3. Writes results safely (INSERT / UPSERT)
4. Stores a new watermark upon success
5. Is fully re-runnable and idempotent

### Incremental Strategy by Table

| Table            | Strategy                                  |
| ---------------- | ----------------------------------------- |
| dim_customers    | UPSERT                                    |
| dim_orders       | Incremental UPSERT (mutable columns only) |
| dim_products     | UPSERT                                    |
| fact_order_items | Insert-only                               |
| Aggregates       | Incremental recompute / UPSERT            |

---

## 🧠 Metadata System (Control Plane)

### meta.config

Stores static pipeline configuration:

* pipeline name
* target table
* load type
* watermark column
* truncation rules

### meta.etl_runs

Tracks every execution:

* run status (IN_PROGRESS / SUCCESS / FAILED)
* start & end time
* rows processed
* watermark used

Features:

* One active run enforced per pipeline
* Full execution history retained
* Restart safety guaranteed

ETL scripts **never query metadata tables directly** — all access goes through a Python metadata layer.

---

## 🧪 Data Validation

Validation is implemented explicitly using Python assertions:

* Primary key uniqueness
* Composite key checks
* Foreign key integrity
* Non-negative metrics
* Allowed NULL handling

This mirrors production data quality thinking (similar to Great Expectations).

---

## 🧰 Tech Stack

* Python
* PostgreSQL
* SQLAlchemy
* Pandas

---

## ▶️ How to Run

1. Create PostgreSQL database
2. Create schemas: `warehouse`, `meta`
3. Create warehouse tables
4. Insert pipeline configs into `meta.config`
5. Run pipelines using:

```bash
python -m etl.<pipeline_name>
```

---

## 🚫 What This Project Does NOT Cover

This project intentionally excludes:

* Streaming ingestion
* Kafka
* Airflow scheduling
* Real-time pipelines

These will be implemented in **my next advanced data engineering project**.

---

## 🎯 Key Takeaway

This project focuses on **correct warehouse design, incremental processing, and metadata-driven control**, which are core expectations for real-world data engineering roles.

---

## 👤 Author

### Manit Shah

Data Engineer | Python | SQL | PostgreSQL
