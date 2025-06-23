# import os
# import re
# import json
# import csv
# from utils import setup_logging, log, extract_text, clean_text, ensure_directories
# from parser import parse_text
# from llm_validation import llm_cross_validate
# from config import SECTION_HEADERS

# OUTPUT_DIR = "output"
# OUTPUT_TEXT = os.path.join(OUTPUT_DIR, "text")
# OUTPUT_VALIDATED_JSON = os.path.join(OUTPUT_DIR, "validated", "json")
# OUTPUT_VALIDATED_CSV = os.path.join(OUTPUT_DIR, "validated", "csv")
# OUTPUT_DISCREPANCY_JSON = os.path.join(OUTPUT_DIR, "discrepancy", "json")
# OUTPUT_DISCREPANCY_CSV = os.path.join(OUTPUT_DIR, "discrepancy", "csv")
# LOG_DIR = "logs"

# def get_latest_pdf_dir():
#     """
#     Returns the path to the latest 'PDF_VERSION_YYYY-MM-DD' directory in data/input.
#     """
#     base_dir = os.path.join("data", "input")
#     candidates = [
#         d for d in os.listdir(base_dir)
#         if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
#     ]
#     if not candidates:
#         raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
#     # Sort by the date in the directory name
#     latest = max(candidates, key=lambda d: d.split("_")[-1])
#     return os.path.join(base_dir, latest)

# def export_json(parsed, json_path, pdf_path):
#     # Add metadata about source PDF and processing
#     out = {
#         "source_pdf": os.path.abspath(pdf_path),
#         "records": parsed
#     }
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(out, f, indent=2)

# # def export_csv(parsed, csv_path):
# #     if not parsed:
# #         return
# #     fieldnames = list(parsed[0].keys())
# #     with open(csv_path, 'w', newline='', encoding='utf-8') as f:
# #         writer = csv.DictWriter(f, fieldnames=fieldnames)
# #         writer.writeheader()
# #         for row in parsed:
# #             writer.writerow(row)


# def export_csv(parsed, csv_path):
#     # If parsed is empty, use default fieldnames
#     fieldnames = list(parsed[0].keys()) if parsed else [
#         "ID", "Title", "Method", "Profile Applicability", "Description", "Rationale", "Impact", 
#         "Audit", "Audit Commands", "Remediations", "Remediation Commands", 
#         "Default value", "References", "CIS Controls", "MITRE ATT&CK Mappings", "Compliant"
#     ]
#     with open(csv_path, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in parsed:
#             writer.writerow(row)

# def save_validation_report(base_name, report, outdir):
#     path = os.path.join(outdir, base_name + "_validation.json")
#     with open(path, 'w', encoding='utf-8') as f:
#         json.dump(report, f, indent=2)

# def main():
#     ensure_directories([
#         OUTPUT_TEXT, LOG_DIR,
#         OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
#         OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV
#     ])
#     setup_logging(os.path.join(LOG_DIR, "pipeline.log"))
#     log("[*] Starting CIS PDF parsing pipeline...")

#     # Use the latest versioned PDF input directory
#     pdf_dir = get_latest_pdf_dir()
#     log(f"[*] Using PDF input directory: {pdf_dir}")

#     summary_stats = []  # For ranking at the end

#     for filename in os.listdir(pdf_dir):
#         if not filename.lower().endswith('.pdf'):
#             continue
#         pdf_path = os.path.join(pdf_dir, filename)
#         base = os.path.splitext(filename)[0]
#         txt_path = os.path.join(OUTPUT_TEXT, base + ".txt")
#         try:
#             extract_text(pdf_path, txt_path)
#             clean_text(txt_path)
#             parsed = parse_text(txt_path)
#             # Export outputs
#             validation = llm_cross_validate(parsed, txt_path)
#             if validation["status"] == "ok":
#                 json_dir = OUTPUT_VALIDATED_JSON
#                 csv_dir = OUTPUT_VALIDATED_CSV
#             else:
#                 json_dir = OUTPUT_DISCREPANCY_JSON
#                 csv_dir = OUTPUT_DISCREPANCY_CSV
#             json_path = os.path.join(json_dir, base + ".json")
#             csv_path = os.path.join(csv_dir, base + ".csv")
#             export_json(parsed, json_path, pdf_path)
#             export_csv(parsed, csv_path)
#             # Validation report is stored alongside the JSON output
#             save_validation_report(base, validation, json_dir)
#             log(f"[+] {filename} processed: {validation['summary']}")
#             summary_stats.append({
#                 "pdf": filename,
#                 "validation_percent": validation["percent_found"],
#                 "status": validation["status"],
#                 "controls_total": validation["expected_controls"],
#                 "controls_missing": validation["missing_count"],
#             })
#         except Exception as e:
#             log(f"[ERROR] Failed processing {filename}: {e}", "error")

