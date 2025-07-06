from geopy.distance import geodesic

def calculate_distance(store_a, store_b):
    """
    Calculate distance between two store locations.
    """
    coord_a = (store_a['lat'], store_a['lon'])
    coord_b = (store_b['lat'], store_b['lon'])
    return geodesic(coord_a, coord_b).km