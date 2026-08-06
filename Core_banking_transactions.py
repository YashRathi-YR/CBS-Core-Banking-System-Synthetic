import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text   # text imported at top
import urllib

# =============================
# CONFIGURATION
# =============================
num_rows = 100000
start_date = datetime(2026, 7, 1)

# =============================
# CONNECT FIRST — everything depends on this
# =============================
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CBS;"
    "Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
print("Connected to CBS database successfully")

# =============================
# GET STARTING TNX_ID
# engine exists now, so this works
# =============================
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT ISNULL(MAX(tnx_id), 0) FROM dbo.core_banking_transactions"
    ))
    max_id = result.scalar()

start_id = max_id + 1
print(f"Max existing tnx_id  : {max_id}")
print(f"Starting insert from : {start_id}")

# =============================
# GENERATE TIMESTAMPS
# =============================
timestamps = []
for _ in range(num_rows):
    random_day = start_date + timedelta(days=random.randint(0, 29))
    hour = np.random.choice(
        [3,7,10, 11, 12, 18, 19, 20, 21, 23],
        p=[0.01,0.15,0.08, 0.08, 0.08, 0.18, 0.20, 0.20, 0.10, 0.08]
    )
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    timestamps.append(datetime(
        random_day.year, random_day.month, random_day.day,
        hour, minute, second
    ))

# =============================
# CREATE DATAFRAME
# start_id is now correctly set
# =============================
df = pd.DataFrame({
    "tnx_id":        range(start_id, start_id + num_rows),
    "account_id":    np.random.randint(1000, 5000, num_rows),
    "branch_id":     np.random.randint(101, 120, num_rows),
    "tnx_type":      np.random.choice(
                         ["DEPOSIT", "WITHDRAWAL", "TRANSFER"],
                         num_rows, p=[0.3, 0.4, 0.3]
                     ),
    "channel":       np.random.choice(
                         ["BRANCH", "ATM", "ONLINE"],
                         num_rows, p=[0.25, 0.35, 0.40]
                     ),
    "amount":        np.random.randint(1000, 200000, num_rows),
    "tnx_status":    np.random.choice(
                         ["SUCCESS", "FAILED"],
                         num_rows, p=[0.95, 0.05]
                     ),
    "tnx_timestamp": timestamps
})

print(f"Data Generated Successfully")
print(f"Rows in dataframe    : {len(df)}")
print(f"tnx_id range         : {df['tnx_id'].min()} → {df['tnx_id'].max()}")

# =============================
# ASSIGN ATM_ID
# =============================
atm_ids = list(range(200, 230))
df["atm_id"] = None
atm_mask = df["channel"] == "ATM"
df.loc[atm_mask, "atm_id"] = np.random.choice(
    atm_ids, size=atm_mask.sum()
)

print(f"\nATM ID Assignment:")
print(f"ATM transactions     : {atm_mask.sum()}")
print(f"atm_id assigned      : {df['atm_id'].notna().sum()}")
print(f"atm_id NULL          : {df['atm_id'].isna().sum()}")

# =============================
# VALIDATE DISTRIBUTIONS
# =============================
print("\nFailure Rate (%):")
print(df["tnx_status"].value_counts(normalize=True).mul(100).round(2))

print("\nChannel Distribution (%):")
print(df["channel"].value_counts(normalize=True).mul(100).round(2))

print("\nPeak Hour Distribution:")
print(df["tnx_timestamp"].dt.hour.value_counts().sort_index())

# =============================
# INSERT INTO SQL SERVER
# =============================
df.to_sql(
    "core_banking_transactions",
    con=engine,
    schema="dbo",
    if_exists="append",
    index=False,
    chunksize=10000
)

print(f"\nInserted {len(df)} rows successfully")
print(f"tnx_id range in DB   : {start_id} → {start_id + num_rows - 1}")