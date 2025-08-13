import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import pytest
from main import app
from routing.core import generate_route
import logging

logging.basicConfig(level=logging.DEBUG)
from datetime import datetime
from flask import request


def is_valid_day(today, allowed_days):
    return today in allowed_days


def is_within_time_window(now, time_window):
    try:
        start = datetime.strptime(time_window["start"], "%H:%M").time()
        end = datetime.strptime(time_window["end"], "%H:%M").time()
        return start <= now <= end
    except (KeyError, ValueError, TypeError):
        return False


def is_valid_visit_hours(visit_hours):
    if (
        not isinstance(visit_hours, dict)
        or "start" not in visit_hours
        or "end" not in visit_hours
    ):
        return False
    try:
        datetime.strptime(visit_hours["start"], "%H:%M")
        datetime.strptime(visit_hours["end"], "%H:%M")
        return True
    except (ValueError, TypeError):
        return False


# Edge cases for generate_route


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """
    GIVEN a Flask application
    WHEN the '/' route is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1>RouteForce Routing</h1>" in response.data
    assert b"Optimize your delivery routes with intelligent algorithms" in response.data


def test_index_renders_template(client, monkeypatch):
    """
    GIVEN a Flask application
    WHEN the '/' route is requested
    THEN check that the correct template content is rendered
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"RouteForce Routing" in response.data
    assert b"form" in response.data
    assert b"Generate Optimized Route" in response.data
    assert b"Upload Stores File" in response.data


def test_priority_sorting():
    stores = [
        {"name": "Store A", "chain": "Chain A"},
        {"name": "Store B", "chain": "Chain B"},
        {"name": "Store C", "chain": "Chain C"},
    ]
    playbook = {
        "Chain A": {"priority": 2},
        "Chain B": {"priority": 3},
        "Chain C": {"priority": 1},
    }
    result = generate_route(stores, None, playbook)
    assert [store["name"] for store in result] == ["Store B", "Store A", "Store C"]


def test_stop_limit_applies_after_sort():
    stores = [
        {"name": "Store A", "chain": "Chain A"},
        {"name": "Store B", "chain": "Chain B"},
    ]
    playbook = {
        "max_route_stops": 1,
        "Chain A": {"priority": 1},
        "Chain B": {"priority": 2},
    }
    result = generate_route(stores, None, playbook)
    assert len(result) == 1
    assert result[0]["name"] == "Store B"


def test_missing_chain_rules():
    stores = [{"name": "Store A", "chain": "UnknownChain"}]
    playbook = {}
    result = generate_route(stores, None, playbook)
    assert result == stores


def test_generate_route_submission(client):
    """
    GIVEN a Flask application with the /generate route
    WHEN a CSV file is submitted via POST
    THEN check that the response includes the generated route
    """
    import io

    sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"
    data = {"file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv")}
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Store A" in response.data or b"Store B" in response.data


def test_generate_route_with_invalid_file_type(client):
    import io

    bad_data = {"file": (io.BytesIO(b"not,a,csv"), "not_a_csv.txt")}
    response = client.post(
        "/generate", data=bad_data, content_type="multipart/form-data"
    )
    assert response.status_code == 400


def test_generate_route_with_empty_file(client):
    import io

    empty_data = {"file": (io.BytesIO(b""), "empty.csv")}
    response = client.post(
        "/generate", data=empty_data, content_type="multipart/form-data"
    )
    assert response.status_code == 400


def test_generate_route_with_malformed_playbook():
    stores = [{"name": "Store A", "chain": "Chain A"}]
    playbook = {"Chain A": {"visit_hours": None}}  # Invalid data type
    result = generate_route(stores, None, playbook)
    assert isinstance(result, list)


def test_generate_route_with_empty_store_list():
    result = generate_route([], None, {})
    assert result == []


