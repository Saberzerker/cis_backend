# import os
# import sys
# import requests
# import json
# import datetime
# import time
# import re

# from bs4 import BeautifulSoup

# from dotenv import load_dotenv; load_dotenv()
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import imaplib
# import email
# from email.header import decode_header

# LOG_FILE = "update_log.txt"
# HEADLESS = True
# def log_event(event_type, details=""):
#     timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "a", encoding="utf-8") as f:
#         f.write(f"[{timestamp}] {event_type}: {details}\n")

# def get_output_dir():
#     today_str = datetime.datetime.now().strftime("%Y-%m-%d")
#     dir_name = f"PDF_VERSION_{today_str}"
#     output_dir = os.path.join("data", "input", dir_name)
#     os.makedirs(output_dir, exist_ok=True)
#     return output_dir

# def setup_driver(download_dir, headless=HEADLESS):
#     from selenium.webdriver.firefox.options import Options as FirefoxOptions
#     from selenium import webdriver

#     options = FirefoxOptions()
#     options.headless = headless
#     profile = webdriver.FirefoxProfile()
#     profile.set_preference("browser.download.folderList", 2)
#     profile.set_preference("browser.download.dir", os.path.abspath(download_dir))
#     profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
#     profile.set_preference("pdfjs.disabled", True)
#     profile.set_preference("browser.download.manager.showWhenStarting", False)
#     profile.set_preference("browser.download.panel.shown", False)
#     profile.set_preference("browser.download.useDownloadDir", True)
#     options.profile = profile
#     driver = webdriver.Firefox(options=options)
#     return driver

# def dismiss_cookie_popup(driver):
#     try:
#         cookie_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
#         )
#         cookie_button.click()
#         print("[*] Cookie popup dismissed (Allow All).")
#         log_event("COOKIE", "Cookie popup dismissed (Allow All)")
#     except Exception as e:
#         print("[*] No cookie popup found or already dismissed.", e)
#         log_event("COOKIE", f"No cookie popup found or already dismissed. {e}")




# def wait_for_downloads(download_dir, timeout=600):
#     start = time.time()
#     while True:
#         if not any(f.endswith('.part') for f in os.listdir(download_dir)):
#             break
#         if time.time() - start > timeout:
#             print("[!] Timeout: Some downloads may be incomplete.")
#             break
#         time.sleep(1)

# def download_all_pdfs(downloads_page_url):
#     output_dir = get_output_dir()
#     driver = setup_driver(output_dir)
#     driver.get(downloads_page_url)
#     time.sleep(2)
#     dismiss_cookie_popup(driver)

#     # Expand all accordions/dropdowns if present
#     try:
#         dropdowns = driver.find_elements(By.CSS_SELECTOR, ".toggle-section, .MuiButtonBase-root.MuiAccordionSummary-root")
#         for d in dropdowns:
#             try:
#                 driver.execute_script("arguments[0].scrollIntoView();", d)
#                 d.click()
#             except Exception:
#                 pass
#         time.sleep(2)
#     except Exception:
#         pass

#     # Wait for all "Download PDF" links to appear
#     try:
#         WebDriverWait(driver, 40).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]"))
#         )
#     except Exception as e:
#         print("[!] PDF download links did not load:", e)
#         driver.quit()
#         return

#     idx = 0
#     while True:
#         pdf_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]")
#         if idx >= len(pdf_links):
#             break
#         link_elem = pdf_links[idx]
#         try:
#             driver.execute_script("arguments[0].scrollIntoView();", link_elem)
#             link_elem.click()
#             print(f"[*] Clicked PDF link {idx+1} of {len(pdf_links)}")
#             time.sleep(2.5)  # Adjust for your network speed
#         except Exception as e:
#             print(f"[!] Failed to click PDF link {idx+1}: {e}")
#         idx += 1

#     print("[*] Waiting for downloads to finish...")
#     wait_for_downloads(output_dir, timeout=600)
#     driver.quit()
#     print(f"[+] Attempted download of {idx} PDFs to {output_dir}")

# if __name__ == "__main__":
#     # <<<--- UPDATE THIS LINE WITH YOUR DOWNLOAD PAGE LINK --->>>
#     downloads_page_url = "https://learn.cisecurity.org/e/799323/l-799323-2020-07-20-28mnm/2mnqr/2468316193/h/Up1Q8dCgFQMbXxV904KZrQBGgVBYWXqxW6hdW29E_fg"
#     download_all_pdfs(downloads_page_url)


#! VERSION 2.0
# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from tqdm import tqdm

# LOG_FILE = "update_log.txt"
# HEADLESS = True

