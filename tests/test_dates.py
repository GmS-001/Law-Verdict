# tests/test_download_pdfs.py
from src.scraper import download_pdfs

if __name__ == "__main__":
    test_data = [
        {"pdf_id": "3334_1_2016"},  # Replace with a real ID from scraped data
    ]
    download_pdfs(test_data)
    print("Test completed.")
