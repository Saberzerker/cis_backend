import os
import json
import csv
import re
from config import (
    INPUT_DIR, OUTPUT_TEXT, OUTPUT_JSON, OUTPUT_CSV, LOG_FILE, SECTION_HEADERS,
    OUTPUT_VALIDATION, PDF_ACCURATE, PDF_DISCREPANCY, LOG_DIR
)
from utils import setup_logging, log, extract_text, clean_text, ensure_directories
from parser import parse_text
from llm_validation import llm_cross_validate

def export_json(data, json_path):
    with open(json_path, 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, separators=(',', ':'))
    log(f"[+] JSON File Exported: {json_path}")

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

def save_validation_report(base_name, report):
    validation_path = os.path.join(OUTPUT_VALIDATION, f"{base_name}_validation.json")
    with open(validation_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    log(f"[+] Validation report exported: {validation_path}")

def process_pdf(pdf_path, base_name):
    txt_path = os.path.join(OUTPUT_TEXT, base_name + ".txt")
    json_path = os.path.join(OUTPUT_JSON, base_name + ".json")
    csv_path = os.path.join(OUTPUT_CSV, base_name + ".csv")

    extract_text(pdf_path, txt_path)
    clean_text(txt_path)
    parsed = parse_text(txt_path, SECTION_HEADERS)
    export_json(parsed, json_path)
    export_csv(parsed, csv_path)

    validation_result = llm_cross_validate(parsed, txt_path)
    save_validation_report(base_name, validation_result)

    # Route based on validation
    if validation_result["status"] == "ok":
        os.makedirs(PDF_ACCURATE, exist_ok=True)
        target = os.path.join(PDF_ACCURATE, os.path.basename(pdf_path))
        os.replace(pdf_path, target)
        log(f"[+] PDF moved to accurate: {target}")
    else:
        os.makedirs(PDF_DISCREPANCY, exist_ok=True)
        target = os.path.join(PDF_DISCREPANCY, os.path.basename(pdf_path))
        os.replace(pdf_path, target)
        log(f"[!] PDF moved to discrepancy: {target}")

def get_latest_pdf_dir():
    """
    Returns the path to the latest 'PDF_VERSION_YYYY-MM-DD' directory in data/input.
    """
    base_dir = os.path.join("data", "input")
    candidates = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
    ]
    if not candidates:
        raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
    # Sort by the date in the directory name
    latest = max(candidates, key=lambda d: d.split("_")[-1])
    return os.path.join(base_dir, latest)

def main():
    ensure_directories([
        INPUT_DIR, OUTPUT_TEXT, OUTPUT_JSON, OUTPUT_CSV, OUTPUT_VALIDATION,
        PDF_ACCURATE, PDF_DISCREPANCY, LOG_DIR
    ])
    setup_logging(LOG_FILE)
    log("[*] Starting CIS PDF parsing pipeline...")

    # Use the latest versioned PDF input directory
    pdf_dir = get_latest_pdf_dir()
    log(f"[*] Using PDF input directory: {pdf_dir}")

    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            base = os.path.splitext(filename)[0]
            try:
                process_pdf(pdf_path, base)
                log(f"[+] Finished processing: {filename}")
            except Exception as e:
                log(f"[ERROR] Failed processing {filename}: {e}", "error")
    log("[*] All PDFs processed.")

if __name__ == "__main__":
    main()