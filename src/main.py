"""
Entry point for the RPA Data Extractor robot.
Extracts market data and index theoretical portfolios from B3.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.browser import BrowserManager
from src.services.b3_navigator import B3Navigator
from src.services.b3_extractor import B3TableExtractor
from src.services.data_cleaner import B3DataCleaner
from src.services.market_analyzer import MarketAnalyzer
from src.services.excel_reporter import B3ExcelReporter
from src.services.pdf_reporter import B3PdfReporter

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")
    
    print("[INFO] Starting end-to-end B3 RPA pipeline...")
    with BrowserManager() as page:
        # 1. Navigation and page preparation
        navigator = B3Navigator(page)
        navigator.navigate_to_index_page()
        total_rows = navigator.select_maximum_items_per_page()
        print(f"[SUCCESS] Table ready with {total_rows} elements.")

        # 2. Tabular data extraction from live DOM
        extractor = B3TableExtractor(page)
        records = extractor.extract_records()
        print(f"[SUCCESS] Extracted {len(records)} raw records from DOM.")

        # 3. Data engineering and financial sanitization
        print("\n[INFO] Starting data cleaning and financial metrics computation...")
        cleaner = B3DataCleaner()
        df_clean = cleaner.clean_records(records)
        metrics = cleaner.get_summary_metrics(df_clean)

        # 4. Market analytics and concentration intelligence
        print("[INFO] Running market analysis and concentration intelligence...")
        analyzer = MarketAnalyzer()
        enriched_df = analyzer.enrich_with_analytics(df_clean)
        type_distribution = analyzer.get_share_type_distribution(enriched_df)
        csv_file = analyzer.export_to_csv(enriched_df)

        # 5. Corporate Excel report generation (.xlsx)
        print("[INFO] Generating corporate Excel executive report...")
        excel_reporter = B3ExcelReporter()
        excel_file = excel_reporter.generate_report(enriched_df, metrics)

        # 6. Executive PDF briefing generation (.pdf)
        print("[INFO] Generating executive PDF briefing...")
        pdf_reporter = B3PdfReporter(page)
        pdf_file = pdf_reporter.generate_report(enriched_df, metrics, type_distribution)

    # 7. Publish visual summary to GitHub Actions if running in CI/CD
    publish_github_summary(metrics, enriched_df, type_distribution)

    print("\n=================================================================")
    print("           B3 IBOVESPA RPA EXTRACTION SUMMARY                   ")
    print("=================================================================")
    print(f"Total Assets Processed: {metrics.get('total_assets')}")
    print(f"Total Theoretical Shares: {metrics.get('total_quantity'):,}".replace(",", "."))
    print(f"Top 5 Concentration: {metrics.get('top_5_share_pct')}%")
    print(f"Top 10 Concentration: {metrics.get('top_10_share_pct')}%")
    print("-----------------------------------------------------------------")
    print(f"[OUTPUT 1] Cleaned CSV Dataset:    {csv_file}")
    print(f"[OUTPUT 2] Styled Excel Report:   {excel_file}")
    print(f"[OUTPUT 3] Executive PDF Report:  {pdf_file}")
    print("=================================================================\n")
    print("[INFO] Robot execution finished cleanly.")

def publish_github_summary(
    metrics: Dict[str, Any],
    df: pd.DataFrame,
    type_distribution: pd.DataFrame,
) -> None:
    """Publishes an executive Markdown summary to $GITHUB_STEP_SUMMARY when executing in GitHub Actions."""
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    top_10 = df.head(10)
    top_10_rows = "\n".join(
        f"| {row['Posição']} | `{row['Código']}` | {row['Ação']} | {row['Classe Ação']} | {row['Part. (%)']:.3f}% | {row['Part. Acumulada (%)']:.3f}% | {row['Classificação']} |"
        for _, row in top_10.iterrows()
    )

    dist_rows = "\n".join(
        f"| **{row['Classe Ação']}** | {row['Quantidade_Ativos']} | {row['Participacao_Total_Pct']:.3f}% |"
        for _, row in type_distribution.iterrows()
    ) if not type_distribution.empty else ""

    total_shares = f"{metrics.get('total_quantity', 0):,}".replace(",", ".")

    markdown = f"""# B3 Ibovespa - Relatório Executivo RPA

> Extração automatizada da Carteira Teórica do Índice Ibovespa diretamente dos sistemas oficiais da B3.

## Indicadores Chave de Mercado (KPIs)

| Indicador | Valor |
|:---|---:|
| **Total de Ativos na Carteira** | **{metrics.get('total_assets', 0)}** |
| **Volume Total de Ações Teóricas** | **{total_shares}** |
| **Concentração Top 5 Maiores Ações** | **{metrics.get('top_5_share_pct', 0.0):.2f}%** |
| **Concentração Top 10 Maiores Ações** | **{metrics.get('top_10_share_pct', 0.0):.2f}%** |

## Top 10 Maiores Ações por Participação

| Pos | Código | Ação | Classe | Part. (%) | Acumulado (%) | Classificação |
|:---:|:---:|:---|:---:|---:|---:|:---:|
{top_10_rows}

## Distribuição da Carteira por Classe de Ações

| Classe de Ação | Quantidade de Ativos | Participação Total (%) |
|:---|:---:|---:|
{dist_rows}

---
*Relatório gerado automaticamente por robô RPA em Python • Artefatos disponíveis para download na seção Artifacts.*
"""
    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(markdown)
        print("[SUCCESS] Published executive summary to GITHUB_STEP_SUMMARY.")
    except Exception as exc:
        print(f"[WARN] Failed to write GITHUB_STEP_SUMMARY: {exc}")

if __name__ == "__main__":
    main()

