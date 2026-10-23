def total(lines: list[tuple[int, float]]) -> float:
    """Suma cantidad × precio de cada línea. Rechaza cantidades y precios negativos."""
    for n, (q, p) in enumerate(lines, start=1):
        if q < 0:
            raise ValueError(f"Cantidad negativa en la línea {n}: {q}")
        if p < 0:
            raise ValueError(f"Precio negativo en la línea {n}: {p}")
    return round(sum(q * p for q, p in lines), 2)
