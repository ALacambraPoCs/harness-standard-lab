def total(lines: list[tuple[int, float]]) -> float:
    """Suma cantidad × precio de cada línea. Rechaza cantidades negativas."""
    for n, (q, _) in enumerate(lines, start=1):
        if q < 0:
            raise ValueError(f"Cantidad negativa en la línea {n}: {q}")
    return round(sum(q * p for q, p in lines), 2)
