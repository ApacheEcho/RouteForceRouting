import webbrowser

from routing.config import DEFAULT_MAP_ZOOM_LEVEL
from routing.core import generate_route as core_generate_route


def open_full_route_map(route):
    base_url = "https://www.google.com/maps/dir/"
    waypoint_str = "/".join(
        f"{store['latitude']},{store['longitude']}"
        for store in route
        if "latitude" in store and "longitude" in store
    )
    webbrowser.open(f"{base_url}{waypoint_str}&zoom={DEFAULT_MAP_ZOOM_LEVEL}")


def generate_route_with_map_links(stores):
    route = core_generate_route(stores)
    open_full_route_map(route)
    return route
