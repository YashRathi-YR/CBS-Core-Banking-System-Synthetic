import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import urllib

# =============================
# CONNECT TO SQL SERVER (CBS)
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
# CONFIG
# =============================
num_rows = 50000
start_date = datetime(2026, 3, 1)

# =============================
# DEFINE ATM MASTER DATA
# Each ATM has a FIXED location — this is the key fix
# =============================
atm_master = {
    200: "Mumbai - Andheri",
    201: "Mumbai - Andheri",
    202: "Mumbai - Andheri",
    203: "Mumbai - Andheri",
    204: "Mumbai - Parel",
    205: "Mumbai - Parel",
    206: "Mumbai - Parel",
    207: "Mumbai - Parel",
    208: "Mumbai - Parel",
    209: "Mumbai - Andheri",
    210: "Mumbai - Bandra",
    211: "Mumbai - Bandra",
    212: "Mumbai - Bandra",
    213: "Mumbai - Bandra",
    214: "Mumbai - Churchgate",
    215: "Mumbai - Churchgate",
    216: "Mumbai - Churchgate",
    217: "Mumbai - Churchgate",
    218: "Mumbai - Bandra",
    219: "Mumbai - Bandra",
    220: "Mumbai - Dadar",
    221: "Mumbai - Dadar",
    222: "Mumbai - Dadar",
    223: "Mumbai - Matunga",
    224: "Mumbai - Matunga",
    225: "Mumbai - Matunga",
    226: "Mumbai - Matunga",
    227: "Mumbai - Churchgate",
    228: "Mumbai - Matunga",
    229: "Mumbai - Parel",
}

atm_ids   = list(atm_master.keys())
atm_locs  = [atm_master[a] for a in atm_ids]

# =============================
# GENERATE TIMESTAMPS
# =============================
timestamps = []
for _ in range(num_rows):
    random_day = start_date + timedelta(days=random.randint(0, 29))
    hour = random.choice([3, 7, 10, 11, 12, 18, 19, 20, 21, 23])
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    timestamps.append(datetime(
        random_day.year, random_day.month, random_day.day,
        hour, minute, second
    ))

# =============================
# GENERATE ATM LOG DATA
# Each row picks a random ATM — location comes from master
# =============================
chosen_atm_ids = np.random.choice(atm_ids, num_rows)
chosen_locations = [atm_master[a] for a in chosen_atm_ids]

atm_df = pd.DataFrame({
    "atm_id":            chosen_atm_ids,      # which ATM (200-229)
    "location":          chosen_locations,     # fixed per ATM
    "withdrawal_amount": np.random.randint(1000, 20000, num_rows),
    "tnx_status":        np.random.choice(
                             ["SUCCESS", "FAILED"],
                             num_rows,
                             p=[0.96, 0.04]
                         ),
    "response_time_ms":  np.random.randint(500, 2000, num_rows),
    "timestamp":         timestamps
    # NO log_id column here — SQL Server generates it
})

# Failed transactions take longer — realistic detail
atm_df.loc[atm_df["tnx_status"] == "FAILED", "response_time_ms"] *= 3

print("ATM Logs Generated:", len(atm_df))

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
print("ATM logs inserted successfully")