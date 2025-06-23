# # import psycopg2
# # import uuid
# # import os
# # import re
# # import pymonogo

# # # --- CONFIGURABLE PATHS ---
# # DB_URL = os.getenv("DB_URL", "http://localhost:27017/")
# # OUTPUT_JSON = "output/validated/json"   # Use your actual JSON output directory
# # OUTPUT_CSV = "output/validated/csv"     # Use your actual CSV output directory

# # def get_latest_pdf_dir():
# #     """
# #     Returns the absolute path to the latest "PDF_VERSION_YYYY-MM-DD" directory in data/input.
# #     """
# #     base_dir = os.path.join("data", "input")
# #     candidates = [
# #         d for d in os.listdir(base_dir)
# #         if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
# #     ]
# #     if not candidates:
# #         raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
# #     latest = max(candidates, key=lambda d: d.split("_")[-1])
# #     return os.path.join(base_dir, latest)

# # PDF_DIR = get_latest_pdf_dir()

# # def standardize_base_name(filename):
# #     """
# #     Standardizes the base name for matching PDF/JSON/CSV files.
# #     This function should match the logic used by your parser for naming outputs.
# #     """
# #     base = os.path.splitext(filename)[0]
# #     # Remove duplicated/extra extensions or trailing ' PDF'
# #     base = re.sub(r"(\s*PDF)?(\(\d+\))?$", '', base, flags=re.IGNORECASE).strip()
# #     return base

# # def find_os_id_from_filename(filename):
# #     # Example: CIS_Ubuntu_22.04.pdf -> "1.ubuntu.22.04"
# #     base = os.path.splitext(filename)[0]
# #     name = base.replace("CIS_", "").replace(" ", "_").lower()
# #     return f"1.{name}"

# # def store_benchmark_files(
# #     db_url,
# #     title,
# #     pdf_path,
# #     csv_path,
# #     json_path,
# #     os_id,
# #     metadata=None
# # ):
# #     """
# #     Store a benchmark with files into the database.
# #     The benchmark_id is auto-generated (UUID).
# #     """
# #     benchmark_id = str(uuid.uuid4())

# #     with open(pdf_path, "rb") as f:
# #         pdf_data = f.read()
# #     with open(csv_path, "rb") as f:
# #         csv_data = f.read()
# #     with open(json_path, "rb") as f:
# #         json_data = f.read()

# #     conn = psycopg2.connect(db_url)
# #     try:
# #         with conn.cursor() as cur:
# #             cur.execute("""
# #                 INSERT INTO benchmarks (
# #                     benchmark_id, title, date_updated, pdf_file, csv_file, json_file, metadata, os_id
# #                 )
# #                 VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
# #                 ON CONFLICT (benchmark_id) DO UPDATE
# #                 SET title = EXCLUDED.title,
# #                     date_updated = NOW(),
# #                     pdf_file = EXCLUDED.pdf_file,
# #                     csv_file = EXCLUDED.csv_file,
# #                     json_file = EXCLUDED.json_file,
# #                     metadata = EXCLUDED.metadata,
# #                     os_id = EXCLUDED.os_id
# #             """, (
# #                 benchmark_id, title, psycopg2.Binary(pdf_data), psycopg2.Binary(csv_data),
# #                 psycopg2.Binary(json_data), metadata, os_id
# #             ))
# #         conn.commit()
# #     finally:
# #         conn.close()
# #     return benchmark_id

# # def store_report_file(
# #     db_url,
# #     save_id,
# #     device_id,
# #     user_id,
# #     report_bytes,
# #     metadata=None
# # ):
# #     """
# #     Store a generated report into the reports table.
# #     """
# #     report_id = str(uuid.uuid4())
# #     conn = psycopg2.connect(db_url)
# #     try:
# #         with conn.cursor() as cur:
# #             cur.execute("""
# #                 INSERT INTO reports (
# #                     report_id, save_id, device_id, user_id, generated_at, file, metadata
# #                 )
# #                 VALUES (%s, %s, %s, %s, NOW(), %s, %s)
# #             """, (
# #                 report_id, save_id, device_id, user_id, psycopg2.Binary(report_bytes), metadata
# #             ))
# #         conn.commit()
# #     finally:
# #         conn.close()
# #     return report_id

