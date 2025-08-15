from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import csv
import io
import os
import logging
from typing import List, Dict, Any, Optional
from routing.core import generate_route as core_generate_route

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = "uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# Ensure uploads directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_file_content(file_path: str) -> bool:
    """Validate that the file has required columns"""
    try:
        stores = load_stores_from_file(file_path)
        if not stores:
            return False

        # Check for required columns (flexible naming)
        # For now, just check that we have at least one store with a name
        first_store = stores[0]

        # Check if there's at least a name field (flexible naming)
        name_fields = ["name", "store_name", "store name", "storename"]
        has_name = any(
            key.lower().replace(" ", "_") in name_fields
            for key in first_store.keys()
        )

        if not has_name:
            logger.warning("Missing required field: name")
            return False

        return True
    except Exception as e:
        logger.error(f"Error validating file content: {str(e)}")
        return False


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Generate route with comprehensive validation and error handling"""
    try:
        # Parse all form parameters
        file = request.files.get("file")
        proximity = "proximity" in request.form
        time_start = request.form.get("time_start")
        time_end = request.form.get("time_end")
        priority_only = "priority_only" in request.form
        exclude_days = request.form.getlist("exclude_days")
        max_stores_per_chain = request.form.get(
            "max_stores_per_chain", type=int
        )
        min_sales_threshold = request.form.get(
            "min_sales_threshold", type=float
        )

        # Validate required file
        if not file or file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type. Please upload CSV or Excel file.",
                        "supported_formats": list(ALLOWED_EXTENSIONS),
                    }
                ),
                400,
            )

        # Validate time window
        if time_start and time_end:
            if time_start >= time_end:
                return (
                    jsonify({"error": "Time start must be before time end"}),
                    400,
                )

        # Validate numeric inputs
        if max_stores_per_chain is not None and max_stores_per_chain < 1:
            return (
                jsonify({"error": "Max stores per chain must be at least 1"}),
                400,
            )

        if min_sales_threshold is not None and min_sales_threshold < 0:
            return (
                jsonify({"error": "Min sales threshold must be non-negative"}),
                400,
            )

        # Save and process file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Validate file is not empty
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)
            return jsonify({"error": "Empty file uploaded"}), 400

        # Validate file content
        if not validate_file_content(file_path):
            os.remove(file_path)
            return (
                jsonify(
                    {
                        "error": "Invalid file format or missing required columns (name field required)"
                    }
                ),
                400,
            )

        # Generate route with all parameters
        route_result = generate_route_with_filters(
            file_path=file_path,
            proximity=proximity,
            time_start=time_start,
            time_end=time_end,
            priority_only=priority_only,
            exclude_days=exclude_days,
            max_stores_per_chain=max_stores_per_chain,
            min_sales_threshold=min_sales_threshold,
        )

        # Clean up uploaded file
        os.remove(file_path)

        logger.info(
            f"Route generated successfully with {len(route_result) if route_result else 0} stops"
        )

        return (
            jsonify(
                {
                    "message": "Route generated successfully",
                    "route": route_result,
                    "filters_applied": {
                        "proximity": proximity,
                        "time_window": (
                            f"{time_start} - {time_end}"
                            if time_start and time_end
                            else None
                        ),
                        "priority_only": priority_only,
                        "exclude_days": exclude_days,
                        "max_stores_per_chain": max_stores_per_chain,
                        "min_sales_threshold": min_sales_threshold,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error generating route: {str(e)}")
        # Clean up file if it exists
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return (
            jsonify({"error": "Failed to process route", "details": str(e)}),
            500,
        )


def generate_route_with_filters(
    file_path: str,
    proximity: bool,
    time_start: Optional[str],
    time_end: Optional[str],
    priority_only: bool,
    exclude_days: List[str],
    max_stores_per_chain: Optional[int],
    min_sales_threshold: Optional[float],
) -> List[Dict[str, Any]]:
    """
    Enhanced route generation with comprehensive filtering parameters

    Args:
        file_path: Path to the stores file
        proximity: Whether to apply proximity-based sorting
        time_start: Start time for time window filtering
        time_end: End time for time window filtering
        priority_only: Whether to filter only priority stores
        exclude_days: List of days to exclude from routing
        max_stores_per_chain: Maximum number of stores per chain
        min_sales_threshold: Minimum sales threshold for store inclusion

    Returns:
        List of filtered and sorted stores representing the route
    """
    try:
        # Load stores from file
        stores = load_stores_from_file(file_path)

        if not stores:
            logger.warning("No stores found in file")
            return []

        # Build playbook constraints based on form inputs
        playbook_constraints = build_playbook_constraints(
            time_start=time_start,
            time_end=time_end,
            priority_only=priority_only,
            exclude_days=exclude_days,
            max_stores_per_chain=max_stores_per_chain,
            min_sales_threshold=min_sales_threshold,
        )

        # Generate route using core logic
        route = core_generate_route(stores, None, playbook_constraints)

        # Apply proximity sorting if enabled
        if proximity and route:
            route = apply_proximity_sorting(route)

        return route

    except Exception as e:
        logger.error(f"Error in generate_route_with_filters: {str(e)}")
        raise


def load_stores_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load stores from CSV or Excel file with proper error handling"""
    try:
        if file_path.endswith(".csv"):
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                stores = list(reader)
                logger.info(f"Loaded {len(stores)} stores from CSV file")
                return stores
        elif file_path.endswith((".xlsx", ".xls")):
            try:
                import pandas as pd

                df = pd.read_excel(
                    file_path,
                    engine=(
                        "openpyxl" if file_path.endswith(".xlsx") else "xlrd"
                    ),
                )
                stores = df.to_dict("records")
                logger.info(f"Loaded {len(stores)} stores from Excel file")
                return stores
            except ImportError:
                logger.error(
                    "pandas or openpyxl not installed for Excel support"
                )
                raise NotImplementedError(
                    "Excel file support requires pandas and openpyxl packages"
                )
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        logger.error(f"Error loading stores from file {file_path}: {str(e)}")
        raise


