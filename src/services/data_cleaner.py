"""
Data cleaning and financial parsing service using Pandas.
Converts pt-BR string formatting to numeric data types and computes summary metrics.
"""
from typing import List, Dict, Any
import pandas as pd

class B3DataCleaner:
    """Cleans, parses, and enriches market data records extracted from B3."""

    def clean_records(self, records: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Transforms raw string records into a typed and sorted Pandas DataFrame.
        Converts Brazilian currency/number conventions to native int/float types.
        """
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Clean whitespace in text columns
        text_cols = ["Código", "Ação", "Tipo"]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Convert "Qtde. Teórica" (Theoretical Quantity) from string with thousands separators to integer.
        if "Qtde. Teórica" in df.columns:
            df["Qtde. Teórica"] = df["Qtde. Teórica"].astype(str).str.replace(".", "", regex=False)
            df["Qtde. Teórica"] = pd.to_numeric(df["Qtde. Teórica"], errors="coerce").fillna(0).astype("int64")

        # Convert "Part. (%)" (Participation Percentage) from string with comma decimal separator to float.
        if "Part. (%)" in df.columns:
            df["Part. (%)"] = df["Part. (%)"].astype(str).str.replace(",", ".", regex=False)
            df["Part. (%)"] = pd.to_numeric(df["Part. (%)"], errors="coerce").fillna(0.0).astype(float)
            # Create decimal fraction for financial and accounting calculations
            df["Part. Decimal"] = (df["Part. (%)"] / 100.0).round(6)

        # Sort in descending order of participation (largest weights first)
        if "Part. (%)" in df.columns:
            df = df.sort_values(by="Part. (%)", ascending=False).reset_index(drop=True)

        return df

    def get_summary_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates executive summary metrics from the cleaned DataFrame."""
        if df.empty:
            return {}

        total_assets = len(df)
        total_quantity = int(df["Qtde. Teórica"].sum()) if "Qtde. Teórica" in df.columns else 0
        total_share = round(float(df["Part. (%)"].sum()), 4) if "Part. (%)" in df.columns else 0.0
        top_5_share = round(float(df.head(5)["Part. (%)"].sum()), 4) if "Part. (%)" in df.columns else 0.0
        top_10_share = round(float(df.head(10)["Part. (%)"].sum()), 4) if "Part. (%)" in df.columns else 0.0

        return {
            "total_assets": total_assets,
            "total_quantity": total_quantity,
            "total_share_pct": total_share,
            "top_5_share_pct": top_5_share,
            "top_10_share_pct": top_10_share,
        }
