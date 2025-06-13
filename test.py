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

LOG_FILE = "update_log.txt"
HEADLESS = True
def log_event(event_type, details=""):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event_type}: {details}\n")

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

if __name__ == "__main__":
    # <<<--- UPDATE THIS LINE WITH YOUR DOWNLOAD PAGE LINK --->>>
    downloads_page_url = "https://learn.cisecurity.org/e/799323/l-799323-2020-07-20-28mnm/2mnqr/2468316193/h/Up1Q8dCgFQMbXxV904KZrQBGgVBYWXqxW6hdW29E_fg"
    download_all_pdfs(downloads_page_url)