def build_playbook_constraints(
    time_start: Optional[str],
    time_end: Optional[str],
    priority_only: bool,
    exclude_days: List[str],
    max_stores_per_chain: Optional[int],
    min_sales_threshold: Optional[float],
) -> Dict[str, Any]:
    """
    Build playbook constraints from form inputs

    Args:
        time_start: Start time for time window
        time_end: End time for time window
        priority_only: Whether to filter only priority stores
        exclude_days: List of days to exclude
        max_stores_per_chain: Maximum stores per chain
        min_sales_threshold: Minimum sales threshold

    Returns:
        Dictionary of constraints for the routing engine
    """
    constraints = {}

    # Global constraints (non-dict values allowed)
    if max_stores_per_chain:
        constraints["max_route_stops"] = max_stores_per_chain

    # For now, we'll create a general constraint bucket since the routing core
    # expects chain-specific constraints as nested dictionaries
    general_constraints = {}

    # Add time window constraints
    if time_start and time_end:
        general_constraints["time_window"] = {
            "start": time_start,
            "end": time_end,
        }

    # Add day exclusion constraints
    if exclude_days:
        # Convert to days_allowed (inverse of exclude_days)
        all_days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        allowed_days = [day for day in all_days if day not in exclude_days]
        if allowed_days:
            general_constraints["days_allowed"] = allowed_days

    # Add priority filter
    if priority_only:
        general_constraints["priority_only"] = True

    # Add sales threshold
    if min_sales_threshold:
        general_constraints["min_sales_threshold"] = min_sales_threshold

    # Apply general constraints to all chains (workaround for current routing core structure)
    if general_constraints:
        constraints["*"] = general_constraints  # Use wildcard for all chains

    logger.debug(f"Built constraints: {constraints}")
    return constraints


