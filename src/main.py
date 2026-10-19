"""
Entry point for the RPA Data Extractor robot.
Extracts market data and index theoretical portfolios from B3.
"""
import sys

def main() -> None:
    print("[INFO] [rpa-data-extractor-python] Initialized successfully.")
    print(f"[INFO] Python runtime: {sys.version.split()[0]}")

if __name__ == "__main__":
    main()