#     # Save ranking summary
#     ranking = sorted(summary_stats, key=lambda x: x["validation_percent"], reverse=True)
#     with open(os.path.join(OUTPUT_DIR, "summary_validation_ranking.json"), 'w', encoding='utf-8') as f:
#         json.dump(ranking, f, indent=2)
#     log("[*] Validation ranking summary written.")

# if __name__ == "__main__":
#     main()


# #! Parallelized Code

# import os
# import re
# import json
# import csv
# from concurrent.futures import ProcessPoolExecutor, as_completed
# from tqdm import tqdm

# from utils import setup_logging, log, extract_text, clean_text, ensure_directories
# from parser import parse_text
# from llm_validation import llm_cross_validate
# from config import SECTION_HEADERS

# OUTPUT_DIR = "output"
# OUTPUT_TEXT = os.path.join(OUTPUT_DIR, "text")
# OUTPUT_VALIDATED_JSON = os.path.join(OUTPUT_DIR, "validated", "json")
# OUTPUT_VALIDATED_CSV = os.path.join(OUTPUT_DIR, "validated", "csv")
# OUTPUT_DISCREPANCY_JSON = os.path.join(OUTPUT_DIR, "discrepancy", "json")
# OUTPUT_DISCREPANCY_CSV = os.path.join(OUTPUT_DIR, "discrepancy", "csv")
# LOG_DIR = "logs"

# def get_latest_pdf_dir():
#     """
#     Returns the path to the latest 'PDF_VERSION_YYYY-MM-DD' directory in data/input.
#     """
#     base_dir = os.path.join("data", "input")
#     candidates = [
#         d for d in os.listdir(base_dir)
#         if os.path.isdir(os.path.join(base_dir, d)) and re.match(r"PDF_VERSION_\d{4}-\d{2}-\d{2}", d)
#     ]
#     if not candidates:
#         raise Exception("No PDF_VERSION_YYYY-MM-DD directories found in data/input.")
#     # Sort by the date in the directory name
#     latest = max(candidates, key=lambda d: d.split("_")[-1])
#     return os.path.join(base_dir, latest)

# def export_json(parsed, json_path, pdf_path):
#     # Add metadata about source PDF and processing
#     out = {
#         "source_pdf": os.path.abspath(pdf_path),
#         "records": parsed
#     }
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(out, f, indent=2)

# # def export_csv(parsed, csv_path):
# #     # If parsed is empty, use default fieldnames
# #     fieldnames = list(parsed[0].keys()) if parsed else [
# #         "ID", "Title", "Method", "Profile Applicability", "Description", "Rationale", "Impact",
# #         "Audit", "Audit Commands", "Remediations", "Remediation Commands",
# #         "Default value", "References", "CIS Controls", "MITRE ATT&CK Mappings", "Compliant"
# #     ]
# #     with open(csv_path, 'w', newline='', encoding='utf-8') as f:
# #         writer = csv.DictWriter(f, fieldnames=fieldnames)
# #         writer.writeheader()
# #         for row in parsed:
# #             writer.writerow(row)

# def export_csv(parsed, csv_path):
#     # Define the standard fieldnames you want in the CSV
#     fieldnames = [
#         "ID", "Title", "Method", "Profile Applicability",
#         "Description", "Rationale", "Impact", "Audit", "Audit Commands",
#         "Remediations", "Remediation Commands",
#         "Default value", "References", "CIS Controls",
#         "MITRE ATT&CK Mappings", "Compliant", "Ranking Score"
#     ]
#     with open(csv_path, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in parsed:
#             # Only keep keys that are in fieldnames; drop any extra keys like 'Additional Information'
#             row_filtered = {k: row.get(k, "") for k in fieldnames}
#             writer.writerow(row_filtered)
            
