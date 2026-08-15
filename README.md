# 🏦 Banking Analytics System (SQL + Python + Power BI)

## 📌 Project Overview

In real-world banking environments, data privacy restrictions limit the use of production data for analytics and learning.

To work around this, I built a **simulated core banking system** — a Python-generated dataset of 100K+ transactions and 30K+ ATM logs, backed by a SQL Server database with proper relational integrity, and visualized through an interactive Power BI dashboard.

This project demonstrates **end-to-end data engineering and analytics**: schema design, incremental data loading, SQL view creation, and dashboard building with DAX.

---

## 🏗️ Architecture

```

Main.py (single entry point)
├── Schema\_new.sql        → creates database + tables
├── Core\_banking\_transactions.py  → generates & inserts CBT data
├── Atm\_logs.py            → derives ATM logs from CBT
└── Views\_new.sql          → creates reporting views
↓
Power BI Dashboard

````

---

## 🗄️ Database Design

The system uses **two related tables**, intentionally kept minimal so every piece of data serves a purpose:

| Table | Purpose | Row Count |
|---|---|---|
| `core_banking_transactions` | Central transaction record across all channels (Online, ATM, Branch) | 100K+ |
| `atm_logs` | Machine-level ATM log data, generated from CBT's ATM transactions | 30K+ |

**Relationship:** `atm_logs.tnx_id` is a foreign key referencing `core_banking_transactions.tnx_id`. Every ATM log entry corresponds to exactly one verified bank transaction — status, timestamp, and ATM assignment are consistent across both tables.

Branch-level reporting uses `branch_id` from `core_banking_transactions` directly, the same way ATM locations are mapped from `atm_id` — each ID maps to a fixed branch, so branch performance can be aggregated consistently.

---

## ⚙️ Data Generation & Pipeline

- Built with **Python (Pandas, NumPy, SQLAlchemy)**
- `core_banking_transactions` generates first — 100K rows with:
  - Realistic peak-hour distribution (evening-heavy load)
  - Channel split: Online 40%, ATM 35%, Branch 25%
  - ~5% simulated failure rate
- `atm_logs` reads ATM-channel rows directly from `core_banking_transactions` and builds machine-level logs from them — response time, location, and status are derived from the linked transaction, not generated independently
- **Incremental loading**: each script reads `MAX(tnx_id)` before inserting, so re-running the pipeline appends new data instead of failing on duplicate keys or wiping existing records
- `Main.py` orchestrates the full pipeline in the correct dependency order (CBT → ATM logs)

---

## 📊 SQL Layer

Three SQL views back the Power BI model:

- `vw_transaction_failure_rate` — uses a window function (`SUM() OVER()`) to calculate failure percentage
- `vw_atm_performance` — average response time and failure count grouped by ATM and location
- `vw_top_accounts` — top 10 accounts by total transaction value

Raw tables (`core_banking_transactions`, `atm_logs`) are also imported directly into Power BI so DAX can handle dynamic aggregations and cross-filtering that static views can't provide.

---

## 📈 Dashboard (Power BI)

**Core Banking Transaction Overview**

- KPI cards: Total Transactions, Total Amount, Success Rate, Avg Transaction Amount
- Transactions by Channel (bar chart)
- Hourly Transaction Trend (line chart, shows peak-hour load)
- Transaction Status Breakdown (donut: Success vs Failed)
- Top Branches by Transaction Volume
- Daily Transaction Trend
- Summary strip: Peak Hour, Highest Channel, Failed Transactions, Total Branches

Built using a mix of native Power BI aggregation (drag-and-drop on raw columns) and a small set of DAX measures — used only where a ratio or average couldn't be derived from a raw column directly.

---

## 🔍 Key Insights

- Evening hours show the clearest transaction spike, consistent with the simulated peak-hour distribution
- Online is the highest-volume channel, followed by ATM and Branch
- Overall transaction failure rate holds steady around ~5%, matching the generated distribution
- ATM response times increase noticeably for failed transactions compared to successful ones
- Transaction volume varies meaningfully across branches, visible in the top-branches breakdown

---

## 🛠️ Tools & Technologies

- **SQL Server** — schema design, primary/foreign keys, views, window functions
- **Python** — Pandas, NumPy, SQLAlchemy for data generation and incremental loading
- **Power BI** — data modeling, relationships, DAX measures, dashboard design

---

## 🚀 How to Run

```bash
python Main.py
````

That's it — `Main.py` orchestrates the entire pipeline in the correct order:

1. Executes `Schema_new.sql` to create the database and tables (connects via `master` first, so this works even on a completely fresh SQL Server instance where `CBS` doesn't exist yet)
2. Runs `Core_banking_transactions.py`, then `Atm_logs.py` (in that dependency order)
3. Executes `Views_new.sql` to create the reporting views

Once it completes, the database is ready — open the Power BI file and refresh the data connection.

Re-running `Main.py` is safe. Table creation is guarded (`IF OBJECT_ID ... IS NULL`), and the Python scripts use incremental loading (`MAX(id) + 1`), so nothing gets duplicated or wiped on a second run.

---

## 💡 Key Learnings

- Designing relational schemas with proper primary/foreign key constraints, and understanding why a primary key choice can break at scale (learned this directly from a duplicate-key production error)
- Building genuinely correlated datasets — deriving one table from another (`atm_logs` from `core_banking_transactions`) instead of generating disconnected data that merely shares a key range
- Implementing incremental data loading (`MAX(id) + 1`) instead of relying on destructive truncate-and-reload patterns
- Making the pipeline resilient to a fresh environment — connecting to `master` for database creation instead of assuming the target database already exists
- Knowing when DAX is necessary versus when native Power BI aggregation on raw columns is sufficient

---

## 📬 Connect With Me

- LinkedIn: https://www.linkedin.com/in/yash-rathi-024b30235/