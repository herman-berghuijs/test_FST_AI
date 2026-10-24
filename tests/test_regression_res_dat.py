import csv
from pathlib import Path
import subprocess
import sys

import pytest

from lintul2.model import COLUMNS, simulate
from lintul2.weather import read_weather

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = (
    "TIME", "LAI", "WSOTHA", "WSO", "WST", "WLV", "WRT", "TSUM", "DAVTMP",
    "DTR", "ROOTD", "TRAN", "EVAP", "TRANRF", "WA", "WC", "YEAR", "RAIN", "TRAIN",
)


def read_reference():
    lines = [
        line for line in (ROOT / "res.dat").read_text(encoding="ascii").splitlines()
        if line.strip() and not line.startswith("*")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    assert tuple(reader.fieldnames) == EXPECTED_COLUMNS
    return [{key: float(value) for key, value in row.items()} for row in reader]


def compare_rows(actual, expected):
    assert COLUMNS == EXPECTED_COLUMNS
    assert [row["TIME"] for row in actual] == [*range(58, 239, 5), 241]
    assert [row["TIME"] for row in actual] == [row["TIME"] for row in expected]
    for column in EXPECTED_COLUMNS:
        assert [row[column] for row in actual] == pytest.approx(
            [row[column] for row in expected], rel=1e-3, abs=1e-4
        ), column


def test_regressie_alle_19_kolommen():
    expected = read_reference()
    actual = simulate(read_weather(ROOT / "NLD1.987"))
    compare_rows(actual, expected)
    print("\nGrootste relatieve verschil per kolom (referentienul: absoluut verschil):")
    for column in EXPECTED_COLUMNS:
        largest = max(
            abs(a[column] - e[column]) / abs(e[column]) if e[column] else abs(a[column])
            for a, e in zip(actual, expected)
        )
        print(f"{column}: {largest:.8g}")


def test_controlepunten_en_euler_timing():
    rows = simulate(read_weather(ROOT / "NLD1.987"))
    assert rows[0]["WLV"] == pytest.approx(0.54545, abs=1e-5)
    assert rows[0]["WA"] == 36.0
    assert rows[0]["DTR"] == 0.65
    assert rows[0]["RAIN"] == 14.5
    assert rows[0]["TRAIN"] == 0
    assert rows[1]["TRAIN"] == pytest.approx(43.5)
    assert rows[1]["DAVTMP"] == -4.75
    assert rows[-1]["WSO"] == pytest.approx(735.50, rel=1e-3)
    assert rows[-1]["TSUM"] == pytest.approx(2091.6, rel=1e-3)
    assert rows[-1]["ROOTD"] == pytest.approx(1.2040)


def test_cli_schrijft_regressietabel(tmp_path):
    output = tmp_path / "python.dat"
    subprocess.run([sys.executable, "-m", "lintul2", str(output)], cwd=ROOT, check=True)
    with output.open(encoding="ascii", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        assert tuple(reader.fieldnames) == EXPECTED_COLUMNS
        actual = [{key: float(value) for key, value in row.items()} for row in reader]
    compare_rows(actual, read_reference())


@pytest.mark.parametrize("name", ["res.dat", "LINTUL2.FST", "NLD1.987"])
def test_cli_weigert_bronbestanden_als_uitvoer(name):
    path = ROOT / name
    before = path.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "lintul2", str(path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "het uitvoerpad mag geen" in result.stderr
    assert path.read_bytes() == before


@pytest.mark.parametrize("name", ["res.dat", "LINTUL2.FST", "NLD1.987"])
def test_cli_beschermt_bronmap_buiten_werkmap(tmp_path, monkeypatch, name):
    from lintul2 import __main__ as cli

    source_root = tmp_path / "bron"
    source_root.mkdir()
    output = source_root / name
    output.write_bytes(b"ongewijzigd")
    monkeypatch.setattr(cli, "__file__", str(source_root / "lintul2" / "__main__.py"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["lintul2", str(output)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert output.read_bytes() == b"ongewijzigd"


def test_cli_beschermt_aangepast_weerbestand(tmp_path, monkeypatch):
    from lintul2 import __main__ as cli

    weather = tmp_path / "ander_weer.dat"
    weather.write_bytes(b"ongewijzigd")
    monkeypatch.setattr(sys, "argv", ["lintul2", str(weather), "--weather", str(weather)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert weather.read_bytes() == b"ongewijzigd"
