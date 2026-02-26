from config import get_config

config = get_config()
sizing_whale_pct = config.STAKE_WHALE_PCT

def sizing_constraints(usdc_size: float) -> float:
    new_size = usdc_size * sizing_whale_pct
    print(new_size)
    return new_size

if __name__ == "__main__":
    print(sizing_constraints(500))
