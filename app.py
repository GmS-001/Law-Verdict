import streamlit as st
from datetime import datetime
from src.scraper import (
    get_date_10_days_before,
    open_and_prepare_page,
    scrape_results_table,
    setup_selenium,
    submit_captcha_and_search,
    save_data_to_csv
)
from src.db import init_db, load_seen_ids_db, save_scraped_data_db
import os

st.set_page_config(page_title="Law & Verdict Scraper")
st.title("📄 Law & Verdict PDF Scraper")
PDF_DIR = "PDFs"
CSV_DIR = "CSVs"
# --- Initialize DB and Session State ---
init_db()
if 'stage' not in st.session_state:
    st.session_state.stage = 'initial'
if 'driver' not in st.session_state:
    st.session_state.driver = None
if 'captcha_path' not in st.session_state:
    st.session_state.captcha_path = None

# --- UI LOGIC BASED ON STAGE ---

if st.session_state.stage == 'initial':
    to_date = st.date_input("Select Date", value=datetime.today())
    from_date = get_date_10_days_before(to_date.strftime("%d/%m/%Y"))
    st.info(f"Scraping from **{from_date}** to **{to_date.strftime('%d/%m/%Y')}**")
    option = st.radio("Reportable Judgment", ["Yes", "No", "All"])
    if st.button("Go to Website and Get CAPTCHA"):
        with st.spinner("Opening website..."):
            st.session_state.driver = setup_selenium(download_dir=PDF_DIR)
            st.session_state.captcha_path = open_and_prepare_page(
                st.session_state.driver, from_date, to_date.strftime("%d/%m/%Y")
            )
            st.session_state.stage = 'captcha_input'
            st.rerun()

elif st.session_state.stage == 'captcha_input':
    st.image(st.session_state.captcha_path, caption="Enter CAPTCHA shown in the browser")
    
    with st.form("captcha_form"):
        captcha_text = st.text_input("Enter CAPTCHA text")
        submit_button = st.form_submit_button("Extract Judgments")

        if submit_button:
            with st.spinner("Submitting CAPTCHA and scraping... This may take a moment."):
                seen_ids = load_seen_ids_db()
                submit_captcha_and_search(st.session_state.driver, captcha_text)
                scraped_data = scrape_results_table(st.session_state.driver, pdfs_dir=PDF_DIR, seen_ids=seen_ids)
                
                if scraped_data:
                    st.info("Data scraped. Saving to files...")
                    save_scraped_data_db(scraped_data)
                    save_data_to_csv(scraped_data,csv_dir=CSV_DIR)
                    st.success(f"Scraping complete! {len(scraped_data)} new rows added.")
                    st.dataframe(scraped_data)
                else:
                    st.warning("No new data found to scrape.")

                # --- Cleanup ---
                st.session_state.driver.quit()
                st.session_state.driver = None
                st.session_state.captcha_path = None
                st.session_state.stage = 'initial' # Reset for next run
                # Keep the success message by not immediately rerunning, or store results in state
    
    if st.button("Start Over"):
        # Cleanup and reset
        if st.session_state.driver:
            st.session_state.driver.quit()
        st.session_state.stage = 'initial'
        st.session_state.driver = None
        st.session_state.captcha_path = None
        st.rerun()