from routing.cli_adapter import store_dict_to_dataclass, vehicle_dict_to_dataclass


def test_store_mapping_latlng():
    d = {
        "id": "S1",
        "name": "Alpha",
        "address": "123 A St",
        "lat": 40.0,
        "lng": -73.0,
        "priority": "high",
        "estimated_service_time": 20,
        "packages": 3,
        "weight_kg": 12.5,
    }
    s = store_dict_to_dataclass(d)
    assert s.store_id == "S1"
    assert s.name == "Alpha"
    assert s.coordinates == {"lat": 40.0, "lng": -73.0}
    assert s.priority == "high"
    assert s.estimated_service_time == 20
    assert s.packages == 3
    assert s.weight_kg == 12.5


def test_store_mapping_latitude_longitude_defaults():
    d = {
        "name": "Beta",
        "address": "234 B St",
        "latitude": 41.0,
        "longitude": -72.5,
    }
    s = store_dict_to_dataclass(d)
    assert s.coordinates == {"lat": 41.0, "lng": -72.5}
    # defaults applied
    assert s.priority == "medium"
    assert s.estimated_service_time == 15
    assert s.packages == 1
    assert s.weight_kg == 1.0


def test_vehicle_mapping_defaults_and_status():
    d = {
        "vehicle_id": "V1",
        "capacity_kg": 800,
        "max_packages": 120,
        "max_driving_hours": 7.5,
        "status": "available",
    }
    v = vehicle_dict_to_dataclass(d)
    assert v.vehicle_id == "V1"
    assert v.capacity_kg == 800
    assert v.max_packages == 120
    assert v.max_driving_hours == 7.5
    assert v.status.value == "available"

