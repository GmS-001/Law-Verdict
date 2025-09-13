# src/scraper.py
import os
from typing import List, Dict
from datetime import datetime, timedelta

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
    """Set up Selenium Chrome driver with PDF download preferences."""
    # We'll add Selenium setup here later
    pass


# ---- Function 3: Scrape judgments ----
def scrape_judgments(driver, from_date: str, to_date: str, option: str) -> List[Dict]:
    """
    Scrape judgment data between from_date and to_date based on the selected option.
    Returns a list of dicts with scraped data.
    """
    # We'll add scraping logic here later
    pass


# ---- Function 4: Download PDFs ----
def download_pdfs(data: List[Dict], pdf_dir: str):
    """Download PDFs based on scraped data."""
    # We'll add PDF download logic later
    pass


# ---- Function 5: Save CSV ----
def save_data_to_csv(data: List[Dict], csv_path: str):
    """Save scraped data to a CSV file."""
    # We'll add CSV saving logic later
    pass
