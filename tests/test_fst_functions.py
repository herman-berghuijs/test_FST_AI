import pytest

from lintul2.fst_functions import afgen, insw, limit, notnul, reaand


@pytest.mark.parametrize("x,expected", [(-1, 2), (0, 2), (1, 4), (2, 6), (4, 5), (6, 4), (7, 4)])
def test_afgen_knikpunten_en_grenzen(x, expected):
    assert afgen(((0, 2), (2, 6), (6, 4)), x) == expected


@pytest.mark.parametrize("x,expected", [(-1, 7), (0, 9), (1, 9)])
def test_insw_nul_kiest_tweede_tak(x, expected):
    assert insw(x, 7, 9) == expected


@pytest.mark.parametrize("x,y,expected", [(1, 2, 1), (0, 2, 0), (2, 0, 0), (-1, 2, 0), (2, -1, 0)])
def test_reaand_strikt_positief(x, y, expected):
    assert reaand(x, y) == expected


@pytest.mark.parametrize("x,expected", [(-1, 0), (0, 0), (0.5, 0.5), (1, 1), (2, 1)])
def test_limit_begrenst(x, expected):
    assert limit(0, 1, x) == expected


@pytest.mark.parametrize("x,expected", [(0, 1), (-0.0, 1), (2, 2), (-2, -2)])
def test_notnul_vervangt_alleen_nul(x, expected):
    assert notnul(x) == expected
