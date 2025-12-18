from datetime import date
from merkle import compute_daily_root

today = date.today().isoformat()
root = compute_daily_root(today)

if root:
    print("Merkle root generated:", root)
else:
    print("No evidence today")
