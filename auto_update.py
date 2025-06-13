import os
import sys
import requests
import json
import datetime
import time
import re

from bs4 import BeautifulSoup

from dotenv import load_dotenv; load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import imaplib
import email
from email.header import decode_header

# --- Configuration ---
CIS_BENCHMARKS_URL = "https://www.cisecurity.org/cis-benchmarks"
VERSION_FILE = "local_versions.json"
LOG_FILE = "update_log.txt"

CIS_DOWNLOAD_URL = "https://learn.cisecurity.org/benchmarks"
EMAIL_ADDRESS = "smartdummyedge@gmail.com"
EMAIL_PASSWORD = os.getenv("CIS_EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
HEADLESS = False  # Set to False for manual steps

# --- Form details ---
FORM_DATA = {
    "first_name": "Lokesh",
    "last_name": "Yadav",
    "organization": "Mysore University",
    "sector": "Education",
    "role": "Student",
    "email": EMAIL_ADDRESS,
    "country": "India"
}

def log_event(event_type, details=""):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event_type}: {details}\n")

def scrape_bench_versions():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(CIS_BENCHMARKS_URL, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    version_map = {}
    for a in soup.find_all("a", class_="cta"):
        tech = a.get("tech_key")
        version = a.get("version")
        if tech and version:
            version_map[tech] = version
    return version_map

def load_local_versions():
    if not os.path.exists(VERSION_FILE):
        return {}
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_local_versions(version_map):
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(version_map, f, indent=2)

def check_for_updates():
    remote = scrape_bench_versions()
    local = load_local_versions()
    updates = {k: v for k, v in remote.items() if local.get(k) != v}
    if updates:
        print("Updates found!")
        for k, v in updates.items():
            print(f"{k}: {local.get(k)} → {v}")
        log_event("UPDATE_AVAILABLE", f"Updates: {updates}")
    else:
        print("No new versions found.")
        log_event("NO_UPDATE", "No new versions found.")
    return updates, remote

def get_output_dir():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_name = f"PDF_VERSION_{today_str}"
    output_dir = os.path.join("data", "input", dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def setup_driver(download_dir, headless=HEADLESS):
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium import webdriver

    options = FirefoxOptions()
    options.headless = headless
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", os.path.abspath(download_dir))
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    options.profile = profile
    driver = webdriver.Firefox(options=options)
    return driver


def dismiss_cookie_popup(driver):
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        print("[*] Cookie popup dismissed (Allow All).")
        log_event("COOKIE", "Cookie popup dismissed (Allow All)")
    except Exception as e:
        print("[*] No cookie popup found or already dismissed.", e)
        log_event("COOKIE", f"No cookie popup found or already dismissed. {e}")

def fill_download_form(driver):
    driver.get(CIS_DOWNLOAD_URL)
    dismiss_cookie_popup(driver)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "799323_28507pi_799323_28507"))
    )
    driver.find_element(By.NAME, "799323_28507pi_799323_28507").send_keys(FORM_DATA["first_name"])
    driver.find_element(By.NAME, "799323_28509pi_799323_28509").send_keys(FORM_DATA["last_name"])
    driver.find_element(By.NAME, "799323_28511pi_799323_28511").send_keys(FORM_DATA["organization"])
    Select(driver.find_element(By.NAME, "799323_28513pi_799323_28513")).select_by_visible_text(FORM_DATA["sector"])
    Select(driver.find_element(By.NAME, "799323_28515pi_799323_28515")).select_by_visible_text(FORM_DATA["role"])
    driver.find_element(By.NAME, "799323_28497pi_799323_28497").send_keys(FORM_DATA["email"])
    Select(driver.find_element(By.NAME, "799323_28499pi_799323_28499")).select_by_visible_text(FORM_DATA["country"])
    marketing_checkbox = driver.find_element(By.NAME, "799323_28501pi_799323_28501_410269")
    if not marketing_checkbox.is_selected():
        marketing_checkbox.click()
    terms_checkbox = driver.find_element(By.NAME, "799323_28505pi_799323_28505_410271")
    if not terms_checkbox.is_selected():
        terms_checkbox.click()
    print("[*] Please solve the CAPTCHA in the browser window, then click Submit.")
    log_event("FORM_FILLED", "Form filled, waiting for CAPTCHA")
    if not HEADLESS:
        input("[!] After you have solved CAPTCHA and submitted the form, press Enter to continue...")

def extract_access_pdfs_link(html):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        style = a.get("style", "")
        href = a["href"]
        if (
            text == "Access PDFs" and
            "background-color:#72a94e" in style and
            "display:inline-block" in style and
            href.startswith("https://learn.cisecurity.org/e/799323/")
        ):
            return href
    return None

