# -----------------------------
# ✅ Module: loader.py
# Status: Complete and tested
# Notes:
# - Supports .csv, .xlsx, .xls, .parquet (gzipped or plain)
# - Validates for 'store name' and 'address'
# - Preview and load functions are clean
# - Unit test in test_loader.py is passing
# Next Step: Move on to routing/core.py
# -----------------------------
# File: routing/loader.py
# This script loads store data from a CSV or Excel file and returns a list of stores.
# The file is expected to have columns 'Store Name' and 'Address'.
import argparse
import pandas as pd
import sys
import os
from typing import List, Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORE_PATH: str = os.path.join(script_dir, "sample_stores.xlsx")

import gzip
from io import BytesIO, TextIOWrapper

def _read_store_file(filepath: str) -> pd.DataFrame:
    ext = filepath.lower()
    is_gzip = ext.endswith('.gz')
    # Remove .gz from the end if present, to get the base extension
    base_ext = ext[:-3] if is_gzip else ext
    try:
        open_fn = gzip.open if is_gzip else open

        with open_fn(filepath, 'rb') as f:
            if base_ext.endswith('.csv'):
                # For gzipped csv, wrap in TextIOWrapper to get text stream
                return pd.read_csv(TextIOWrapper(f)) if is_gzip else pd.read_csv(f)
            elif base_ext.endswith('.xlsx'):
                return pd.read_excel(f, engine='openpyxl')
            elif base_ext.endswith('.xls'):
                return pd.read_excel(f, engine='xlrd')
            elif base_ext.endswith('.parquet'):
                return pd.read_parquet(f)
            else:
                raise ValueError(f"Unsupported file extension: {filepath}")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")

def load_stores(filepath: str) -> List[Dict[str, Any]]:
    """
    Load stores from file and normalize column names.
    
    Args:
        filepath: Path to the store data file
        
    Returns:
        List of store dictionaries with normalized keys
        
    Raises:
        ValueError: If required columns are missing
    """
    df = _read_store_file(filepath)

    # Check for required columns (case-insensitive)
    required_columns = ['store name', 'address']
    df_columns_lower = [col.lower() for col in df.columns]
    
    missing_columns = []
    for req_col in required_columns:
        if req_col not in df_columns_lower:
            missing_columns.append(req_col)
    
    if missing_columns:
        raise ValueError(f"File must contain columns: {', '.join(missing_columns)}. Found: {', '.join(df.columns)}")

    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Use the highly efficient to_dict method instead of iterrows()
    stores = df.rename(columns={'store name': 'name'}).to_dict(orient='records')
    
    # Validate that stores have required fields
    validate_store_rows(stores)
    
    return stores

def validate_store_rows(stores: List[Dict[str, Any]]) -> None:
    for i, store in enumerate(stores):
        if not store.get('name') or not store.get('address'):
            raise ValueError(
                f"Store at row {i+1} is missing required fields: "
                f"name={store.get('name')}, address={store.get('address')}"
            )

def preview_stores(filepath: str) -> None:
    try:
        df = _read_store_file(filepath)
        print(f"\nFile: {os.path.basename(filepath)}")
        print(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print("\nFirst 5 rows:")
        print(df.head().to_string())
    except Exception as e:
        print(f"Error previewing store file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load or preview store data.")
    parser.add_argument(
        "filepath",
        nargs="?",
        default=DEFAULT_STORE_PATH,
        help="Path to the store data file (CSV or Excel).",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Display file metadata and the first 5 rows instead of loading.",
    )
    args = parser.parse_args()

    if args.preview:
        preview_stores(args.filepath)
    else:
        print("Loading stores...")
        try:
            stores = load_stores(args.filepath)
            print(f"Stores loaded successfully: {len(stores)} stores")
            for i, store in enumerate(stores[:5]):  # Show first 5 stores
                print(f"  {i+1}. Name: {store['name']}, Address: {store['address']}")
            if len(stores) > 5:
                print(f"  ... and {len(stores) - 5} more stores")
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            print(f"Error: {e}")