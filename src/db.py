# src/db.py
import sqlite3
from datetime import datetime
from typing import List, Dict

DB_FILE = "logs/data.db"

def init_db(db_file=DB_FILE):
    """Initialize the database and create table if not exists."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_pdfs (
            pdf_id TEXT PRIMARY KEY,
            serial_no TEXT,
            case_details TEXT,
            judge_name TEXT,
            order_date TEXT,
            scrape_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_seen_ids_db(db_file=DB_FILE) -> set:
    """Return a set of all pdf_ids stored in the DB."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_id FROM scraped_pdfs")
    rows = cursor.fetchall()
    conn.close()
    return set(r[0] for r in rows)

def save_scraped_data_db(new_data: List[Dict], db_file=DB_FILE):
    """Insert new scraped rows into DB."""
    if not new_data:
        print("No new data to save.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    for row in new_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO scraped_pdfs 
                (pdf_id, serial_no, case_details, judge_name, order_date, pdf_file, scrape_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["pdf_id"], row["serial_no"], row["case_details"], 
                row["judge_name"], row["order_date"], row.get("pdf_file", ""), 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        except Exception as e:
            print(f"Error inserting {row['pdf_id']}: {e}")
    conn.commit()
    conn.close()
    print(f"Saved {len(new_data)} new rows to DB.")
