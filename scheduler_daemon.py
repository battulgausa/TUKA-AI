import time
from tools.scheduler import run_due

print("Scheduler daemon started... (runs every 60s)")

while True:
    try:
        out = run_due()
        print("run_due:", out)
    except Exception as e:
        print("error:", e)

    time.sleep(60)