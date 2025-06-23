# import subprocess
# import sys

# def run_auto_update():
#     """
#     Runs the auto_update.py script and checks its output for new updates.
#     Returns True if updates occurred (i.e., main pipeline should run), False otherwise.
#     """
#     print("[*] Running auto updater...")
#     # Use capture_output to get output for checking "UPDATED" string
#     result = subprocess.run([sys.executable, 'auto_update.py'], capture_output=True, text=True)
#     print(result.stdout)
#     # Convention: auto_update.py logs "UPDATED" if anything changed
#     if "UPDATED" in result.stdout or "updated" in result.stdout:
#         print("[*] Updates detected. Will run main pipeline.")
#         return True
#     print("[*] No updates detected. Skipping main pipeline.")
#     return False

# def run_main():
#     print("[*] Running main.py pipeline...")
#     subprocess.run([sys.executable, 'main.py'])

# def main():
#     updated = run_auto_update()
#     if updated:
#         run_main()
#     else:
#         print("[*] Pipeline not triggered; no new updates.")

# if __name__ == "__main__":
#     main()


# import subprocess
# import sys
# import os

# def run_autoupdate():
#     """
#     Run the auto_update.py script. Returns True if an update was performed, False otherwise.
#     The auto_update.py script should exit with code 0 if no update, 1 (or any nonzero) if update performed.
#     """
#     print("[*] Running auto_update.py ...")
#     result = subprocess.run([sys.executable, "auto_update.py"])
#     # You can adjust this logic if your auto_update.py signals updates differently
#     return result.returncode != 0

# def run_main_parser():
#     print("[*] Running main.py parsing pipeline ...")
#     result = subprocess.run([sys.executable, "main.py"])
#     return result.returncode

# def main():
#     updated = run_autoupdate()
#     if not updated:
#         print("[*] No new CIS Benchmark updates found. Skipping pipeline.")
#         return
#     print("[*] New update detected! Running parsing/validation pipeline ...")
#     run_main_parser()
#     print("[*] Pipeline completed.")

# if __name__ == "__main__":
#     main()






import subprocess
import sys
import os
import uuid
from db_store import store_benchmark_files
import re


DB_URL = os.getenv("DB_URL", "http://localhost:27017/")  # Update if needed
OUTPUT_JSON = "output/validated/json"
OUTPUT_CSV = "output/validated/csv"

def get_latest_pdf_dir():
    base_dir = os.path.join("data", "input")
    candidates = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
    ]
    if not candidates:
        raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
    latest = max(candidates, key=lambda d: d.split("_")[-1])
    return os.path.join(base_dir, latest)

PDF_DIR = get_latest_pdf_dir()  # Update if needed

def find_os_id_from_filename(filename):
    # Example: CIS_Ubuntu_22.04.pdf -> "1.ubuntu.22.04"
    base = os.path.splitext(filename)[0]
    name = base.replace("CIS_", "").replace(" ", "_").lower()
    return f"1.{name}"

def run_autoupdate():
    print("[*] Running auto_update.py ...")
    result = subprocess.run([sys.executable, "auto_update.py"])
    return result.returncode == 1  

def run_main_parser():
    print("[*] Running main.py parsing pipeline ...")
    result = subprocess.run([sys.executable, "main.py"])
    return result.returncode

def standardize_base_name(filename):
    base = os.path.splitext(filename)[0]
    base = re.sub(r"(\s*PDF)?(\(\d+\))?$", '', base, flags=re.IGNORECASE).strip()
    return base

def store_all_parsed_files():
    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith('.pdf'):
            continue
        pdf_path = os.path.join(PDF_DIR, filename)
        base = standardize_base_name(filename)
        json_path = os.path.join(OUTPUT_JSON, base + ".json")
        csv_path = os.path.join(OUTPUT_CSV, base + ".csv")
        if not (os.path.exists(json_path) and os.path.exists(csv_path)):
            print(f"[!] Skipping {filename}: missing parsed JSON/CSV. Expected JSON: {json_path} CSV: {csv_path}")
            continue
        os_id = find_os_id_from_filename(filename)
        title = base.replace("_", " ")
        benchmark_id = store_benchmark_files(
            title=title,
            pdf_path=pdf_path,
            csv_path=csv_path,
            json_path=json_path,
            os_id=os_id,
            metadata=None
        )
        print(f"[+] Stored benchmark {title} (benchmark_id={benchmark_id}, os_id={os_id})")


def main():
    updated = run_autoupdate()
    if not updated:
        print("[*] No new CIS Benchmark updates found. Skipping pipeline.")
        return
    print("[*] New update detected! Running parsing/validation pipeline ...")
    run_main_parser()
    print("[*] Storing all parsed files in the database ...")
    store_all_parsed_files()
    print("[*] Pipeline completed.")

if __name__ == "__main__":
    main()