"""
Executive PDF briefing generator using Playwright browser rendering engine.
Generates an A4 corporate one-page briefing with KPI cards and Top 10 asset table.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from playwright.sync_api import Page

class B3PdfReporter:
    """Renders styled HTML templates into executive PDF reports via Playwright."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def generate_report(
        self,
        df: pd.DataFrame,
        metrics: Dict[str, Any],
        type_distribution: pd.DataFrame,
        output_path: str = "output/b3_ibovespa_relatorio_executivo.pdf",
    ) -> str:
        """Renders styled executive briefing and exports to PDF."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        today_str = datetime.now().strftime("%d/%m/%Y")
        total_qty_formatted = f"{metrics.get('total_quantity', 0):,}".replace(",", ".")

        top_10_df = df.head(10)

        # Build table rows HTML for Top 10
        table_rows_html = ""
        for _, row in top_10_df.iterrows():
            table_rows_html += f"""
            <tr>
                <td style="text-align: center; font-weight: bold;">{row['Posição']}</td>
                <td style="text-align: center; font-weight: bold; color: #002060;">{row['Código']}</td>
                <td>{row['Ação']}</td>
                <td style="text-align: center;">{row['Classe Ação']}</td>
                <td style="text-align: right; font-weight: bold;">{row['Part. (%)']:.3f}%</td>
                <td style="text-align: right;">{row['Part. Acumulada (%)']:.3f}%</td>
                <td style="text-align: center;"><span class="badge">{row['Classificação']}</span></td>
            </tr>
            """

        # Build table rows HTML for share class distribution
        type_rows_html = ""
        if not type_distribution.empty:
            for _, row in type_distribution.iterrows():
                type_rows_html += f"""
                <tr>
                    <td style="font-weight: 600;">{row['Classe Ação']}</td>
                    <td style="text-align: center;">{row['Quantidade_Ativos']}</td>
                    <td style="text-align: right; font-weight: bold; color: #002060;">{row['Participacao_Total_Pct']:.3f}%</td>
                </tr>
                """

        # HTML and CSS corporate template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                    margin: 0;
                    padding: 24px;
                    color: #1a1a1a;
                    font-size: 11px;
                }}
                .header {{
                    border-bottom: 3px solid #002060;
                    padding-bottom: 12px;
                    margin-bottom: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                }}
                .title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #002060;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 11px;
                    color: #595959;
                    margin-top: 4px;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 12px;
                    margin-bottom: 24px;
                }}
                .kpi-card {{
                    background: #F2F4F8;
                    border-left: 4px solid #002060;
                    padding: 10px 14px;
                    border-radius: 4px;
                }}
                .kpi-label {{
                    font-size: 9px;
                    font-weight: bold;
                    color: #595959;
                    text-transform: uppercase;
                }}
                .kpi-value {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #002060;
                    margin-top: 4px;
                }}
                .section-title {{
                    font-size: 13px;
                    font-weight: bold;
                    color: #002060;
                    margin-bottom: 8px;
                    border-left: 3px solid #002060;
                    padding-left: 8px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th {{
                    background-color: #002060;
                    color: #ffffff;
                    text-align: left;
                    padding: 6px 8px;
                    font-size: 10px;
                    font-weight: 600;
                }}
                td {{
                    padding: 5px 8px;
                    border-bottom: 1px solid #E0E0E0;
                    font-size: 10px;
                }}
                tr:nth-child(even) {{
                    background-color: #FAFAFA;
                }}
                .badge {{
                    background: #E8EEF8;
                    color: #002060;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: 600;
                }}
                .footer {{
                    margin-top: 24px;
                    padding-top: 8px;
                    border-top: 1px solid #E0E0E0;
                    font-size: 9px;
                    color: #8C8C8C;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h1 class="title">B3 - RELATÓRIO EXECUTIVO</h1>
                    <div class="subtitle">Carteira Teórica e Inteligência de Concentração do Índice Ibovespa</div>
                </div>
                <div style="text-align: right; color: #595959; font-size: 10px;">
                    Data de Referência: <strong>{today_str}</strong>
                </div>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Total de Ativos</div>
                    <div class="kpi-value">{metrics.get('total_assets', 0)}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Volume Total de Ações</div>
                    <div class="kpi-value">{total_qty_formatted}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Top 5 Concentração</div>
                    <div class="kpi-value">{metrics.get('top_5_share_pct', 0.0):.2f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Top 10 Concentração</div>
                    <div class="kpi-value">{metrics.get('top_10_share_pct', 0.0):.2f}%</div>
                </div>
            </div>

            <div class="section-title">Top 10 Maiores Ações por Participação de Mercado</div>
            <table>
                <thead>
                    <tr>
                        <th style="text-align: center;">Pos</th>
                        <th style="text-align: center;">Código</th>
                        <th>Ação</th>
                        <th style="text-align: center;">Classe</th>
                        <th style="text-align: right;">Part. (%)</th>
                        <th style="text-align: right;">Acumulado (%)</th>
                        <th style="text-align: center;">Classificação</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>

            <div class="section-title">Distribuição da Carteira por Classe de Ações</div>
            <table>
                <thead>
                    <tr>
                        <th>Classe de Ação</th>
                        <th style="text-align: center;">Quantidade de Ativos</th>
                        <th style="text-align: right;">Participação Total (%)</th>
                    </tr>
                </thead>
                <tbody>
                    {type_rows_html}
                </tbody>
            </table>

            <div class="footer">
                Relatório gerado automaticamente por robô RPA em Python • Dados extraídos oficialmente de sistemaswebb3-listados.b3.com.br
            </div>
        </body>
        </html>
        """

        # Load HTML content in page and print to PDF
        self.page.set_content(html_content, wait_until="load")
        self.page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
        )
        print(f"[SUCCESS] [B3PdfReporter] Executive PDF report generated: {output_path}")
        return output_path
