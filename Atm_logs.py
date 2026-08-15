import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import urllib

# =============================
# CONNECT TO SQL SERVER
# =============================
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CBS;"
    "Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
print("Connected to CBS")

# =============================
# READ ATM TRANSACTIONS FROM CBT
# This is the key change — we don't generate
# row count independently anymore.
# We read exactly what CBT recorded.
# =============================
query = """
    SELECT 
        tnx_id,
        atm_id,
        tnx_status,
        tnx_timestamp
    FROM dbo.core_banking_transactions
    WHERE channel = 'ATM'
    AND atm_id IS NOT NULL
"""

cbt_atm_df = pd.read_sql(query, engine)
print(f"ATM transactions read from CBT : {len(cbt_atm_df)}")
print(f"tnx_id range                   : {cbt_atm_df['tnx_id'].min()} → {cbt_atm_df['tnx_id'].max()}")

# =============================
# ATM MASTER — fixed location per atm_id
# Same master as before
# =============================
atm_master = {
    200: "Mumbai - Andheri", 201: "Mumbai - Andheri",
    202: "Mumbai - Andheri", 203: "Mumbai - Andheri",
    204: "Mumbai - Andheri", 205: "Mumbai - Andheri",
    206: "Mumbai - Andheri", 207: "Mumbai - Andheri",
    208: "Mumbai - Andheri", 209: "Mumbai - Andheri",
    210: "Mumbai - Bandra",  211: "Mumbai - Bandra",
    212: "Mumbai - Bandra",  213: "Mumbai - Bandra",
    214: "Mumbai - Bandra",  215: "Mumbai - Bandra",
    216: "Mumbai - Bandra",  217: "Mumbai - Bandra",
    218: "Mumbai - Bandra",  219: "Mumbai - Bandra",
    220: "Mumbai - Dadar",   221: "Mumbai - Dadar",
    222: "Mumbai - Dadar",   223: "Mumbai - Dadar",
    224: "Mumbai - Dadar",   225: "Mumbai - Dadar",
    226: "Mumbai - Dadar",   227: "Mumbai - Dadar",
    228: "Mumbai - Dadar",   229: "Mumbai - Dadar",
}

# =============================
# BUILD ATM LOGS FROM CBT DATA
# Each row in atm_logs now corresponds
# to a real row in core_banking_transactions
# =============================

# Map location from atm_master using atm_id from CBT
locations = cbt_atm_df["atm_id"].map(atm_master)

# Generate response times based on tnx_status from CBT
# If CBT says FAILED, ATM also shows higher response time
# This is realistic — failed transactions timeout slower
response_times = np.where(
    cbt_atm_df["tnx_status"] == "SUCCESS",
    np.random.randint(500, 2000, len(cbt_atm_df)),   # normal for success
    np.random.randint(4000, 8000, len(cbt_atm_df))   # slow for failure
)

# Withdrawal amount — only for ATM withdrawals
# In CBT, tnx_type could be TRANSFER or WITHDRAWAL via ATM
withdrawal_amounts = np.random.randint(1000, 20000, len(cbt_atm_df))

atm_df = pd.DataFrame({
    "tnx_id":           cbt_atm_df["tnx_id"].values,      # direct link to CBT
    "atm_id":           cbt_atm_df["atm_id"].values,       # same atm_id as CBT
    "location":         locations.values,                   # derived from master
    "withdrawal_amount": withdrawal_amounts,
    "tnx_status":       cbt_atm_df["tnx_status"].values,   # matches CBT status
    "response_time_ms": response_times,
    "timestamp":        cbt_atm_df["tnx_timestamp"].values  # same timestamp as CBT
})

print(f"\nATM Logs built from CBT data")
print(f"Total rows                     : {len(atm_df)}")
print(f"\nStatus distribution:")
print(atm_df["tnx_status"].value_counts())
print(f"\nLocation distribution:")
print(atm_df["location"].value_counts())

# =============================
# INSERT INTO SQL SERVER
# =============================
atm_df.to_sql(
    "atm_logs",
    con=engine,
    schema="dbo",
    if_exists="append",
    index=False,
    chunksize=5000
)

print(f"\nATM logs inserted successfully : {len(atm_df)} rows")