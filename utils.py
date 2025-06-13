import os
import re
import logging
import fitz
from .config import INVISIBLE_UNICODE_PATTERN, KNOWN_HEADER_FOOTER_PATTERNS, SECTION_HEADERS

def setup_logging(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

def log(msg,level="info"):
    print(msg)
    getattr(logging,level)(msg)

def extract_text(pdf_path, text_path):
    log(f"[+] Extracting text from: {pdf_path}")
    pdf_text = ""
    try:
        with fitz.open(pdf_path) as pdf_file:
            for page_num in range(pdf_file.page_count):
                page = pdf_file[page_num]
                pdf_text += page.get_text()
        
        with open(text_path,'w', encoding='utf-8') as f:
            f.write(pdf_text)
        
        log(f"[+] Text written tp: {text_path}")
    
    except Exception as e:
        log(f"[ERROR] Failed extracting text from {pdf_path}: {e}", "error")
        raise

def remove_invisible_unicode(text):
    return re.sub(INVISIBLE_UNICODE_PATTERN, '', text)


def normalize_whitespace(line):
    line = re.sub(r'[\t]+',' ', line)
    return line.strip() + '\n' if line.strip() else ''

def remove_headers_footers(lines, patterns):
    cleaned = []
    for line in lines:
        if not any(re.search(pat,line) for pat in patterns):
            cleaned.append(line)
        return cleaned
    
def ensure_section_headers(lines, headers):
    pattern = r'(' + '|'.join(re.escape(h) for h in headers) + r')'
    new_line = []
    for line in lines:
        split_line = re.sub(pattern, r'\n\1\n', line)
        for piece in split_line.split('\n'):
            if piece.strip():
                new_line.append(piece + '\n')
    return new_line

def clean_text(text_path):
    try:
        with open(text_path,'r', encoding='utf-8') as f:
            lines =f.readlines()
        lines = [remove_invisible_unicode(line) for line in lines]
        lines = [normalize_whitespace(line) for line in lines]
        lines = [line for line in lines if line.strip()]
        lines = remove_headers_footers(lines, KNOWN_HEADER_FOOTER_PATTERNS)
        lines = ensure_section_headers(lines, SECTION_HEADERS)
        lines = [line for line in lines if line.strip()]

        with open(text_path, 'w', encoding = "utf-8") as f:
            f.writelines(lines)
        log(f"[+] Cleaned text file: {text_path}")
    except Exception as e:
        log(f"[ERROR] Cleaning Failed for {text_path}: {e}", "error")
        raise
