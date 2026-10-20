"""
B3 portal navigation and filter management service using Playwright.
Handles URL navigation, pagination filters, and DOM readiness.
"""
from typing import Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

class B3Navigator:
    """Manages navigation, interaction and page preparation on B3 listed index portal."""

    BASE_URL = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
    TABLE_SELECTOR = "table"
    SELECT_PAGE_SELECTOR = "#selectPage"
    ROWS_SELECTOR = "table tbody tr"

    def __init__(self, page: Page, url: Optional[str] = None) -> None:
        self.page = page
        self.url = url or self.BASE_URL

    def navigate_to_index_page(self) -> None:
        """Navigates to the B3 index page and waits for the initial table to load."""
        print(f"[INFO] [B3Navigator] Navigating to: {self.url}")
        self.page.goto(self.url, wait_until="domcontentloaded")
        self.page.wait_for_selector(self.TABLE_SELECTOR, timeout=30000)
        print("[INFO] [B3Navigator] Page and initial table loaded successfully.")

    def select_maximum_items_per_page(self) -> int:
        """
        Dynamically detects all pagination options, selects the highest numeric value,
        and waits until the table refreshes with all rows.
        Returns the total number of rows loaded.
        """
        self.page.wait_for_selector(self.SELECT_PAGE_SELECTOR, timeout=30000)

        # Capture the text of all options in the select
        options_texts = self.page.locator(f"{self.SELECT_PAGE_SELECTOR} option").all_inner_texts()
        
        # Convert to integers only what is number (filtering texts like 'Select')
        numeric_options = [int(opt.strip()) for opt in options_texts if opt.strip().isdigit()]
        
        # Discover the maximum value dynamically (with fallback to 120 for security)
        max_option = str(max(numeric_options)) if numeric_options else "120"
        print(f"[INFO] [B3Navigator] Available pagination options: {numeric_options}. Auto-selected maximum: '{max_option}'")

        # Select the maximum option detected
        self.page.select_option(self.SELECT_PAGE_SELECTOR, value=max_option)

        # Wait for the asynchronous table synchronization
        self.page.wait_for_function("() => document.querySelectorAll('table tbody tr').length > 20", timeout=15000)
        rows_count = self.page.locator(self.ROWS_SELECTOR).count()
        return rows_count

    