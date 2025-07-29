def print_route(route, score):
    """
    Print the route details and score.

    Args:
        route: List of store dictionaries.
        score: Route score (float).
    """
    print("\nRoute Details:")
    for idx, store in enumerate(route):
        print(f"Stop {idx + 1}: {store['name']} ({store['address']})")

    print(f"\nRoute Score: {score:.2f}")
