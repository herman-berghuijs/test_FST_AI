"""Rechtstreekse vertaling van de vier Fortran-subroutines in LINTUL2.FST."""

from math import exp

from .fst_functions import limit, notnul


def gla(
    time: float,
    doyem: float,
    dteff: float,
    tsum: float,
    laii: float,
    rgrl: float,
    delt: float,
    sla: float,
    lai: float,
    glv: float,
    tranrf: float,
    wc: float,
    wcwp: float,
) -> float:
    """Bereken de dagelijkse bladoppervlaktetoename GLAI in m2/m2/d.

    TIME en DOYEM zijn dagnummers; DELT is in dagen, DTEFF in graden Celsius
    en TSUM in graaddagen. LAI en LAII zijn in m2/m2, RGRL per graaddag,
    SLA in m2/g en GLV in g/m2/d. TRANRF is dimensieloos; WC en WCWP in m3/m3.
    """
    # 1-op-1 port: vaste getallen blijven letterlijk staan; VERBETERSUGGESTIES.md #2.
    glai = sla * glv
    if tsum < 330.0 and lai < 0.75:
        glai = lai * (exp(rgrl * dteff * delt) - 1.0) / delt * tranrf
    # 1-op-1 port: exacte nulvergelijking en overschrijfvolgorde; VERBETERSUGGESTIES.md #6.
    if time >= doyem and lai == 0.0 and wc > wcwp:
        glai = laii / delt
    if time < doyem:
        glai = 0.0
    return glai


def penman(
    davtmp: float,
    vp: float,
    dtr: float,
    lai: float,
    wn: float,
    rnintc: float,
) -> tuple[float, float]:
    """Bereken potentiele verdamping (PEVAP, PTRAN), beide in mm/d.

    DAVTMP is in graden Celsius, VP in kPa, DTR in MJ/m2/d, LAI in m2/m2,
    WN in m/s en RNINTC in mm/d.
    """
    # 1-op-1 port: vaste getallen niet geparametriseerd; VERBETERSUGGESTIES.md #2.
    dtrjm2 = dtr * 1.0e6
    boltzm = 5.668e-8
    lhvap = 2.4e6
    psych = 0.067
    bbrad = boltzm * (davtmp + 273.0)**4 * 86400.0
    svp = 0.611 * exp(17.4 * davtmp / (davtmp + 239.0))
    slope = 4158.6 * svp / (davtmp + 239.0)**2
    rlwn = bbrad * max(0.0, 0.55 * (1.0 - vp / svp))
    nrads = dtrjm2 * (1.0 - 0.15) - rlwn
    nradc = dtrjm2 * (1.0 - 0.25) - rlwn
    penmrs = nrads * slope / (slope + psych)
    penmrc = nradc * slope / (slope + psych)
    wdf = 2.63 * (1.0 + 0.54 * wn)
    penmd = lhvap * wdf * (svp - vp) * psych / (slope + psych)
    pevap = exp(-0.5 * lai) * (penmrs + penmd) / lhvap
    ptran = (1.0 - exp(-0.5 * lai)) * (penmrc + penmd) / lhvap
    ptran = max(0.0, ptran - 0.5 * rnintc)
    return pevap, ptran


def evaptr(
    pevap: float,
    ptran: float,
    rootd: float,
    wa: float,
    wcad: float,
    wcwp: float,
    wcfc: float,
    wcwet: float,
    wcst: float,
    tranco: float,
    delt: float,
) -> tuple[float, float]:
    """Bereken actuele bodemverdamping en transpiratie (EVAP, TRAN) in mm/d.

    PEVAP, PTRAN en TRANCO zijn in mm/d, ROOTD in m, WA in mm en DELT in dagen.
    WCAD, WCWP, WCFC, WCWET en WCST zijn volumetrische vochtgehalten in m3/m3.
    """
    wc = 0.001 * wa / rootd
    waad = 1000.0 * wcad * rootd
    evap = pevap * limit(0.0, 1.0, (wc - wcad) / (wcfc - wcad))
    wccr = wcwp + max(0.01, ptran / (ptran + tranco) * (wcfc - wcwp))
    if wc > wccr:
        fr = limit(0.0, 1.0, (wcst - wc) / (wcst - wcwet))
    else:
        fr = limit(0.0, 1.0, (wc - wcwp) / (wccr - wcwp))
    tran = ptran * fr
    availf = min(1.0, ((wa - waad) / delt) / notnul(evap + tran))
    evap = evap * availf
    tran = tran * availf
    return evap, tran


def drunir(
    rain: float,
    rnintc: float,
    evap: float,
    tran: float,
    irrigf: float,
    drate: float,
    delt: float,
    wa: float,
    rootd: float,
    wcfc: float,
    wcst: float,
) -> tuple[float, float, float]:
    """Bereken drainage, afstroming en beregening (DRAIN, RUNOFF, IRRIG) in mm/d.

    RAIN, RNINTC, EVAP, TRAN en DRATE zijn in mm/d, WA in mm, ROOTD in m
    en DELT in dagen. WCFC en WCST zijn in m3/m3; IRRIGF is dimensieloos.
    """
    wafc = 1000.0 * wcfc * rootd
    wast = 1000.0 * wcst * rootd
    drain = limit(0.0, drate, (wa - wafc) / delt + (rain - rnintc - evap - tran))
    runoff = max(0.0, (wa - wast) / delt + (rain - rnintc - evap - tran - drain))
    irrig = irrigf * max(
        0.0, (wafc - wa) / delt - (rain - rnintc - evap - tran - drain - runoff)
    )
    return drain, runoff, irrig
