import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
OUTPUT_TEXT = os.path.join(BASE_DIR, "data", "output", "text")
OUTPUT_JSON = os.path.join(BASE_DIR, "data", "output", "json")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "output", "csv")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR,"parser.log")

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
    r'Pages\s*\d+'                 #Page 1
    r'P\s*a\s*g\s*e\s*\d*'         #P a g e
    r'CIS\s+Benchmark'
]   

INVISIBLE_UNICODE_PATTERN = r'[\u200B-\u200D\uFEFF]'