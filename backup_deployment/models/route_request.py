"""
Route Request Model - Data validation and management
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
from flask import Request
from dataclasses import dataclass


@dataclass
class RouteRequest:
    """Model for route generation requests with validation"""

    file: FileStorage
    proximity: bool = False
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    priority_only: bool = False
    exclude_days: List[str] = None
    max_stores_per_chain: Optional[int] = None
    min_sales_threshold: Optional[float] = None

    def __post_init__(self):
        if self.exclude_days is None:
            self.exclude_days = []

    @classmethod
    def from_request(cls, request: Request) -> "RouteRequest":
        """
        Create RouteRequest from Flask request

        Args:
            request: Flask request object

        Returns:
            RouteRequest instance
        """
        return cls(
            file=request.files.get("file"),
            proximity="proximity" in request.form,
            time_start=request.form.get("time_start") or None,
            time_end=request.form.get("time_end") or None,
            priority_only="priority_only" in request.form,
            exclude_days=request.form.getlist("exclude_days") or [],
            max_stores_per_chain=request.form.get("max_stores_per_chain", type=int),
            min_sales_threshold=request.form.get("min_sales_threshold", type=float),
        )

    def is_valid(self) -> bool:
        """Validate the request"""
        errors = self.get_validation_errors()
        return len(errors) == 0

    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors"""
        errors = []

        # File validation
        if not self.file or not self.file.filename:
            errors.append("No file uploaded")
        elif not self._is_allowed_file(self.file.filename):
            errors.append("Invalid file type. Please upload CSV or Excel file")

        # Time window validation
        if self.time_start and self.time_end:
            if self.time_start >= self.time_end:
                errors.append("Time start must be before time end")

        # Numeric validation
        if self.max_stores_per_chain is not None and self.max_stores_per_chain < 1:
            errors.append("Max stores per chain must be at least 1")

        if self.min_sales_threshold is not None and self.min_sales_threshold < 0:
            errors.append("Min sales threshold must be non-negative")

        # Day validation
        valid_days = {
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        }
        for day in self.exclude_days:
            if day not in valid_days:
                errors.append(f"Invalid day: {day}")

        return errors

    def get_filters(self) -> Dict[str, Any]:
        """Get filters dictionary for route generation"""
        return {
            "proximity": self.proximity,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "priority_only": self.priority_only,
            "exclude_days": self.exclude_days,
            "max_stores_per_chain": self.max_stores_per_chain,
            "min_sales_threshold": self.min_sales_threshold,
        }

    def get_cache_key(self) -> str:
        """Generate cache key for the request using SHA-256"""
        file_content = self.file.read()
        self.file.seek(0)  # Reset file pointer

        cache_data = {
            "file_content": file_content.decode("utf-8", errors="ignore")[:1000],  # First 1000 chars
            "filters": self.get_filters(),
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        allowed_extensions = {"csv", "xlsx", "xls"}
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging"""
        return {
            "has_file": self.file is not None,
            "filename": self.file.filename if self.file else None,
            "proximity": self.proximity,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "priority_only": self.priority_only,
            "exclude_days": self.exclude_days,
            "max_stores_per_chain": self.max_stores_per_chain,
            "min_sales_threshold": self.min_sales_threshold,
        }
