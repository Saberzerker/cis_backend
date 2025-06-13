import os
import json
import csv
from config import (INPUT_DIR, OUTPUT_TEXT, OUTPUT_JSON, OUTPUT_CSV, LOG_FILE, SECTION_HEADERS)
from utils import setup_logging, log, extract_text, clean_text
from parser import parse_text
from llm_validation import validate_parsed_data

def export_json(data, json_path):
    with open(json_path, 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, separators=(',', ':'))
    log(f"[+] JSON File Exported: (json_path)")
    

def export_csv(data, csv_path):
    if not data:
        log("[!] No data to write to CSV.")
        return

    keys = data[0].keys()
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = "; ".join([json.dumps(i) if isinstance(i, dict) else str(i) for i in v])
            writer.writerow(row)

    log(f"[+] CSV exported: {csv_path}")

def process_pdf(pdf_path, base_name):
    txt_path = os.path.join(OUTPUT_TEXT, base_name + ".txt")
    json_path = os.path.join(OUTPUT_JSON, base_name + ".json")
    csv_path = os.path.join(OUTPUT_CSV, base_name + ".csv")  # Changed from .xlsx to .csv

    extract_text(pdf_path, txt_path)
    clean_text(txt_path)
    parsed = parse_text(txt_path, SECTION_HEADERS)
    validate_parsed_data(parsed)
    export_json(parsed, json_path)
    export_csv(parsed, csv_path)

def main():
    setup_logging(LOG_FILE)
    log("[*] Starting CIS PDF parsing pipeline...")
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            base = os.path.splitext(filename)[0]
            try:
                process_pdf(pdf_path, base)
                log(f"[+] Finished processing: {filename}")
            except Exception as e:
                log(f"[ERROR] Failed processing {filename}: {e}", "error")
    log("[*] All PDFs processed.")

if __name__ == "__main__":
    main()