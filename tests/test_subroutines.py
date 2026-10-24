import pytest

from lintul2.subroutines import drunir, evaptr, gla


def test_gla_opkomst_overschrijft_juveniele_groei():
    assert gla(60, 60, 10, 0, 0.012, 0.009, 1, 0.022, 0, 5, 1, 0.36, 0.23) == 0.012


def test_gla_voor_opkomst_overschrijft_alle_groei():
    assert gla(59, 60, 10, 400, 0.012, 0.009, 1, 0.022, 1, 5, 1, 0.36, 0.23) == 0


def test_gla_exacte_nulvergelijking_en_strikte_watergrens():
    assert gla(60, 60, 10, 0, 0.012, 0.009, 1, 0.022, 0, 5, 1, 0.23, 0.23) == 0
    assert 0 < gla(60, 60, 10, 0, 0.012, 0.009, 1, 0.022, 1e-15, 5, 1, 0.36, 0.23) < 1e-15


def test_gla_maturatie_op_drempel():
    assert gla(100, 60, 10, 330, 0.012, 0.009, 1, 0.022, 0.5, 5, 1, 0.36, 0.23) == pytest.approx(0.11)


@pytest.mark.parametrize("wa,expected", [(80, (0, 0)), (230, (1.0714285714285714, 0)), (360, (2, 4)), (550, (2, 0))])
def test_evaptr_watergrenzen_volgens_formules(wa, expected):
    # Algebraische grensgevallen, geen verzonnen agronomische referentierun.
    assert evaptr(2, 4, 1, wa, 0.08, 0.23, 0.36, 0.48, 0.55, 8, 1) == pytest.approx(expected)


@pytest.mark.parametrize("rain,wa,irrigf,expected", [
    (0, 360, 1, (0, 0, 3)),
    (0, 360, 0, (0, 0, 0)),
    (10, 360, 1, (7, 0, 0)),
    (100, 550, 1, (50, 47, 0)),
])
def test_drunir_afvoer_en_beregening_volgens_formules(rain, wa, irrigf, expected):
    assert drunir(rain, 0, 1, 2, irrigf, 50, 1, wa, 1, 0.36, 0.55) == pytest.approx(expected)
