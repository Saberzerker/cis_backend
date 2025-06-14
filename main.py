import os
import re
import json
import csv
from utils import setup_logging, log, extract_text, clean_text, ensure_directories
from parser import parse_text
from llm_validation import llm_cross_validate
from config import SECTION_HEADERS

OUTPUT_DIR = "output"
OUTPUT_TEXT = os.path.join(OUTPUT_DIR, "text")
OUTPUT_VALIDATED_JSON = os.path.join(OUTPUT_DIR, "validated", "json")
OUTPUT_VALIDATED_CSV = os.path.join(OUTPUT_DIR, "validated", "csv")
OUTPUT_DISCREPANCY_JSON = os.path.join(OUTPUT_DIR, "discrepancy", "json")
OUTPUT_DISCREPANCY_CSV = os.path.join(OUTPUT_DIR, "discrepancy", "csv")
LOG_DIR = "logs"

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

def export_json(parsed, json_path, pdf_path):
    # Add metadata about source PDF and processing
    out = {
        "source_pdf": os.path.abspath(pdf_path),
        "records": parsed
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

# def export_csv(parsed, csv_path):
#     if not parsed:
#         return
#     fieldnames = list(parsed[0].keys())
#     with open(csv_path, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in parsed:
#             writer.writerow(row)


def export_csv(parsed, csv_path):
    # If parsed is empty, use default fieldnames
    fieldnames = list(parsed[0].keys()) if parsed else [
        "ID", "Title", "Method", "Profile Applicability", "Description", "Rationale", "Impact", 
        "Audit", "Audit Commands", "Remediations", "Remediation Commands", 
        "Default value", "References", "CIS Controls", "MITRE ATT&CK Mappings", "Compliant"
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in parsed:
            writer.writerow(row)

def save_validation_report(base_name, report, outdir):
    path = os.path.join(outdir, base_name + "_validation.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

def main():
    ensure_directories([
        OUTPUT_TEXT, LOG_DIR,
        OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
        OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV
    ])
    setup_logging(os.path.join(LOG_DIR, "pipeline.log"))
    log("[*] Starting CIS PDF parsing pipeline...")

    # Use the latest versioned PDF input directory
    pdf_dir = get_latest_pdf_dir()
    log(f"[*] Using PDF input directory: {pdf_dir}")

    summary_stats = []  # For ranking at the end

    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith('.pdf'):
            continue
        pdf_path = os.path.join(pdf_dir, filename)
        base = os.path.splitext(filename)[0]
        txt_path = os.path.join(OUTPUT_TEXT, base + ".txt")
        try:
            extract_text(pdf_path, txt_path)
            clean_text(txt_path)
            parsed = parse_text(txt_path)
            # Export outputs
            validation = llm_cross_validate(parsed, txt_path)
            if validation["status"] == "ok":
                json_dir = OUTPUT_VALIDATED_JSON
                csv_dir = OUTPUT_VALIDATED_CSV
            else:
                json_dir = OUTPUT_DISCREPANCY_JSON
                csv_dir = OUTPUT_DISCREPANCY_CSV
            json_path = os.path.join(json_dir, base + ".json")
            csv_path = os.path.join(csv_dir, base + ".csv")
            export_json(parsed, json_path, pdf_path)
            export_csv(parsed, csv_path)
            # Validation report is stored alongside the JSON output
            save_validation_report(base, validation, json_dir)
            log(f"[+] {filename} processed: {validation['summary']}")
            summary_stats.append({
                "pdf": filename,
                "validation_percent": validation["percent_found"],
                "status": validation["status"],
                "controls_total": validation["expected_controls"],
                "controls_missing": validation["missing_count"],
            })
        except Exception as e:
            log(f"[ERROR] Failed processing {filename}: {e}", "error")

    # Save ranking summary
    ranking = sorted(summary_stats, key=lambda x: x["validation_percent"], reverse=True)
    with open(os.path.join(OUTPUT_DIR, "summary_validation_ranking.json"), 'w', encoding='utf-8') as f:
        json.dump(ranking, f, indent=2)
    log("[*] Validation ranking summary written.")

if __name__ == "__main__":
    main()