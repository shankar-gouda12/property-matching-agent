import requests

def test_matching_agent():
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Fetch Dynamic Filters
    print("Testing GET /api/filters...")
    r_filters = requests.get(f"{base_url}/filters")
    assert r_filters.status_code == 200
    filters = r_filters.json()
    print("Available filters:")
    print("Types:", filters["property_types"])
    print("BHKs:", filters["bhks"])
    print("Locations:", filters["locations"])
    print("Statuses:", filters["statuses"])
    print("-" * 50)

    # 2. Test STRICT Search matching 3 BHK Apartment in Hennur (should match 1 row Prestige Vista)
    print("Testing POST /api/search (STRICT Mode)...")
    payload = {
        "property_type": "Apartment",
        "bhk": 3,
        "budget_cr": 1.2,
        "location": "Hennur",
        "status": "Ready to Move",
        "mode": "STRICT"
    }
    r_search = requests.post(f"{base_url}/search", json=payload)
    assert r_search.status_code == 200
    res = r_search.json()
    print(f"Total Matches found: {res['total_matches']}")
    for match in res["matches"]:
        print(f"Score: {match['score']} | Project: {match['details']['Project Name']} | Budget: {match['details']['Budget (Cr)']} | Location: {match['details']['Location']}")
    print("-" * 50)

    # 3. Test STRICT Search Budget Exceeded (should NOT match)
    print("Testing POST /api/search Budget Exceeded (STRICT Mode)...")
    payload_budget_exceeded = {
        "property_type": "Apartment",
        "bhk": 3,
        "budget_cr": 0.5,  # Too low
        "location": "Hennur",
        "status": "Ready to Move",
        "mode": "STRICT"
    }
    r_search_budget = requests.post(f"{base_url}/search", json=payload_budget_exceeded)
    res_budget = r_search_budget.json()
    print(f"Total Matches (Budget Exceeded): {res_budget['total_matches']}")
    print("-" * 50)

    # 4. Test FLEXIBLE Search (should show partial score e.g. 4/5 for budget mismatch)
    print("Testing POST /api/search (FLEXIBLE Mode)...")
    r_flexible = requests.post(f"{base_url}/search", json=payload_budget_exceeded)
    res_flex = r_flexible.json()
    print(f"Total Matches (Flexible Mode): {res_flex['total_matches']}")
    for match in res_flex["matches"]:
        print(f"Score: {match['score']} | Project: {match['details']['Project Name']} | Match details: {match['match_details']}")
    print("-" * 50)

if __name__ == "__main__":
    test_matching_agent()
