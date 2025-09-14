import streamlit as st
from datetime import datetime
from src.scraper import (
    get_date_10_days_before,
    scrape_results_table,
    setup_selenium,
    submit_captcha_and_search
)
from src.db import init_db, load_seen_ids_db, save_scraped_data_db
import time
from PIL import Image

st.set_page_config(page_title="Law & Verdict Scraper")
st.title("📄 Law & Verdict PDF Scraper")

# --- Step 1: Date input ---
from_date = st.date_input("Select From Date", value=datetime.today())

# --- Step 2: Radio button selection ---
option = st.radio("Reportable Judgment", ["Yes", "No", "All"])

if st.button("Go to Website") :
    # Placeholder for CAPTCHA image
    captcha_placeholder = st.empty()
    captcha_input = st.text_input("Enter CAPTCHA", "")

    # --- Step 3: Extract button ---
    if st.button("Extract"):
        if not captcha_input.strip():
            st.error("Please enter the CAPTCHA.")
        else:
            st.info("Scraping started... Please wait.")
            
            # --- Initialize DB and load seen_ids ---
            init_db()
            seen_ids = load_seen_ids_db()

            # --- Calculate 10 days before ---
            to_date = get_date_10_days_before(from_date.strftime("%d/%m/%Y"))

            # --- Open Selenium Chrome driver ---
            driver = setup_selenium(download_dir="pdfs")

            # --- Navigate to page and take captcha screenshot ---
            captcha_file = submit_captcha_and_search(driver, from_date, to_date, option)
            captcha_placeholder.image(captcha_file, caption="Enter CAPTCHA shown above")

            # Wait a little for user to input captcha
            st.info("Enter the CAPTCHA above and click Extract again.")

            if captcha_input:
                # Submit CAPTCHA input to page
                submit_captcha_and_search(driver, from_date, to_date, option, captcha_input=captcha_input)

                # --- Scrape table and download PDFs incrementally ---
                scraped_data = scrape_results_table(driver, pdfs_dir="pdfs", seen_ids=seen_ids)

                # --- Save scraped data to DB ---
                save_scraped_data_db(scraped_data)

                driver.quit()

                st.success(f"Scraping completed! {len(scraped_data)} new rows added.")
                if scraped_data:
                    st.download_button(
                        label="Download CSV of scraped data",
                        data=open("logs/data.db", "rb").read(),
                        file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                        mime="application/octet-stream"
                    )
                else:
                    st.info("No new data to scrape.")