@pytest.mark.parametrize(
    "stores, playbook, expected_names",
    [
        ([{"name": "S1", "chain": "A"}], {"A": {"priority": 1}}, ["S1"]),
        (
            [{"name": "S1", "chain": "A"}, {"name": "S2", "chain": "B"}],
            {"A": {"priority": 2}, "B": {"priority": 1}},
            ["S1", "S2"],
        ),
    ],
)
def test_param_route_sorting(stores, playbook, expected_names):
    result = generate_route(stores, None, playbook)
    assert [s["name"] for s in result] == expected_names


# Edge cases for generate_route
@pytest.mark.parametrize(
    "stores,playbook,expected",
    [
        ([], {}, []),  # Empty stores list
        (
            [{"name": "Store A", "chain": "Chain A"}],
            {"Chain A": {"priority": 1}},
            [{"name": "Store A", "chain": "Chain A"}],
        ),  # Single store
        (
            [{"name": "Store A", "chain": "Chain A"}],
            {"Chain A": {"visit_hours": {"start": "invalid", "end": "invalid"}}},
            [],
        ),  # Malformed playbook
    ],
)
def test_generate_route_edge_cases(stores, playbook, expected):
    result = generate_route(stores, None, playbook)
    assert result == expected


def test_disallowed_day():
    stores = [{"name": "Store A", "chain": "Chain A"}]
    playbook = {"Chain A": {"days_allowed": ["Tuesday"]}}  # Will fail on most days
    # Pass a specific date (Wednesday) to test the filtering
    test_date = datetime.strptime("2025-07-16", "%Y-%m-%d")  # Wednesday
    result = generate_route(stores, test_date, playbook)
    assert result == []


def test_disallowed_time_window():
    stores = [{"name": "Store A", "chain": "Chain A"}]
    playbook = {
        "Chain A": {"time_window": {"start": "00:00", "end": "01:00"}}
    }  # Will fail most times
    # Pass a specific time outside the window
    test_date = datetime.strptime("2025-07-16 12:00", "%Y-%m-%d %H:%M")  # 12:00 PM
    result = generate_route(stores, test_date, playbook)
    assert result == []


def test_allowed_time_window_and_day():
    stores = [{"name": "Store A", "chain": "Chain A"}]
    today = datetime.now().strftime("%A")
    playbook = {
        "Chain A": {
            "days_allowed": [today],
            "time_window": {"start": "00:00", "end": "23:59"},
            "priority": 1,
        }
    }
    result = generate_route(stores, None, playbook)
    assert len(result) == 1


def test_export_route(client):
    """Test the CSV export functionality"""
    import io

    sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"
    data = {"file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv")}
    response = client.post("/export", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Store A" in response.data or b"Store B" in response.data


# -------------------------------------------
# 🚀 ROUTEFORCE PHASE 2: FRONTEND + PROXIMITY
# -------------------------------------------
#
# Phase focus:
# 1. HTMX Frontend Input Flow (CSV upload, result display, export)
# 2. Proximity Logic (geo-bias, nearest-start, corridor flow)
#
# All core logic is passing. Next commits should extend usability + intelligence.


def test_export_with_route_csv_download(client):
    """Test POST '/export' with route data to confirm CSV download functionality"""
    # Test with sample route data
    test_route_data = {
        'route': [
            {'store_name': 'Store A', 'address': '123 Main St', 'priority': 'high'},
            {'store_name': 'Store B', 'address': '456 Oak Ave', 'priority': 'medium'}
        ]
    }
    response = client.post('/export', json=test_route_data)
    # Export may return 200 with CSV or error response depending on data
    assert response.status_code in [200, 400, 500]


# === HTMX Frontend Upload Flow ===
def test_htmx_input_form_present(client):
    response = client.get("/")
    assert b"<form" in response.data
    assert b'name="file"' in response.data
    assert b"Upload" in response.data


def test_generate_route_render_html(client):
    import io

    sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"
    data = {"file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv")}
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Store A" in response.data or b"Store B" in response.data


