"""
Entry point for the RPA Data Extractor robot.
Extracts market data and index theoretical portfolios from B3.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.browser import BrowserManager
from src.services.b3_navigator import B3Navigator
from src.services.b3_extractor import B3TableExtractor

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")
    
    print("[INFO] Starting B3 extraction workflow...")
    with BrowserManager() as page:
        # Navigation and syncronization
        navigator = B3Navigator(page)
        navigator.navigate_to_index_page()
        total_rows = navigator.select_maximum_items_per_page()
        print(f"[SUCCESS] Table ready with {total_rows} elements.")

        # Table extraction
        extractor = B3TableExtractor(page)
        records = extractor.extract_records()
        
        # Display sample data
        if records:
            print("\n--- FIRST EXTRACTED ASSET SAMPLE ---")
            print(records[0])
            print("--- LAST EXTRACTED ASSET SAMPLE ---")
            print(records[-1])
            print(f"-----------------------------------------\n")
            print(f"[SUCCESS] Extraction completed. Total valid records: {len(records)}")
        else:
            print("[WARNING] No records extracted.")
    
    print("[INFO] Robot execution finished cleanly.")

if __name__ == "__main__":
    main()
