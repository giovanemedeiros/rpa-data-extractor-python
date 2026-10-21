"""
B3 tabular data extractor using Playwright.
Extracts column headers, row records, and validates tabular integrity.
"""
from typing import List, Dict
from playwright.sync_api import Page

class B3TableExtractor:
    """Extracts tabular market composition data from B3 index page."""

    HEADER_SELECTOR = "table thead tr th"
    ROWS_SELECTOR = "table tbody tr"

    def __init__(self, page: Page) -> None:
        self.page = page

    def get_headers(self) -> List[str]:
        """
        Extracts and cleans column headers from table thead.
        Returns a list of header names (e.g. ['Código', 'Ação', 'Tipo', 'Qtde. Teórica', 'Part. (%)']).
        """
        header_texts = self.page.locator(self.HEADER_SELECTOR).all_inner_texts()
        headers = [header.strip() for header in header_texts if header.strip()]
        return headers

    def extract_records(self) -> List[Dict[str, str]]:
        """
        Extracts all row data and maps each cell to its corresponding column header.
        Filters out totalizer or malformed rows.
        Returns a list of dictionaries with raw string values.
        """
        headers = self.get_headers()
        print(f"[INFO] [B3TableExtractor] Detected table headers: {headers}")

        # Extração em alta performance via evaluate no JavaScript do navegador:
        raw_rows: List[List[str]] = self.page.evaluate(
            """
            () => {
                const rows = Array.from(document.querySelectorAll('table tbody tr'));
                return rows.map(tr => 
                    Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
                );
            }
            """
        )

        records: List[Dict[str, str]] = []
        for row_cells in raw_rows:
            if len(row_cells) == len(headers):
                record = dict(zip(headers, row_cells))
                records.append(record)
        
        print(f"[INFO] [B3TableExtractor] Extracted {len(records)} valid records.")
        return records
