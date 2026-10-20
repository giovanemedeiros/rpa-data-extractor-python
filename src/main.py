"""
Entry point for the RPA Data Extractor robot.
Extracts market data and index theoretical portfolios from B3.
"""
import sys
from pathlib import Path

# Add root to sys.path to allow direct file execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.browser import BrowserManager

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")
    
    print("[INFO] Validating Playwright BrowserManager lifecycle...")
    with BrowserManager() as page:
        page.goto("https://www.google.com")
        title = page.title()
        print(f"[SUCCESS] Page navigated successfully. Title: '{title}'")
        print(f"[INFO] Viewport size: {page.viewport_size}")
    
    print("[INFO] BrowserManager teardown completed successfully.")

if __name__ == "__main__":
    main()
