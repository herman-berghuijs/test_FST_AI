"""De scalaire hulpfuncties van FST."""

from collections.abc import Sequence


def afgen(table: Sequence[tuple[float, float]], x: float) -> float:
    """Interpoleer lineair; houd buiten de tabel de eindwaarden vast."""
    if x <= table[0][0]:
        return table[0][1]
    for (x1, y1), (x2, y2) in zip(table, table[1:]):
        if x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return table[-1][1]


def insw(x: float, y1: float, y2: float) -> float:
    return y1 if x < 0 else y2


def reaand(x1: float, x2: float) -> float:
    return 1.0 if x1 > 0 and x2 > 0 else 0.0


def limit(lo: float, hi: float, x: float) -> float:
    return min(max(x, lo), hi)


def notnul(x: float) -> float:
    return 1.0 if x == 0 else x