# # def store_all_parsed_files():
# #     for filename in os.listdir(PDF_DIR):
# #         if not filename.lower().endswith('.pdf'):
# #             continue
# #         pdf_path = os.path.join(PDF_DIR, filename)
# #         # Standardize base name to match parser output
# #         base = standardize_base_name(filename)
# #         json_path = os.path.join(OUTPUT_JSON, base + ".json")
# #         csv_path = os.path.join(OUTPUT_CSV, base + ".csv")
# #         if not (os.path.exists(json_path) and os.path.exists(csv_path)):
# #             print(f"[!] Skipping {filename}: missing parsed JSON/CSV. Expected JSON: {json_path} CSV: {csv_path}")
# #             continue
# #         os_id = find_os_id_from_filename(filename)
# #         title = base.replace("_", " ")
# #         benchmark_id = store_benchmark_files(
# #             db_url=DB_URL,
# #             title=title,
# #             pdf_path=pdf_path,
# #             csv_path=csv_path,
# #             json_path=json_path,
# #             os_id=os_id,
# #             metadata=None
# #         )
# #         print(f"[+] Stored benchmark {title} (benchmark_id={benchmark_id}, os_id={os_id})")

# # def main():
# #     print("[*] Storing all parsed files in the database ...")
# #     store_all_parsed_files()

# # if __name__ == "__main__":
# #     main()




# import os
# import uuid
# import re
# from pymongo import MongoClient
# from bson.binary import Binary
# import datetime

# # --- CONFIGURABLE PATHS ---
# DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017/")
# DB_NAME = os.getenv("DB_NAME", "cis_db")
# BENCHMARKS_COLLECTION = "benchmarks"
# REPORTS_COLLECTION = "reports"
# OUTPUT_JSON = "output/validated/json"
# OUTPUT_CSV = "output/validated/csv"

# def get_latest_pdf_dir():
#     base_dir = os.path.join("data", "input")
#     candidates = [
#         d for d in os.listdir(base_dir)
#         if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
#     ]
#     if not candidates:
#         raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
#     latest = max(candidates, key=lambda d: d.split("_")[-1])
#     return os.path.join(base_dir, latest)

# PDF_DIR = get_latest_pdf_dir()

# def standardize_base_name(filename):
#     base = os.path.splitext(filename)[0]
#     base = re.sub(r"(\s*PDF)?(\(\d+\))?$", '', base, flags=re.IGNORECASE).strip()
#     return base

# def find_os_id_from_filename(filename):
#     base = os.path.splitext(filename)[0]
#     name = base.replace("CIS_", "").replace(" ", "_").lower()
#     return f"1.{name}"

# def get_mongo_collections():
#     client = MongoClient(DB_URL)
#     db = client[DB_NAME]
#     return db[BENCHMARKS_COLLECTION], db[REPORTS_COLLECTION]

# def store_benchmark_files(
#     title,
#     pdf_path,
#     csv_path,
#     json_path,
#     os_id,
#     metadata=None
# ):
#     benchmark_id = str(uuid.uuid4())
#     with open(pdf_path, "rb") as f:
#         pdf_data = Binary(f.read())
#     with open(csv_path, "rb") as f:
#         csv_data = Binary(f.read())
#     with open(json_path, "rb") as f:
#         json_data = Binary(f.read())

#     benchmarks_col, _ = get_mongo_collections()
#     doc = {
#         "benchmark_id": benchmark_id,
#         "title": title,
#         "date_updated": datetime.datetime.utcnow(),
#         "pdf_file": pdf_data,
#         "csv_file": csv_data,
#         "json_file": json_data,
#         "metadata": metadata,
#         "os_id": os_id
#     }
#     benchmarks_col.update_one(
#         {"benchmark_id": benchmark_id},
#         {"$set": doc},
#         upsert=True
#     )
#     return benchmark_id

# def store_report_file(
#     save_id,
#     device_id,
#     user_id,
#     report_bytes,
#     metadata=None
# ):
#     report_id = str(uuid.uuid4())
#     _, reports_col = get_mongo_collections()
#     doc = {
#         "report_id": report_id,
#         "save_id": save_id,
#         "device_id": device_id,
#         "user_id": user_id,
#         "generated_at": datetime.datetime.utcnow(),
#         "file": Binary(report_bytes),
#         "metadata": metadata
#     }
#     reports_col.insert_one(doc)
#     return report_id

