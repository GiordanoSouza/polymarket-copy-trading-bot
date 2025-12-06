import requests

def has_already_an_open_position(user: str, market: str) -> bool:
    """Checks if the user has an open position in the specified market."""
    try:
        resp = requests.get(
            "https://data-api.polymarket.com/positions",
            params={"user": user, "market": market},
        )
        resp.raise_for_status()
        return bool(resp.json())
    except Exception:
        return False

if __name__ == "__main__":
    # Example usage - replace with actual addresses
    user_address = input("Enter user address: ")
    market_address = input("Enter market address: ")
    
    if user_address and market_address:
        result = has_already_an_open_position(user_address, market_address)
        print(f"Has open position: {result}")
    else:
        print("Please provide both user and market addresses.")