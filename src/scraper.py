# src/scraper.py
import os
import time
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.db import init_db, load_seen_ids_db, save_scraped_data_db

init_db()
seen_ids = load_seen_ids_db()

# ---- Function 1: Date calculation ----
def get_date_10_days_before(date_str: str, date_format: str = "%d/%m/%Y") -> str:
    """Return a date string that is 10 days before the given date."""
    try:
        input_date = datetime.strptime(date_str, date_format)
        new_date = input_date - timedelta(days=10)
        return new_date.strftime(date_format)
    except ValueError as e:
        raise ValueError(f"Invalid date or format: {e}")


# ---- Function 2: Setup Selenium ----
def setup_selenium(download_dir: str):
    """
    Set up Selenium Chrome driver with custom PDF download directory.
    Returns a WebDriver instance.
    """
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.maximize_window()
    return driver


def open_and_prepare_page(driver, from_date: str, to_date: str) -> str:
    """
    Open Rajasthan HC website, fill dates, select 'Reportable Judgement',
    and screenshot captcha. Returns captcha image path for user input.
    """
    url = 'https://hcraj.nic.in/cishcraj-jdp/JudgementFilters/'
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    time.sleep(2)

    # Fill 'From Date'
    from_date_input = wait.until(EC.presence_of_element_located((By.ID, "partyFromDate")))
    from_date_input.clear()
    from_date_input.send_keys(from_date)
    from_date_input.send_keys(Keys.ENTER)

    # Fill 'To Date'
    to_date_input = wait.until(EC.presence_of_element_located((By.ID, "partyToDate")))
    to_date_input.clear()
    to_date_input.send_keys(to_date)
    to_date_input.send_keys(Keys.ENTER)

    # Select 'Reportable Judgement'
    reportable_judgement = wait.until(EC.presence_of_element_located((By.ID, "rpjudgeA")))
    reportable_judgement.click()

    # Capture captcha image
    captcha_img = wait.until(EC.presence_of_element_located((By.ID, "captcha")))
    captcha_path = "captcha.png"
    captcha_img.screenshot(captcha_path)
    print(f"Captcha saved as {captcha_path}")

    return captcha_path


def submit_captcha_and_search(driver, captcha_text: str):
    """
    Takes user-provided captcha text, enters it, and clicks the search button.
    """
    wait = WebDriverWait(driver, 60)
    
    captcha_input = wait.until(EC.presence_of_element_located((By.ID, "txtCaptcha")))
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)

    search_button = wait.until(EC.presence_of_element_located((By.ID, "btncasedetail1_1")))
    search_button.click()
    print("Submitted captcha and clicked search.")


# ---- Function 3: Scrape judgments ----
def scrape_results_table(driver, pdfs_dir = "pdfs", seen_ids = seen_ids) -> List[Dict]:
    """ 
    Scrape all rows from the results table.
    Returns a list of dicts with case details.
    """
    wait = WebDriverWait(driver, 60)
    os.makedirs(pdfs_dir, exist_ok=True)
    scraped_data = []
    if seen_ids is None:
        seen_ids = set()

    while True:
        try:
            # Wait for table
            table = wait.until(EC.presence_of_element_located((By.ID, "sample_1")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

            for row in rows:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                buttons = row.find_elements(By.CSS_SELECTOR, "button.btn.btn-sm.blue.tooltips")

                if buttons and len(buttons) > 1 :
                    case_no = buttons[1].get_attribute("data-caseno")
                    order_no = buttons[1].get_attribute("data-orderno")
                    year = buttons[1].get_attribute("data-cyear")
                    unique_id = f"{case_no}_{order_no}_{year}"

                    if unique_id not in seen_ids:
                        seen_ids.add(unique_id)
                        scraped_data.append({
                            "serial_no": cells[0].text,
                            "case_details": cells[1].text,
                            "judge_name": cells[2].text,
                            "order_date": cells[3].text,
                            "pdf_id": unique_id
                        })
                        buttons[1].click()
                        time.sleep(1) 
                else:
                    print(f"No PDF button found for case: {cells[1].text}")

        except Exception as e:
            print("No table found or error while scraping:", e)
            break

        # Try clicking next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "#sample_1_paginate ul li a i.fa-angle-right")
            next_btn.click()
            time.sleep(1)
        except:
            print("No more pages.")
            break

    print(f"Scraped {len(scraped_data)} rows.")
    return scraped_data


# ---- Function 4: Download PDFs ----


# ---- Function 5: Save CSV ----
def save_data_to_csv(data: List[Dict], logs_dir: str = "logs") -> str:
    """
    Save scraped data to CSV in logs folder.
    Returns the path to the saved CSV, or an empty string if no data.
    """
    if not data:
        print("No data to save. Skipping CSV creation.")
        return ""

    os.makedirs(logs_dir, exist_ok=True)
    scrape_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = f"judgments_{scrape_date}.csv"
    csv_path = os.path.join(logs_dir, csv_filename)

    # Add scrape_date to each row
    for row in data:
        row["scrape_date"] = scrape_date

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"CSV saved at {csv_path}")
    return csv_path

