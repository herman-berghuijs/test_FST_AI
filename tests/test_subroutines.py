import pytest

from lintul2.subroutines import drunir, evaptr, gla


def test_gla_opkomst_overschrijft_juveniele_groei():
    assert gla(
        time=60, doyem=60, dteff=10, tsum=0, laii=0.012, rgrl=0.009,
        delt=1, sla=0.022, lai=0, glv=5, tranrf=1, wc=0.36, wcwp=0.23,
    ) == 0.012


def test_gla_voor_opkomst_overschrijft_alle_groei():
    assert gla(
        time=59, doyem=60, dteff=10, tsum=400, laii=0.012, rgrl=0.009,
        delt=1, sla=0.022, lai=1, glv=5, tranrf=1, wc=0.36, wcwp=0.23,
    ) == 0


def test_gla_exacte_nulvergelijking_en_strikte_watergrens():
    assert gla(
        time=60, doyem=60, dteff=10, tsum=0, laii=0.012, rgrl=0.009,
        delt=1, sla=0.022, lai=0, glv=5, tranrf=1, wc=0.23, wcwp=0.23,
    ) == 0
    assert 0 < gla(
        time=60, doyem=60, dteff=10, tsum=0, laii=0.012, rgrl=0.009,
        delt=1, sla=0.022, lai=1e-15, glv=5, tranrf=1, wc=0.36, wcwp=0.23,
    ) < 1e-15


def test_gla_maturatie_op_drempel():
    assert gla(
        time=100, doyem=60, dteff=10, tsum=330, laii=0.012, rgrl=0.009,
        delt=1, sla=0.022, lai=0.5, glv=5, tranrf=1, wc=0.36, wcwp=0.23,
    ) == pytest.approx(0.11)


@pytest.mark.parametrize("wa,expected", [(80, (0, 0)), (230, (1.0714285714285714, 0)), (360, (2, 4)), (550, (2, 0))])
def test_evaptr_watergrenzen_volgens_formules(wa, expected):
    # Algebraische grensgevallen, geen verzonnen agronomische referentierun.
    assert evaptr(
        pevap=2, ptran=4, rootd=1, wa=wa, wcad=0.08, wcwp=0.23,
        wcfc=0.36, wcwet=0.48, wcst=0.55, tranco=8, delt=1,
    ) == pytest.approx(expected)


@pytest.mark.parametrize("rain,wa,irrigf,expected", [
    (0, 360, 1, (0, 0, 3)),
    (0, 360, 0, (0, 0, 0)),
    (10, 360, 1, (7, 0, 0)),
    (100, 550, 1, (50, 47, 0)),
])
def test_drunir_afvoer_en_beregening_volgens_formules(rain, wa, irrigf, expected):
    assert drunir(
        rain=rain, rnintc=0, evap=1, tran=2, irrigf=irrigf, drate=50,
        delt=1, wa=wa, rootd=1, wcfc=0.36, wcst=0.55,
    ) == pytest.approx(expected)
