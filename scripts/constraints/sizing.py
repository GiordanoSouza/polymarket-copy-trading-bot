# def sizing_constraints(size: float) -> bool:

def sizing_constraints(usdc_size: float) -> float:
    new_size = usdc_size * 0.001
    print(new_size)
    return new_size

if __name__ == "__main__":
    sizing_constraints(500)
    