def apply_proximity_sorting(
    route: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Apply proximity-based sorting to route using a simple nearest neighbor approach

    Args:
        route: List of store dictionaries

    Returns:
        Sorted route based on proximity
    """
    if not route or len(route) < 2:
        return route

    try:
        # Check if stores have coordinate information
        if not all(
            "latitude" in store and "longitude" in store for store in route
        ):
            logger.warning(
                "Stores missing coordinate information for proximity sorting"
            )
            return route

        # Simple nearest neighbor algorithm
        sorted_route = []
        remaining_stores = route.copy()

        # Start with the first store
        current_store = remaining_stores.pop(0)
        sorted_route.append(current_store)

        # Find nearest neighbors
        while remaining_stores:
            distances = []
            for store in remaining_stores:
                try:
                    from geopy.distance import geodesic

                    distance = geodesic(
                        (
                            current_store["latitude"],
                            current_store["longitude"],
                        ),
                        (store["latitude"], store["longitude"]),
                    ).kilometers
                    distances.append((distance, store))
                except Exception as e:
                    logger.warning(f"Error calculating distance: {e}")
                    distances.append((float("inf"), store))

            # Find the closest store
            distances.sort(key=lambda x: x[0])
            closest_store = distances[0][1]

            sorted_route.append(closest_store)
            remaining_stores.remove(closest_store)
            current_store = closest_store

        logger.info(f"Applied proximity sorting to {len(sorted_route)} stores")
        return sorted_route

    except Exception as e:
        logger.error(f"Error in proximity sorting: {str(e)}")
        return route  # Return original route if sorting fails


@app.route("/export", methods=["POST"])
def export_route():
    """Export route to CSV format with proper error handling"""
    try:
        file = request.files.get("file")
        if not file or file.filename == "":
            return jsonify({"error": "Missing file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        try:
            file_content = file.read().decode("utf-8")
            stream = io.StringIO(file_content)
            reader = csv.DictReader(stream)
            stores = list(reader)
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return jsonify({"error": "Invalid CSV format"}), 400

        # Process optional playbook file
        playbook = {}
        playbook_file = request.files.get("playbook")
        if playbook_file and playbook_file.filename:
            try:
                playbook_content = playbook_file.read().decode("utf-8")
                playbook_stream = io.StringIO(playbook_content)
                for row in csv.DictReader(playbook_stream):
                    chain = row.get("chain")
                    if chain:
                        playbook[chain] = {
                            k: v for k, v in row.items() if k != "chain"
                        }
            except Exception as e:
                logger.error(f"Error reading playbook CSV: {str(e)}")
                return jsonify({"error": "Invalid playbook CSV format"}), 400

        # Generate route
        route = core_generate_route(stores, None, playbook)

        # Create CSV output
        output = io.StringIO()
        if route:
            writer = csv.DictWriter(output, fieldnames=route[0].keys())
            writer.writeheader()
            writer.writerows(route)
        else:
            # Empty route
            output.write("No route generated\n")

        output.seek(0)
        logger.info(f"Exported route with {len(route) if route else 0} stops")
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=route.csv"},
        )

    except Exception as e:
        logger.error(f"Error exporting route: {str(e)}")
        return (
            jsonify({"error": "Failed to export route", "details": str(e)}),
            500,
        )


# --- New API endpoint for playbook constraint validation ---
@app.route("/api/v1/validate_playbook", methods=["POST"])
def validate_playbook_constraints():
    """Validate playbook constraint structure and content"""
    try:
        playbook_file = request.files.get("playbook")
        if not playbook_file or playbook_file.filename == "":
            return jsonify({"error": "Missing playbook file"}), 400

        content = playbook_file.read().decode("utf-8")
        stream = io.StringIO(content)
        reader = csv.DictReader(stream)
        invalid_rows = []

        for idx, row in enumerate(reader, start=1):
            chain = row.get("chain")
            if not chain:
                invalid_rows.append(
                    {"row": idx, "error": "Missing chain value"}
                )
                continue

            for key, value in row.items():
                if key != "chain":
                    if value.strip() == "":
                        continue
                    if key in ["max_route_stops"]:
                        try:
                            int(value)
                        except ValueError:
                            invalid_rows.append(
                                {
                                    "row": idx,
                                    "field": key,
                                    "error": "Must be an integer",
                                }
                            )
                    if key in ["min_sales_threshold"]:
                        try:
                            float(value)
                        except ValueError:
                            invalid_rows.append(
                                {
                                    "row": idx,
                                    "field": key,
                                    "error": "Must be a float",
                                }
                            )

        if invalid_rows:
            return jsonify({"valid": False, "errors": invalid_rows}), 400

        return jsonify({"valid": True}), 200

    except Exception as e:
        logger.error(f"Playbook validation failed: {e}")
        return jsonify({"error": "Validation error", "details": str(e)}), 500


if __name__ == "__main__":
    # Try port 5001 if 5000 is in use (common on macOS with AirPlay)
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