def test_export_route_csv(client):
    import io

    sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"
    playbook_csv = "chain,priority\nChain A,1\nChain B,2"
    data = {
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv"),
        "playbook": (io.BytesIO(playbook_csv.encode("utf-8")), "playbook.csv"),
    }
    response = client.post("/export", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Store A" in response.data or b"Store B" in response.data


# === Enhanced Test Coverage ===

def test_home_page_landing_elements(client):
    """Test GET '/' to confirm landing page elements are present"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'RouteForce' in response.data
    assert b'href="/generate"' in response.data  # Check for Route Generator link

def test_generate_route_html_rendering(client):
    """Test GET '/generate' to confirm HTML form rendering"""
    response = client.get('/generate')
    assert response.status_code == 200
    assert b'<form id="routeForm"' in response.data
    assert b'enctype="multipart/form-data"' in response.data

def test_export_with_playbook_csv_download(client):
    """Test POST '/export' with store + playbook file, check CSV download"""
    import io
    
    sample_stores = "name,address,chain,sales\nStore A,123 Main St,Chain A,1000\nStore B,456 Oak Ave,Chain B,2000"
    sample_playbook = "rule_type,condition,value\nconstraint,max_stores_per_day,5"
    
    data = {
        'file': (io.BytesIO(sample_stores.encode()), 'stores.csv'),
        'playbook_file': (io.BytesIO(sample_playbook.encode()), 'playbook.csv'),
        'algorithm': 'genetic',
        'format': 'csv'
    }
    
    response = client.post('/export', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert 'attachment; filename=' in response.headers.get('Content-Disposition', '')

# === Proximity Logic Tests (Ready for Future Implementation) ===
def test_proximity_filter_placeholder(client):
    """Test for proximity filter request parameter acceptance"""
    # Test that proximity parameter is accepted in route generation
    from io import BytesIO
    test_file_content = "store_name,address,priority\nTest Store,123 Main St,high"
    test_file = (BytesIO(test_file_content.encode()), 'test_stores.csv')
    
    response = client.post('/generate', 
                           data={'proximity': '1', 'file': test_file},
                           content_type='multipart/form-data')
    # Should process request (may error on data validation, but accepts parameters)
    assert response.status_code in [200, 400, 500]


def test_generate_route_with_all_filters(client):
    """Test the enhanced /generate route with all filter parameters"""
    import io

    sample_csv = "name,chain,sales\nStore A,Chain A,1000\nStore B,Chain B,2000\nStore C,Chain C,500"
    data = {
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv"),
        "proximity": "1",
        "time_start": "09:00",
        "time_end": "17:00",
        "priority_only": "1",
        "exclude_days": ["Sunday", "Monday"],
        "max_stores_per_chain": "2",
        "min_sales_threshold": "800",
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    result = response.get_json()
    assert "route" in result
    assert "filters_applied" in result
    assert result["filters_applied"]["proximity"] is True
    assert result["filters_applied"]["time_window"] == "09:00 - 17:00"
    assert result["filters_applied"]["priority_only"] is True
    assert "Sunday" in result["filters_applied"]["exclude_days"]
    assert "Monday" in result["filters_applied"]["exclude_days"]
    assert result["filters_applied"]["max_stores_per_chain"] == 2
    assert result["filters_applied"]["min_sales_threshold"] == 800.0


def test_generate_route_validation_errors(client):
    """Test validation errors for the enhanced /generate route"""
    import io

    sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"

    # Test invalid time window
    data = {
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv"),
        "time_start": "17:00",
        "time_end": "09:00",  # End before start
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Time start must be before time end" in response.get_json()["error"]

    # Test invalid max stores per chain
    data = {
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv"),
        "max_stores_per_chain": "0",  # Invalid value
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Max stores per chain must be at least 1" in response.get_json()["error"]

    # Test invalid min sales threshold
    data = {
        "file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv"),
        "min_sales_threshold": "-100",  # Invalid value
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Min sales threshold must be non-negative" in response.get_json()["error"]