# def store_all_parsed_files():
#     for filename in os.listdir(PDF_DIR):
#         if not filename.lower().endswith('.pdf'):
#             continue
#         pdf_path = os.path.join(PDF_DIR, filename)
#         base = standardize_base_name(filename)
#         json_path = os.path.join(OUTPUT_JSON, base + ".json")
#         csv_path = os.path.join(OUTPUT_CSV, base + ".csv")
#         if not (os.path.exists(json_path) and os.path.exists(csv_path)):
#             print(f"[!] Skipping {filename}: missing parsed JSON/CSV. Expected JSON: {json_path} CSV: {csv_path}")
#             continue
#         os_id = find_os_id_from_filename(filename)
#         title = base.replace("_", " ")
#         benchmark_id = store_benchmark_files(
#             title=title,
#             pdf_path=pdf_path,
#             csv_path=csv_path,
#             json_path=json_path,
#             os_id=os_id,
#             metadata=None
#         )
#         print(f"[+] Stored benchmark {title} (benchmark_id={benchmark_id}, os_id={os_id})")

# def main():
#     print("[*] Storing all parsed files in the MongoDB database ...")
#     store_all_parsed_files()

# if __name__ == "__main__":
#     main()

import os
import uuid
import re
import datetime
from pymongo import MongoClient
from gridfs import GridFS

# --- CONFIGURABLE PATHS ---
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cis_db")
BENCHMARKS_COLLECTION = "benchmarks"
REPORTS_COLLECTION = "reports"
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

PDF_DIR = get_latest_pdf_dir()

def standardize_base_name(filename):
    base = os.path.splitext(filename)[0]
    base = re.sub(r"(\s*PDF)?(\(\d+\))?$", '', base, flags=re.IGNORECASE).strip()
    return base

def find_os_id_from_filename(filename):
    base = os.path.splitext(filename)[0]
    name = base.replace("CIS_", "").replace(" ", "_").lower()
    return f"1.{name}"

def get_mongo_resources():
    client = MongoClient(DB_URL)
    db = client[DB_NAME]
    fs = GridFS(db)
    return db, fs

def store_file_gridfs(fs, file_path):
    with open(file_path, "rb") as f:
        file_id = fs.put(f, filename=os.path.basename(file_path))
    return file_id

def store_benchmark_files(
    title,
    pdf_path,
    csv_path,
    json_path,
    os_id,
    metadata=None
):
    benchmark_id = str(uuid.uuid4())
    db, fs = get_mongo_resources()

    pdf_id = store_file_gridfs(fs, pdf_path)
    csv_id = store_file_gridfs(fs, csv_path)
    json_id = store_file_gridfs(fs, json_path)

    doc = {
        "benchmark_id": benchmark_id,
        "title": title,
        "date_updated": datetime.datetime.utcnow(),
        "pdf_file_id": pdf_id,
        "csv_file_id": csv_id,
        "json_file_id": json_id,
        "metadata": metadata,
        "os_id": os_id
    }
    db[BENCHMARKS_COLLECTION].update_one(
        {"benchmark_id": benchmark_id},
        {"$set": doc},
        upsert=True
    )
    return benchmark_id

def store_report_file(
    save_id,
    device_id,
    user_id,
    report_bytes,
    metadata=None
):
    report_id = str(uuid.uuid4())
    db, fs = get_mongo_resources()
    report_file_id = fs.put(report_bytes, filename=f"{report_id}.pdf")
    doc = {
        "report_id": report_id,
        "save_id": save_id,
        "device_id": device_id,
        "user_id": user_id,
        "generated_at": datetime.datetime.utcnow(),
        "file_id": report_file_id,
        "metadata": metadata
    }
    db[REPORTS_COLLECTION].insert_one(doc)
    return report_id

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
    print("[*] Storing all parsed files in the MongoDB database (GridFS for large files) ...")
    store_all_parsed_files()

if __name__ == "__main__":
    main()