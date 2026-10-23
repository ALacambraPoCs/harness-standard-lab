def total(lines: list[tuple[int, float]]) -> float:
    """Suma cantidad × precio de cada línea."""
    return round(sum(q * p for q, p in lines), 2)
