import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

CIS_URL = "https://www.cisecurity.org/cis-benchmarks/"  # update to actual page
PDF_DIR = "pdf_versions"

def get_available_pdfs():
    """Scrape the CIS page for PDF download links."""
    resp = requests.get(CIS_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        if ".pdf" in a['href']:
            links.append(a['href'])
    return links

def download_pdf(url, dest_dir):
    filename = url.split("/")[-1].split("?")[0]
    # Add timestamp/version to filename
    now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = os.path.join(dest_dir, f"{filename.rsplit('.',1)[0]}_{now}.pdf")
    print(f"Downloading {url} -> {out_path}")
    resp = requests.get(url)
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path

def check_for_updates():
    os.makedirs(PDF_DIR, exist_ok=True)
    seen_file = os.path.join(PDF_DIR, "downloaded_files.txt")
    seen = set()
    if os.path.exists(seen_file):
        with open(seen_file) as f:
            seen = set(line.strip() for line in f)
    links = get_available_pdfs()
    new_links = [link for link in links if link not in seen]
    for link in new_links:
        try:
            pdf_path = download_pdf(link, PDF_DIR)
            print(f"[+] PDF downloaded: {pdf_path}")
            with open(seen_file, "a") as f:
                f.write(link + "\n")
            # You can trigger your parser/validator here
            # os.system(f"python main.py --input {pdf_path}")
        except Exception as e:
            print(f"[!] Failed to download {link}: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(check_for_updates, "interval", hours=6)
    print("[*] CIS PDF auto-updater running (checks every 6 hours)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[!] Scheduler stopped.")