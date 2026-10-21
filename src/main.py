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
from src.services.market_analyzer import MarketAnalyzer

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")
    
    print("[INFO] Starting B3 extraction workflow...")
    with BrowserManager() as page:
        # 1. Navegação e sincronização
        navigator = B3Navigator(page)
        navigator.navigate_to_index_page()
        total_rows = navigator.select_maximum_items_per_page()
        print(f"[SUCCESS] Table ready with {total_rows} elements.")

        # 2. Extração dos dados tabulares
        extractor = B3TableExtractor(page)
        records = extractor.extract_records()
        print(f"[SUCCESS] Extracted {len(records)} raw records from DOM.")

    # 3. Engenharia e Higienização de Dados
    print("\n[INFO] Starting data cleaning and financial metrics computation...")
    cleaner = B3DataCleaner()
    df_clean = cleaner.clean_records(records)
    metrics = cleaner.get_summary_metrics(df_clean)

    # 4. Análise de Mercado e Enriquecimento Analítico
    print("[INFO] Running market analysis and concentration intelligence...")
    analyzer = MarketAnalyzer()
    enriched_df = analyzer.enrich_with_analytics(df_clean)
    type_distribution = analyzer.get_share_type_distribution(enriched_df)
    csv_file = analyzer.export_to_csv(enriched_df)

    print("\n--- TOP 10 MAIORES ATIVOS (COM CLASSIFICAÇÃO E SOMA ACUMULADA) ---")
    print(enriched_df[["Posição", "Código", "Ação", "Classe Ação", "Part. (%)", "Part. Acumulada (%)", "Classificação"]].head(10).to_string(index=False))

    print("\n--- DISTRIBUIÇÃO DO ÍNDICE POR CLASSE DE AÇÃO ---")
    print(type_distribution.to_string(index=False))

    print("\n--- MÉTRICAS EXECUTIVAS DE CARTEIRA ---")
    print(f"Total de Ativos: {metrics.get('total_assets')}")
    print(f"Quantidade Teórica Total de Ações: {metrics.get('total_quantity'):,}".replace(",", "."))
    print(f"Soma Total da Participação: {metrics.get('total_share_pct')}%")
    print(f"Concentração Top 5 Ações: {metrics.get('top_5_share_pct')}%")
    print(f"Concentração Top 10 Ações: {metrics.get('top_10_share_pct')}%")
    print(f"[SUCCESS] Cleaned dataset successfully exported to: {csv_file}")
    print("-----------------------------------------------------------------\n")

    print("[INFO] Robot execution finished cleanly.")

if __name__ == "__main__":
    main()