# def log_event(event_type, details=""):
#     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "a", encoding="utf-8") as f:
#         f.write(f"[{timestamp}] {event_type}: {details}\n")

# def get_output_dir():
#     today_str = time.strftime("%Y-%m-%d")
#     dir_name = f"PDF_VERSION_{today_str}"
#     output_dir = os.path.join("data", "input", dir_name)
#     os.makedirs(output_dir, exist_ok=True)
#     return output_dir

# def setup_driver(download_dir, headless=HEADLESS):
#     options = FirefoxOptions()
#     options.headless = headless
#     profile = webdriver.FirefoxProfile()
#     profile.set_preference("browser.download.folderList", 2)
#     profile.set_preference("browser.download.dir", os.path.abspath(download_dir))
#     profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
#     profile.set_preference("pdfjs.disabled", True)
#     profile.set_preference("browser.download.manager.showWhenStarting", False)
#     profile.set_preference("browser.download.panel.shown", False)
#     profile.set_preference("browser.download.useDownloadDir", True)
#     options.profile = profile
#     driver = webdriver.Firefox(options=options)
#     return driver

# def dismiss_cookie_popup(driver):
#     try:
#         cookie_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
#         )
#         cookie_button.click()
#         print("[*] Cookie popup dismissed (Allow All).")
#         log_event("COOKIE", "Cookie popup dismissed (Allow All)")
#     except Exception as e:
#         print("[*] No cookie popup found or already dismissed.", e)
#         log_event("COOKIE", f"No cookie popup found or already dismissed. {e}")

# def extract_all_pdf_links(driver):
#     # Expand all accordions/dropdowns if present
#     try:
#         dropdowns = driver.find_elements(By.CSS_SELECTOR, ".toggle-section, .MuiButtonBase-root.MuiAccordionSummary-root")
#         for d in dropdowns:
#             try:
#                 driver.execute_script("arguments[0].scrollIntoView();", d)
#                 d.click()
#             except Exception:
#                 pass
#         # Wait for page to render after expanding
#         time.sleep(2)
#         # Scroll to bottom in case of lazy loading
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#     except Exception:
#         pass
#     # Wait for download links to appear
#     try:
#         WebDriverWait(driver, 40).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]"))
#         )
#     except Exception as e:
#         print("[!] PDF download links did not load:", e)
#         return []
#     # Parse links with BeautifulSoup
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     links = []
#     for a in soup.find_all("a", class_="cta_button"):
#         if "Download PDF" in a.get_text(strip=True) and a.has_attr("href") and a["href"].startswith("http"):
#             links.append(a["href"])
#     return links

# def download_pdf(url, output_dir, session=None, retry=0, max_retries=3):
#     local_filename = os.path.join(output_dir, url.split("/")[-1].split("?")[0])
#     session = session or requests.Session()
#     try:
#         r = session.get(url, timeout=60)
#         if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
#             with open(local_filename, "wb") as f:
#                 f.write(r.content)
#             return (url, True, "")
#         else:
#             return (url, False, f"Bad status/content: {r.status_code}")
#     except Exception as e:
#         if retry < max_retries:
#             time.sleep(2 ** retry)
#             return download_pdf(url, output_dir, session, retry + 1, max_retries)
#         return (url, False, str(e))

# def download_all_pdfs(downloads_page_url):
#     output_dir = get_output_dir()
#     driver = setup_driver(output_dir)
#     driver.get(downloads_page_url)
#     time.sleep(2)
#     dismiss_cookie_popup(driver)
#     pdf_links = extract_all_pdf_links(driver)
#     driver.quit()
#     print(f"[*] Found {len(pdf_links)} PDF links. Starting parallel download...")

#     if not pdf_links:
#         print("[!] No PDF links found. Aborting download.")
#         return

#     session = requests.Session()
#     download_results = []
#     with ThreadPoolExecutor(max_workers=8) as executor:
#         futures = {executor.submit(download_pdf, url, output_dir, session): url for url in pdf_links}
#         for f in tqdm(as_completed(futures), total=len(futures), desc="Downloading PDFs"):
#             res = f.result()
#             download_results.append(res)

#     # Summary
#     success = [r for r in download_results if r[1]]
#     failed = [r for r in download_results if not r[1]]
#     print(f"\n[+] Downloaded {len(success)}/{len(pdf_links)} PDFs successfully.")
#     if failed:
#         print("[!] Failed downloads:")
#         for f in failed:
#             print(f"    {f[0]} - Error: {f[2]}")
#     print(f"[+] All downloads attempted. Files are in: {output_dir}")

