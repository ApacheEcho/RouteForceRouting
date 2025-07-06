# File: routing/loader.py
# This script loads store data from a CSV or Excel file and returns a list of stores.
# The file is expected to have columns 'store name' and 'address'.
import argparse
import pandas as pd
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORE_PATH: str = os.path.join(script_dir, "sample_stores.xlsx")

def _read_store_file(filepath: str) -> pd.DataFrame:
    ext = filepath.lower()
    try:
        if ext.endswith('.csv.gz'):
            return pd.read_csv(filepath, compression='gzip')
        elif ext.endswith('.csv'):
            return pd.read_csv(filepath)
        elif ext.endswith(('.xlsx', '.xlsx.gz')):
            kwargs = {'engine': 'openpyxl'}
            if ext.endswith('.gz'):
                kwargs['compression'] = 'gzip'
            return pd.read_excel(filepath, **kwargs)
        elif ext.endswith(('.xls', '.xls.gz')):
            kwargs = {'engine': 'xlrd'}
            if ext.endswith('.gz'):
                kwargs['compression'] = 'gzip'
            return pd.read_excel(filepath, **kwargs)
        else:
            raise ValueError("Unsupported file extension.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")

def load_stores(filepath: str) -> list[dict[str, str]]:
    df = _read_store_file(filepath)

    if 'store name' not in df.columns or 'address' not in df.columns:
        raise ValueError("File must contain 'store name' and 'address' columns.")

    # Use the highly efficient to_dict method instead of iterrows()
    return df.rename(columns={'store name': 'name'}).to_dict(orient='records')

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
            print("Stores loaded successfully:")
            for store in stores:
                print(f"  Name: {store['name']}, Address: {store['address']}")
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            print(f"Error: {e}")