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
from src.services.data_cleaner import B3DataCleaner

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")
    
    print("[INFO] Starting B3 extraction workflow...")
    with BrowserManager() as page:
        # Navigation and synchronization
        navigator = B3Navigator(page)
        navigator.navigate_to_index_page()
        total_rows = navigator.select_maximum_items_per_page()
        print(f"[SUCCESS] Table ready with {total_rows} elements.")

        # Table extraction
        extractor = B3TableExtractor(page)
        records = extractor.extract_records()
        print(f"[SUCCESS] Extracted {len(records)} raw records from DOM.")

    # Data cleaning and engineering
    print("\n[INFO] Starting data cleaning and financial metrics computation...")
    cleaner = B3DataCleaner()
    df = cleaner.clean_records(records)
    metrics = cleaner.get_summary_metrics(df)

    print("\n--- TOP 10 MAIORES PARTICIPAÇÕES NO IBOVESPA ---")
    print(df[["Código", "Ação", "Tipo", "Qtde. Teórica", "Part. (%)"]].head(10).to_string(index=False))
    
    print("\n--- TIPOS DE DADOS SANITIZADOS (PANDAS DTYPES) ---")
    print(df.dtypes)

    print("\n--- MÉTRICAS EXECUTIVAS DE CARTEIRA ---")
    print(f"Total de Ativos: {metrics.get('total_assets')}")
    print(f"Quantidade Teórica Total de Ações: {metrics.get('total_quantity'):,}".replace(",", "."))
    print(f"Soma Total da Participação: {metrics.get('total_share_pct')}%")
    print(f"Concentração Top 5 Ações: {metrics.get('top_5_share_pct')}%")
    print(f"Concentração Top 10 Ações: {metrics.get('top_10_share_pct')}%")
    print("-----------------------------------------\n")

    print("[INFO] Robot execution finished cleanly.")

if __name__ == "__main__":
    main()
