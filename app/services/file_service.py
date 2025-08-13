"""
File Service - Handle file operations and validation
"""

import os
import csv
import io
import hashlib
import logging
from typing import List, Dict, Any, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Response, current_app

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file operations"""

    def __init__(self):
        self.allowed_extensions = {"csv", "xlsx", "xls"}

    def save_uploaded_file(self, file: FileStorage) -> str:
        """
        Save uploaded file securely

        Args:
            file: Uploaded file object

        Returns:
            Path to saved file

        Raises:
            ValueError: If file is invalid
        """
        if not file or not file.filename:
            raise ValueError("No file provided")

        if not self._is_allowed_file(file.filename):
            raise ValueError(f"Invalid file type. Allowed: {self.allowed_extensions}")

        filename = secure_filename(file.filename)

        # Add timestamp to avoid conflicts
        import time

        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"

        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        try:
            file.save(file_path)

            # Validate file size
            if os.path.getsize(file_path) == 0:
                os.remove(file_path)
                raise ValueError("Empty file uploaded")

            logger.info(f"File saved successfully: {filename}")
            return file_path

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Failed to save file: {str(e)}")

    def cleanup_file(self, file_path: str) -> None:
        """Safely remove file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

    def load_stores_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load stores from CSV or Excel file

        Args:
            file_path: Path to the file

        Returns:
            List of store dictionaries
        """
        try:
            if file_path.endswith(".csv"):
                return self._load_csv_file(file_path)
            elif file_path.endswith((".xlsx", ".xls")):
                return self._load_excel_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")

        except Exception as e:
            logger.error(f"Error loading stores from file {file_path}: {str(e)}")
            raise

    def load_playbook_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load playbook from CSV file

        Args:
            file_path: Path to the playbook file

        Returns:
            Dictionary of playbook constraints
        """
        try:
            playbook = {}

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chain = row.get("chain")
                    if chain:
                        playbook[chain] = {k: v for k, v in row.items() if k != "chain"}

            logger.info(f"Loaded playbook with {len(playbook)} chain rules")
            return playbook

        except Exception as e:
            logger.error(f"Error loading playbook from file {file_path}: {str(e)}")
            raise

    def validate_file_content(self, file_path: str) -> bool:
        """
        Validate that file has required structure

        Args:
            file_path: Path to the file

        Returns:
            True if valid, False otherwise
        """
        try:
            stores = self.load_stores_from_file(file_path)

            if not stores:
                logger.warning("File contains no data")
                return False

            # Check for required fields (flexible naming)
            first_store = stores[0]
            name_fields = ["name", "store_name", "store name", "storename"]

            has_name = any(
                key.lower().replace(" ", "_") in name_fields
                for key in first_store.keys()
            )

            if not has_name:
                logger.warning("File missing required 'name' field")
                return False

            logger.info(f"File validation passed: {len(stores)} stores found")
            return True

        except Exception as e:
            logger.error(f"Error validating file content: {str(e)}")
            return False

    def export_route_to_csv(self, route: List[Dict[str, Any]]) -> Response:
        """
        Export route to CSV format

        Args:
            route: List of route stops

        Returns:
            Flask Response with CSV data
        """
        try:
            output = io.StringIO()

            if route:
                # Get all possible fieldnames from all stores
                fieldnames = set()
                for store in route:
                    fieldnames.update(store.keys())

                fieldnames = sorted(list(fieldnames))

                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(route)
            else:
                output.write("No route data available\n")

            output.seek(0)

            logger.info(f"Exported route with {len(route) if route else 0} stops")

            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={
                    "Content-Disposition": "attachment;filename=optimized_route.csv"
                },
            )

        except Exception as e:
            logger.error(f"Error exporting route to CSV: {str(e)}")
            raise

    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file for caching

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash string
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()

        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            return ""

    def process_stores_file(self, file: FileStorage) -> List[Dict[str, Any]]:
        """
        Process uploaded stores file and return list of stores

        Args:
            file: Uploaded file storage object

        Returns:
            List of store dictionaries

        Raises:
            ValueError: If file processing fails
        """
        if not file or not file.filename:
            raise ValueError("No file provided")

        if not self._is_allowed_file(file.filename):
            raise ValueError(f"Invalid file type. Allowed: {self.allowed_extensions}")

        try:
            # Read file content
            file_content = file.read().decode("utf-8")
            file.seek(0)  # Reset file pointer for potential reuse

            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(file_content))
            stores = []

            for row in csv_reader:
                # Clean up row data
                clean_row = {}
                for key, value in row.items():
                    if key and value:
                        clean_row[key.strip()] = value.strip()

                if clean_row:  # Only add non-empty rows
                    stores.append(clean_row)

            logger.info(f"Processed {len(stores)} stores from file {file.filename}")
            return stores

        except Exception as e:
            logger.error(f"Error processing stores file: {str(e)}")
            raise ValueError(f"Failed to process stores file: {str(e)}")

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def _load_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                stores = list(reader)

            logger.info(f"Loaded {len(stores)} stores from CSV file")
            return stores

        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise

    def _load_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from Excel file"""
        try:
            import pandas as pd

            engine = "openpyxl" if file_path.endswith(".xlsx") else "xlrd"
            df = pd.read_excel(file_path, engine=engine)

            # Convert to list of dictionaries
            stores = df.to_dict("records")

            # Clean up NaN values
            for store in stores:
                for key, value in store.items():
                    if pd.isna(value):
                        store[key] = None

            logger.info(f"Loaded {len(stores)} stores from Excel file")
            return stores

        except ImportError:
            logger.error("pandas or openpyxl not installed for Excel support")
            raise ValueError("Excel file support requires pandas and openpyxl packages")
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise
