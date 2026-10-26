from pathlib import Path

import pytest

from lintul2.weather import read_weather

ROOT = Path(__file__).resolve().parents[1]


def test_weerbestand_365_dagen_en_dag_58():
    weather = read_weather(ROOT / "NLD1.987")
    assert set(weather) == set(range(1, 366))
    day = weather[58]
    assert (day.station, day.year, day.day) == (1, 1987, 58)
    assert (day.rdd, day.tmmn, day.tmmx, day.vp, day.wn, day.rain) == (
        650000, 3.3, 10.2, 1.010, 3.9, 14.5,
    )


@pytest.mark.parametrize("record", [
    "1 1987 58 -99 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58 nan 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58 verkeerd 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58 650 3.3",
    "1 1987 0 650 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58.5 650 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58 650 3.3 10.2 1.010 3.9 14.5\n1 1987 58 650 3.3 10.2 1.010 3.9 14.5",
    "1 1987 58 650 3.3 10.2 1.010 3.9 14.5\n1 1988 59 650 3.3 10.2 1.010 3.9 14.5",
])
def test_ongeldige_weerregels_geven_fout(tmp_path, record):
    path = tmp_path / "weer.dat"
    path.write_text("* commentaar\n5.67 51.97 7 0 0\n" + record, encoding="ascii")
    with pytest.raises(ValueError):
        read_weather(path)


@pytest.mark.parametrize("text", ["", "* alleen commentaar", "1 2 3", "5.67 51.97 7 0 0"])
def test_ongeldige_of_lege_header_geeft_fout(tmp_path, text):
    path = tmp_path / "weer.dat"
    path.write_text(text, encoding="ascii")
    with pytest.raises(ValueError):
        read_weather(path)


def test_kwaliteitsregel_wordt_niet_als_meetdag_gebruikt(tmp_path):
    path = tmp_path / "weer.dat"
    path.write_text(
        "5.67 51.97 7 0 0\n"
        "-999 1987 74 3 3 3 3 3 3\n"
        "1 1987 74 3670 -5.7 5.0 0.590 3.5 1.2\n",
        encoding="ascii",
    )
    days = read_weather(path)
    assert list(days) == [74]
    assert days[74].rdd == 3670000
    assert days[74].rain == 1.2
