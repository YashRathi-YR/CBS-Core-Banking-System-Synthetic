# run_all.py
import subprocess
import sys
from datetime import datetime

scripts = [
    "Atm_logs.py",
    "Core_banking_transactions.py", 
    "Interest_logs.py",
]

print(f"Pipeline started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*50)

for script in scripts:
    print(f"\nRunning {script}...")
    start = datetime.now()
    
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    
    duration = (datetime.now() - start).seconds
    
    if result.returncode != 0:
        print(f"FAILED: {script} after {duration}s. Stopping pipeline.")
        sys.exit(1)
    else:
        print(f"SUCCESS: {script} completed in {duration}s")

print("\n" + "="*50)
print(f"Pipeline completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Database is ready for Power BI.")