"""
Market analysis and financial enrichment service using Pandas.
Calculates cumulative concentration, share-type distribution, and exports sanitized CSV datasets.
"""
from pathlib import Path
from typing import Dict, Any
import pandas as pd

class MarketAnalyzer:
    """Enriches market data with analytical classifications and computes market intelligence metrics."""

    @staticmethod
    def _classify_weight(part: float) -> str:
        """Categorizes an asset based on its index weight percentage."""
        if part >= 5.0:
            return "Mega Cap (> 5%)"
        elif part >= 2.0:
            return "Large Cap (2% - 5%)"
        elif part >= 1.0:
            return "Mid Cap (1% - 2%)"
        return "Small Cap (< 1%)"

    @staticmethod
    def _classify_share_type(tipo: str) -> str:
        """Normalizes B3 share types into standard categories: ON, PN, or UNT."""
        tipo_upper = str(tipo).upper()
        if "ON" in tipo_upper:
            return "Ordinária (ON)"
        elif "PN" in tipo_upper:
            return "Preferencial (PN)"
        elif "UNT" in tipo_upper or "11" in tipo_upper:
            return "Unit (UNT)"
        return "Outro"

    def enrich_with_analytics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds ranking, cumulative concentration %, weight tiers, and share class categories."""
        if df.empty:
            return df

        # Add a 'Position' column from 1 to the total number of rows: range(1, len(enriched_df) + 1)
        enriched_df = df.copy()
        enriched_df["Posição"] = range(1, len(enriched_df) + 1)

        # Add the cumulative sum of 'Part. (%)' using .cumsum().round(4) to the 'Part. Acumulada (%)' column
        enriched_df["Part. Acumulada (%)"] = enriched_df["Part. (%)"].cumsum().round(4)

        # Apply self._classify_weight to the 'Part. (%)' column to generate 'Classificação'
        enriched_df["Classificação"] = enriched_df["Part. (%)"].apply(self._classify_weight)

        # Apply self._classify_share_type to the 'Tipo' column to generate 'Classe Ação'
        enriched_df["Classe Ação"] = enriched_df["Tipo"].apply(self._classify_share_type)
        
        # Reorder the columns in the desired order
        columns_order = [
            "Posição",
            "Código",
            "Ação",
            "Tipo",
            "Classe Ação",
            "Part. (%)",
            "Part. Acumulada (%)",
            "Classificação",
            "Qtde. Teórica",
        ]
        enriched_df = enriched_df[columns_order]

        return enriched_df

    def get_share_type_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """Groups index composition by share type (ON vs PN vs UNT)."""
        if df.empty or "Classe Ação" not in df.columns:
            return pd.DataFrame()

        dist = (
            df.groupby("Classe Ação", as_index=False)
            .agg(
                Quantidade_Ativos=("Código", "count"),
                Participacao_Total_Pct=("Part. (%)", "sum"),
            )
            .sort_values(by="Participacao_Total_Pct", ascending=False)
            .reset_index(drop=True)
        )
        dist["Participacao_Total_Pct"] = dist["Participacao_Total_Pct"].round(3)
        return dist

    def export_to_csv(self, df: pd.DataFrame, output_path: str = "output/b3_ibovespa_composicao.csv") -> str:
        """Exports the enriched DataFrame to a clean CSV file using UTF-8 BOM encoding and pt-BR conventions."""

        # Ensure the destination folder exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save the DataFrame to a CSV file
        df.to_csv(output_path, index=False, sep=";", decimal=",", encoding="utf-8-sig")
        
        # Return the output_path
        return output_path
