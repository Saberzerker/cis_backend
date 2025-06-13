import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
OUTPUT_TEXT = os.path.join(BASE_DIR, "data", "output", "text")
OUTPUT_JSON = os.path.join(BASE_DIR, "data", "output", "json")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "output", "csv")
OUTPUT_VALIDATION = os.path.join(BASE_DIR, "data", "output", "validation")
PDF_ACCURATE = os.path.join(BASE_DIR, "pdf_accurate")
PDF_DISCREPANCY = os.path.join(BASE_DIR, "pdf_discrepancy")
PDF_REPORTS = os.path.join(BASE_DIR, "pdf_reports")
PDF_VERSIONS = os.path.join(BASE_DIR, "pdf_versions")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "parser.log")

SECTION_HEADERS = [
    "Profile Applicability:",
    "Description:",
    "Rationale:",
    "Impact:",
    "Audit:",
    "Remediation:",
    "Default Value:",
    "References:",
    "CIS Controls:",
    "MITRE ATT&CK Mappings:"
]

KNOWN_HEADER_FOOTER_PATTERNS = [
    r'Pages\s*\d+',
    r'P\s*a\s*g\s*e\s*\d*',
    r'CIS\s+Benchmark'
]

INVISIBLE_UNICODE_PATTERN = r'[\u200B-\u200D\uFEFF]'