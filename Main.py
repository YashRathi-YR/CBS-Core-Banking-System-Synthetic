import subprocess
import sys
from datetime import datetime
import urllib
from sqlalchemy import create_engine, text

# =====================================================
# DATABASE CONNECTION
# =====================================================

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CBS;"
    "Trusted_Connection=yes;"
)


engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


# =====================================================
# FUNCTION TO EXECUTE SQL FILE
# =====================================================

def execute_sql_file(filename):
    print(f"\nExecuting {filename}...")

    start = datetime.now()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            sql = file.read()

        # Split SQL batches using GO
        batches = [batch.strip() for batch in sql.split("GO") if batch.strip()]

        with engine.begin() as conn:
            for batch in batches:
                conn.execute(text(batch))

        duration = (datetime.now() - start).seconds
        print(f"SUCCESS: {filename} executed in {duration}s")

    except Exception as e:
        duration = (datetime.now() - start).seconds
        print(f"FAILED: {filename} after {duration}s")
        print(e)
        sys.exit(1)


# =====================================================
# PYTHON SCRIPTS
# =====================================================

scripts = [
    "Core_banking_transactions.py",
    "Atm_logs.py",
    
]


# =====================================================
# PIPELINE START
# =====================================================

print("=" * 60)
print(f"Pipeline Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# -----------------------------------------------------
# STEP 1 - CREATE TABLES
# -----------------------------------------------------

execute_sql_file("Schema_new.sql")

# -----------------------------------------------------
# STEP 2 - RUN PYTHON FILES
# -----------------------------------------------------

for script in scripts:

    print(f"\nRunning {script}...")

    start = datetime.now()

    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )

    duration = (datetime.now() - start).seconds

    if result.returncode != 0:
        print(f"FAILED: {script} after {duration}s")
        sys.exit(1)

    print(f"SUCCESS: {script} completed in {duration}s")

# -----------------------------------------------------
# STEP 3 - CREATE VIEWS
# -----------------------------------------------------

execute_sql_file("Views_new.sql")

# =====================================================
# PIPELINE COMPLETE
# =====================================================

print("\n" + "=" * 60)
print(f"Pipeline Completed : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Database is ready for Power BI.")
print("=" * 60)