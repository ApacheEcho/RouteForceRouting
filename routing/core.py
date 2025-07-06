from .utils import calculate_distance

def generate_route(store_list):
    """
    Sort stores by proximity using a circular routing logic.
    """
    if not store_list:
        return []

    # Start with first store, then loop by proximity
    route = [store_list[0]]
    remaining = store_list[1:]

    while remaining:
        last = route[-1]
        next_store = min(remaining, key=lambda s: calculate_distance(last, s))
        route.append(next_store)
        remaining.remove(next_store)

    return route