# def save_validation_report(base_name, report, outdir):
#     path = os.path.join(outdir, base_name + "_validation.json")
#     with open(path, 'w', encoding='utf-8') as f:
#         json.dump(report, f, indent=2)

# def process_pdf(pdf_path, OUTPUT_TEXT, OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
#                 OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV, SECTION_HEADERS):
#     base = os.path.splitext(os.path.basename(pdf_path))[0]
#     txt_path = os.path.join(OUTPUT_TEXT, base + ".txt")
#     try:
#         extract_text(pdf_path, txt_path)
#         clean_text(txt_path)
#         parsed = parse_text(txt_path)
#         validation = llm_cross_validate(parsed, txt_path)
#         if validation["status"] == "ok":
#             json_dir = OUTPUT_VALIDATED_JSON
#             csv_dir = OUTPUT_VALIDATED_CSV
#         else:
#             json_dir = OUTPUT_DISCREPANCY_JSON
#             csv_dir = OUTPUT_DISCREPANCY_CSV
#         json_path = os.path.join(json_dir, base + ".json")
#         csv_path = os.path.join(csv_dir, base + ".csv")
#         export_json(parsed, json_path, pdf_path)
#         export_csv(parsed, csv_path)
#         save_validation_report(base, validation, json_dir)
#         log(f"[+] {os.path.basename(pdf_path)} processed: {validation['summary']}")
#         return {
#             "pdf": os.path.basename(pdf_path),
#             "validation_percent": validation["percent_found"],
#             "status": validation["status"],
#             "controls_total": validation["expected_controls"],
#             "controls_missing": validation["missing_count"],
#         }
#     except Exception as e:
#         log(f"[ERROR] Failed processing {os.path.basename(pdf_path)}: {e}", "error")
#         return {
#             "pdf": os.path.basename(pdf_path),
#             "validation_percent": 0.0,
#             "status": "error",
#             "controls_total": 0,
#             "controls_missing": 0,
#             "error": str(e)
#         }

# def main():
#     ensure_directories([
#         OUTPUT_TEXT, LOG_DIR,
#         OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
#         OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV
#     ])
#     setup_logging(os.path.join(LOG_DIR, "pipeline.log"))
#     log("[*] Starting CIS PDF parsing pipeline...")

#     pdf_dir = get_latest_pdf_dir()
#     log(f"[*] Using PDF input directory: {pdf_dir}")

#     pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     pdf_paths = [os.path.join(pdf_dir, f) for f in pdf_files]

#     summary_stats = []

#     with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
#         futures = [
#             executor.submit(
#                 process_pdf,
#                 pdf_path,
#                 OUTPUT_TEXT,
#                 OUTPUT_VALIDATED_JSON,
#                 OUTPUT_VALIDATED_CSV,
#                 OUTPUT_DISCREPANCY_JSON,
#                 OUTPUT_DISCREPANCY_CSV,
#                 SECTION_HEADERS
#             )
#             for pdf_path in pdf_paths
#         ]
#         for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
#             result = future.result()
#             summary_stats.append(result)

#     # Save ranking summary
#     ranking = sorted(summary_stats, key=lambda x: x.get("validation_percent", 0), reverse=True)
#     with open(os.path.join(OUTPUT_DIR, "summary_validation_ranking.json"), 'w', encoding='utf-8') as f:
#         json.dump(ranking, f, indent=2)
#     log("[*] Validation ranking summary written.")

# if __name__ == "__main__":
#     main()
    
    
    
    


import os
import re
import json
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

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

# New: Report directories
OUTPUT_VALIDATED_REPORTS = os.path.join(OUTPUT_DIR, "validated", "reports")
OUTPUT_DISCREPANCY_REPORTS = os.path.join(OUTPUT_DIR, "discrepancy", "reports")

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

