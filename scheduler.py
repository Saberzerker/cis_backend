# import time
# import subprocess
# import sys

# def run_pipeline():
#     subprocess.run([sys.executable, 'pipeline.py'])

# def main():
#     while True:
#         print("\n[*] Scheduler: Triggering pipeline run...")
#         run_pipeline()
#         print("[*] Scheduler: Sleeping for 6 hours (21600 seconds)...\n")
#         time.sleep(21600)  # 6 hours

# if __name__ == "__main__":
#     main()



import time
import subprocess
import sys

INTERVAL_HOURS = 6
INTERVAL_SECONDS = INTERVAL_HOURS * 60 * 60

def main():
    while True:
        print("[*] Scheduler: Triggering pipeline.py ...")
        result = subprocess.run([sys.executable, "pipeline.py"])
        if result.returncode == 0:
            print("[*] Pipeline run completed.")
        else:
            print("[!] Pipeline run failed or had an error.")
        print(f"[*] Sleeping for {INTERVAL_HOURS} hours...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()