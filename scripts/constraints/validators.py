import requests

def has_already_an_open_position(user: str, market: str) -> bool:
    """Verifica se o usuário tem posição aberta no mercado especificado."""
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
    result = has_already_an_open_position(
        "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
        "0x67749947d4e6a3041b36a90504c81545710fe044e0b1ce4de513d43b243357ed"
    )
    print(f"Tem posição aberta: {result}")