def wait_for_email_and_extract_link(timeout=300, poll=15):
    print("[*] Waiting for CIS email with Access PDFs link...")
    log_event("EMAIL_WAIT", "Waiting for CIS email with Access PDFs link...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
                mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                mail.select("INBOX")
                status, msg_nums = mail.search(None, '(UNSEEN FROM "learn@cisecurity.org")')
                if status == "OK":
                    for num in reversed(msg_nums[0].split()):
                        typ, msg_data = mail.fetch(num, "(RFC822)")
                        if typ != "OK":
                            continue
                        msg = email.message_from_bytes(msg_data[0][1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8", errors="replace")
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/html":
                                    charset = part.get_content_charset() or "utf-8"
                                    html = part.get_payload(decode=True).decode(charset, errors="replace")
                                    link = extract_access_pdfs_link(html)
                                    if link:
                                        log_event("EMAIL_FOUND", "Found Access PDFs link in email.")
                                        print("[+] Found Access PDFs link in email.")
                                        return link
                        else:
                            if msg.get_content_type() == "text/html":
                                charset = msg.get_content_charset() or "utf-8"
                                html = msg.get_payload(decode=True).decode(charset, errors="replace")
                                link = extract_access_pdfs_link(html)
                                if link:
                                    log_event("EMAIL_FOUND", "Found Access PDFs link in email.")
                                    print("[+] Found Access PDFs link in email.")
                                    return link
        except Exception as e:
            log_event("EMAIL_ERROR", str(e))
            print(f"[!] Error checking email: {e}")
        time.sleep(poll)
    log_event("EMAIL_TIMEOUT", "Timed out waiting for CIS Access PDFs email.")
    raise TimeoutError("Timed out waiting for CIS Access PDFs email.")



def wait_for_downloads(download_dir, timeout=600):
    start = time.time()
    while True:
        if not any(f.endswith('.part') for f in os.listdir(download_dir)):
            break
        if time.time() - start > timeout:
            print("[!] Timeout: Some downloads may be incomplete.")
            break
        time.sleep(1)

def download_all_pdfs(downloads_page_url):
    output_dir = get_output_dir()
    driver = setup_driver(output_dir)
    driver.get(downloads_page_url)
    time.sleep(2)
    dismiss_cookie_popup(driver)

    # Expand all accordions/dropdowns if present
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, ".toggle-section, .MuiButtonBase-root.MuiAccordionSummary-root")
        for d in dropdowns:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", d)
                d.click()
            except Exception:
                pass
        time.sleep(2)
    except Exception:
        pass

    # Wait for all "Download PDF" links to appear
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]"))
        )
    except Exception as e:
        print("[!] PDF download links did not load:", e)
        driver.quit()
        return

    idx = 0
    while True:
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]")
        if idx >= len(pdf_links):
            break
        link_elem = pdf_links[idx]
        try:
            driver.execute_script("arguments[0].scrollIntoView();", link_elem)
            link_elem.click()
            print(f"[*] Clicked PDF link {idx+1} of {len(pdf_links)}")
            time.sleep(2.5)  # Adjust for your network speed
        except Exception as e:
            print(f"[!] Failed to click PDF link {idx+1}: {e}")
        idx += 1

    print("[*] Waiting for downloads to finish...")
    wait_for_downloads(output_dir, timeout=600)
    driver.quit()
    print(f"[+] Attempted download of {idx} PDFs to {output_dir}")

def main():
    log_event("CHECK", "Checking for new CIS Benchmark versions")
    updates, remote = check_for_updates()
    if updates:
        print("[*] New versions found, proceeding with update.")
        log_event("AUTO_UPDATE_START", "New versions found. Starting auto update process.")
        driver = setup_driver(get_output_dir())
        try:
            fill_download_form(driver)
        finally:
            driver.quit()
        log_event("SUBMIT", "User submitted form, waiting for email")
        print("[*] Waiting for email...")
        access_link = wait_for_email_and_extract_link()
        log_event("DOWNLOAD_START", f"Starting download from {access_link}")
        print("[*] Downloading all PDFs from email link...")
        download_all_pdfs(access_link)
        log_event("UPDATED", f"Updated local_versions.json with {len(remote)} entries.")
        save_local_versions(remote)
        print("[*] All CIS PDFs downloaded to", get_output_dir())
    else:
        print("No new CIS PDF versions found. You are up to date.")
        log_event("NO_UPDATE", "No new CIS PDF versions found. You are up to date.")

if __name__ == "__main__":
    main()