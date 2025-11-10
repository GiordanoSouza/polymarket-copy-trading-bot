# def sizing_constraints(size: float) -> bool:
import os

from dotenv import load_dotenv

load_dotenv()

def _get_sizing_whale_pct() -> float:
    value = os.getenv("STAKE_WHALE_PCT")
    if value is None:
        raise RuntimeError("Missing STAKE_WHALE_PCT in environment")
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError("STAKE_WHALE_PCT must be a number") from exc

sizing_whale_pct = _get_sizing_whale_pct()

def sizing_constraints(usdc_size: float) -> float:
    new_size = usdc_size * sizing_whale_pct
    print(new_size)
    return new_size

if __name__ == "__main__":
    print(sizing_constraints(500))
    
