"""Schrijf de modeluitvoer als tab-gescheiden tabel."""

import argparse
import csv
from pathlib import Path

from .model import COLUMNS, simulate
from .weather import read_weather


def main() -> None:
    parser = argparse.ArgumentParser(description="Draai de 1-op-1 LINTUL2-port.")
    parser.add_argument("output", type=Path, help="Pad voor de tab-gescheiden uitvoer")
    parser.add_argument("--weather", type=Path, default=Path("NLD1.987"), help="CABO-weerbestand")
    args = parser.parse_args()
    # De originele invoer en referentie mogen nooit als uitvoer overschreven worden.
    source_root = Path(__file__).resolve().parents[1]
    protected = [
        root / name
        for root in (Path.cwd(), source_root)
        for name in ("LINTUL2.FST", "NLD1.987", "res.dat")
    ]
    protected.append(args.weather)
    if any(args.output.resolve() == path.resolve() for path in protected):
        parser.error("het uitvoerpad mag geen bronbestand, weerbestand of referentie zijn")
    rows = simulate(read_weather(args.weather))
    with args.output.open("w", encoding="ascii", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(COLUMNS)
        writer.writerows([f"{row[column]:.8g}" for column in COLUMNS] for row in rows)


if __name__ == "__main__":
    main()
