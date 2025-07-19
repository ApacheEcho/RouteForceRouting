from typing import List, Dict
from datetime import datetime

def summarize_route(route: List[Dict], original_stores: List[Dict], playbook: Dict, visit_date: datetime = None) -> Dict:
    summary = {
        "total_stops": len(route),
        "chains_in_route": list({store["chain"] for store in route}),
        "priorities": {},
        "skipped_due_to_visit_hours": 0
    }

    # Count priorities
    for store in route:
        chain = store.get("chain")
        if chain and chain in playbook and "priority" in playbook[chain]:
            p = playbook[chain]["priority"]
            summary["priorities"][p] = summary["priorities"].get(p, 0) + 1

    # Skipped due to visit_hours
    for store in original_stores:
        if store not in route:
            chain = store.get("chain")
            if chain in playbook and "visit_hours" in playbook[chain]:
                try:
                    now = visit_date or datetime.now()
                    vh = playbook[chain]["visit_hours"]
                    start = datetime.strptime(vh["start"], "%H:%M").time()
                    end = datetime.strptime(vh["end"], "%H:%M").time()
                    if not (start <= now.time() <= end):
                        summary["skipped_due_to_visit_hours"] += 1
                except Exception:
                    continue

    return summary


# Helper to print a route summary in a clean, readable format
def print_route_summary(summary: Dict) -> None:
    print("\n--- Route Summary ---")
    print(f"Total Stops: {summary['total_stops']}")
    print(f"Chains in Route: {', '.join(summary['chains_in_route'])}")
    print("Priority Distribution:")
    for priority, count in sorted(summary['priorities'].items(), reverse=True):
        print(f"  Priority {priority}: {count} stop(s)")
    print(f"Skipped Due to Visit Hours: {summary['skipped_due_to_visit_hours']}")
    print("----------------------\n")

def generate_route(stores: List[Dict], visit_date: datetime = None, playbook: Dict = None) -> List[Dict]:
    """
    Generate optimized route from stores list
    
    Args:
        stores: List of store dictionaries
        visit_date: Optional visit date for time-based filtering
        playbook: Optional playbook constraints
        
    Returns:
        List of stores representing optimized route
    """
    if not stores:
        return []
    
    # Apply playbook constraints if provided
    if playbook:
        filtered_stores = apply_playbook_constraints(stores, playbook, visit_date)
    else:
        filtered_stores = stores.copy()
    
    # Simple optimization: sort by priority if available, then by name
    def sort_key(store):
        chain = store.get("chain", "")
        priority = 0
        if playbook and chain in playbook and "priority" in playbook[chain]:
            priority = playbook[chain]["priority"]
        return (-priority, store.get("name", ""))
    
    return sorted(filtered_stores, key=sort_key)

def apply_playbook_constraints(stores: List[Dict], playbook: Dict, visit_date: datetime = None) -> List[Dict]:
    """Apply playbook constraints to filter stores"""
    filtered_stores = []
    current_time = visit_date or datetime.now()
    
    for store in stores:
        chain = store.get("chain", "")
        
        # Skip if chain not in playbook
        if chain not in playbook:
            filtered_stores.append(store)
            continue
            
        constraints = playbook[chain]
        
        # Check visit hours
        if "visit_hours" in constraints:
            try:
                vh = constraints["visit_hours"]
                start = datetime.strptime(vh["start"], "%H:%M").time()
                end = datetime.strptime(vh["end"], "%H:%M").time()
                if not (start <= current_time.time() <= end):
                    continue  # Skip this store
            except Exception:
                pass  # If parsing fails, include the store
        
        # Check max route stops (simplified - just limit total)
        if "max_route_stops" in constraints:
            max_stops = constraints["max_route_stops"]
            if len(filtered_stores) >= max_stops:
                break
        
        filtered_stores.append(store)
    
    return filtered_stores