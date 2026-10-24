def total(lines: list[tuple[int, float]], descuento: float = 0) -> float:
    """Suma cantidad × precio de cada línea y aplica el descuento porcentual (0–100).
    Rechaza cantidades y precios negativos, y descuentos fuera de 0–100."""
    for n, (q, p) in enumerate(lines, start=1):
        if q < 0:
            raise ValueError(f"Cantidad negativa en la línea {n}: {q}")
        if p < 0:
            raise ValueError(f"Precio negativo en la línea {n}: {p}")
    if not 0 <= descuento <= 100:
        raise ValueError(f"Descuento fuera de rango (0–100): {descuento}")
    subtotal = sum(q * p for q, p in lines)
    return round(subtotal * (1 - descuento / 100), 2)