#     with open(os.path.join(output_dir, "download_log.txt"), "w", encoding="utf-8") as logf:
#         for r in download_results:
#             logf.write(f"{r[0]}\t{'SUCCESS' if r[1] else 'FAIL'}\t{r[2]}\n")

# if __name__ == "__main__":
#     # <<<--- YOUR PDF DOWNLOAD PAGE LINK BELOW --->>>
#     downloads_page_url = "https://learn.cisecurity.org/e/799323/l-799323-2020-07-20-28mnm/2mnqr/2468316193/h/Up1Q8dCgFQMbXxV904KZrQBGgVBYWXqxW6hdW29E_fg"
#     download_all_pdfs(downloads_page_url)



#! CURRENT WORKING STANDARD (THE BEST TILL NOW)
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

LOG_FILE = "update_log.txt"
HEADLESS = True
BATCH_SIZE = 50  # Number of PDFs per browser instance
MAX_WORKERS = 6  # Number of parallel browser instances

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

def expand_accordions(driver):
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

def wait_for_downloads(download_dir, timeout=1200):
    start = time.time()
    while True:
        if not any(f.endswith('.part') for f in os.listdir(download_dir)):
            break
        if time.time() - start > timeout:
            print("[!] Timeout: Some downloads may be incomplete.")
            break
        time.sleep(1)

def get_all_pdf_links(downloads_page_url, output_dir):
    driver = setup_driver(output_dir)
    driver.get(downloads_page_url)
    time.sleep(2)
    dismiss_cookie_popup(driver)
    expand_accordions(driver)
    # Wait for all "Download PDF" links to appear
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]"))
        )
    except Exception as e:
        print("[!] PDF download links did not load:", e)
        driver.quit()
        return []
    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]")
    driver.quit()
    print(f"[*] Found {len(pdf_links)} PDF links.")
    log_event("SCRAPE", f"Found {len(pdf_links)} PDF links.")
    return len(pdf_links)

def download_batch(downloads_page_url, indices, output_dir, worker_id):
    print(f"[Worker {worker_id}] Starting worker for indices {indices[0]} to {indices[-1]}")
    driver = setup_driver(output_dir)
    driver.get(downloads_page_url)
    time.sleep(2)
    dismiss_cookie_popup(driver)
    expand_accordions(driver)
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]"))
        )
    except Exception as e:
        print(f"[Worker {worker_id}] PDF links did not load: {e}")
        driver.quit()
        return 0
    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'cta_button') and contains(text(), 'Download PDF')]")
    count = 0
    for idx in indices:
        if idx >= len(pdf_links):
            break
        link_elem = pdf_links[idx]
        try:
            driver.execute_script("arguments[0].scrollIntoView();", link_elem)
            link_elem.click()
            print(f"[Worker {worker_id}] Clicked PDF link {idx+1}")
            time.sleep(2.5)  # Adjust for your network speed
            count += 1
        except Exception as e:
            print(f"[Worker {worker_id}] Failed to click PDF link {idx+1}: {e}")
    print(f"[Worker {worker_id}] Waiting for downloads to finish...")
    wait_for_downloads(output_dir, timeout=600)
    driver.quit()
    print(f"[Worker {worker_id}] Completed download of {count} PDFs.")
    return count

def download_all_pdfs_parallel(downloads_page_url):
    output_dir = get_output_dir()
    n_links = get_all_pdf_links(downloads_page_url, output_dir)
    if n_links == 0:
        print("[!] No PDF links found. Exiting.")
        return

    # Split indices into batches
    indices = list(range(n_links))
    batches = [indices[i:i+BATCH_SIZE] for i in range(0, n_links, BATCH_SIZE)]

    print(f"[*] Downloading with {min(MAX_WORKERS, len(batches))} parallel browser workers, batch size {BATCH_SIZE}.")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for worker_id, batch_indices in enumerate(batches):
            futures.append(executor.submit(download_batch, downloads_page_url, batch_indices, output_dir, worker_id))
        total_downloaded = 0
        for f in as_completed(futures):
            total_downloaded += f.result()

    print(f"[+] Attempted download of {total_downloaded} PDFs to {output_dir}")
    log_event("DOWNLOAD", f"Attempted download of {total_downloaded} PDFs to {output_dir}")

if __name__ == "__main__":
    # <<<--- UPDATE THIS LINE WITH YOUR DOWNLOAD PAGE LINK --->>>
    downloads_page_url = "https://learn.cisecurity.org/e/799323/l-799323-2020-07-20-28mnm/2mnqr/2468316193/h/Up1Q8dCgFQMbXxV904KZrQBGgVBYWXqxW6hdW29E_fg"
    download_all_pdfs_parallel(downloads_page_url)


