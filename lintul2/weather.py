"""Lees de dagelijkse CABO/FST-weergegevens zonder ontbrekende waarden."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path


@dataclass(frozen=True)
class Weather:
    station: int
    year: int
    day: int
    rdd: float
    tmmn: float
    tmmx: float
    vp: float
    wn: float
    rain: float


def read_weather(path: str | Path) -> dict[int, Weather]:
    days: dict[int, Weather] = {}
    metadata = False
    year = None
    station = None
    for number, line in enumerate(Path(path).read_text(encoding="ascii").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("*"):
            continue
        try:
            values = [float(value) for value in line.split()]
        except ValueError as exc:
            raise ValueError(f"{path}:{number}: ongeldige getalwaarde") from exc
        if not all(isfinite(value) and value != -99 for value in values):
            raise ValueError(f"{path}:{number}: ontbrekende of niet-eindige waarde")
        if not metadata:
            if len(values) != 5:
                raise ValueError(f"{path}:{number}: verwacht vijf locatiegegevens")
            metadata = True
            continue
        if len(values) != 9 or any(value != int(value) for value in values[:3]):
            raise ValueError(f"{path}:{number}: verwacht station, jaar, dag en zes meetwaarden")
        istation, iyear, day = map(int, values[:3])
        # CABO-kwaliteitsregels zijn geen meetdagen; VERBETERSUGGESTIES.md #11.
        if istation == -999:
            continue
        if not 1 <= day <= 366 or day in days:
            raise ValueError(f"{path}:{number}: ongeldige of dubbele dag {day}")
        if year is not None and (iyear != year or istation != station):
            raise ValueError(f"{path}:{number}: meerdere jaren of stations")
        station, year = istation, iyear
        rdd, tmmn, tmmx, vp, wn, rain = values[3:]
        days[day] = Weather(istation, iyear, day, rdd * 1000, tmmn, tmmx, vp, wn, rain)
    if not days:
        raise ValueError(f"{path}: geen dagelijkse weergegevens")
    return days