def natural_sort_key(s):
    """For sorting control IDs naturally, e.g. 1.1.9 < 1.1.10"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s or "")]

def export_json(parsed, json_path, pdf_path):
    out = {
        "source_pdf": os.path.abspath(pdf_path),
        "records": parsed
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

def export_csv(parsed, csv_path):
    fieldnames = [
        "ID", "Title", "Method", "Profile Applicability",
        "Description", "Rationale", "Impact", "Audit", "Audit Commands",
        "Remediations", "Remediation Commands",
        "Default value", "References", "CIS Controls",
        "MITRE ATT&CK Mappings", "Compliant", "Ranking Score"
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in parsed:
            row_filtered = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(row_filtered)

def save_validation_report(base_name, report, outdir):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, base_name + "_validation.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

def process_pdf(pdf_path, OUTPUT_TEXT, OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
                OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV, SECTION_HEADERS,
                OUTPUT_VALIDATED_REPORTS, OUTPUT_DISCREPANCY_REPORTS):
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    txt_path = os.path.join(OUTPUT_TEXT, base + ".txt")
    try:
        extract_text(pdf_path, txt_path)
        clean_text(txt_path)
        parsed = parse_text(txt_path)

        # Sort controls by natural order of ID
        parsed_sorted = sorted(parsed, key=lambda x: natural_sort_key(x.get("ID", "")))

        validation = llm_cross_validate(parsed_sorted, txt_path)
        if validation["status"] == "ok":
            json_dir = OUTPUT_VALIDATED_JSON
            csv_dir = OUTPUT_VALIDATED_CSV
            report_dir = OUTPUT_VALIDATED_REPORTS
        else:
            json_dir = OUTPUT_DISCREPANCY_JSON
            csv_dir = OUTPUT_DISCREPANCY_CSV
            report_dir = OUTPUT_DISCREPANCY_REPORTS
        json_path = os.path.join(json_dir, base + ".json")
        csv_path = os.path.join(csv_dir, base + ".csv")
        export_json(parsed_sorted, json_path, pdf_path)
        export_csv(parsed_sorted, csv_path)
        save_validation_report(base, validation, report_dir)
        log(f"[+] {os.path.basename(pdf_path)} processed: {validation['summary']}")
        return {
            "pdf": os.path.basename(pdf_path),
            "validation_percent": validation["percent_controls_found"],
            "status": validation["status"],
            "controls_total": validation["expected_controls"],
            "controls_missing": validation["missing_count"],
        }
    except Exception as e:
        log(f"[ERROR] Failed processing {os.path.basename(pdf_path)}: {e}", "error")
        return {
            "pdf": os.path.basename(pdf_path),
            "validation_percent": 0.0,
            "status": "error",
            "controls_total": 0,
            "controls_missing": 0,
            "error": str(e)
        }

def main():
    ensure_directories([
        OUTPUT_TEXT, LOG_DIR,
        OUTPUT_VALIDATED_JSON, OUTPUT_VALIDATED_CSV,
        OUTPUT_DISCREPANCY_JSON, OUTPUT_DISCREPANCY_CSV,
        OUTPUT_VALIDATED_REPORTS, OUTPUT_DISCREPANCY_REPORTS
    ])
    setup_logging(os.path.join(LOG_DIR, "pipeline.log"))
    log("[*] Starting CIS PDF parsing pipeline...")

    pdf_dir = get_latest_pdf_dir()
    log(f"[*] Using PDF input directory: {pdf_dir}")

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    pdf_paths = [os.path.join(pdf_dir, f) for f in pdf_files]

    summary_stats = []

    with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        futures = [
            executor.submit(
                process_pdf,
                pdf_path,
                OUTPUT_TEXT,
                OUTPUT_VALIDATED_JSON,
                OUTPUT_VALIDATED_CSV,
                OUTPUT_DISCREPANCY_JSON,
                OUTPUT_DISCREPANCY_CSV,
                SECTION_HEADERS,
                OUTPUT_VALIDATED_REPORTS,
                OUTPUT_DISCREPANCY_REPORTS
            )
            for pdf_path in pdf_paths
        ]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
            result = future.result()
            summary_stats.append(result)

    # Save ranking summary
    ranking = sorted(summary_stats, key=lambda x: x.get("validation_percent", 0), reverse=True)
    with open(os.path.join(OUTPUT_DIR, "summary_validation_ranking.json"), 'w', encoding='utf-8') as f:
        json.dump(ranking, f, indent=2)
    log("[*] Validation ranking summary written.")

if __name__ == "__main__":
    main()