"""Dagelijkse rates, uitvoer en rechthoekige Euler-integratie van FST."""

from collections.abc import Mapping
from math import exp

from . import parameters as p
from .fst_functions import afgen, insw, limit, notnul, reaand
from .subroutines import drunir, evaptr, gla, penman
from .weather import Weather

COLUMNS = (
    "TIME", "LAI", "WSOTHA", "WSO", "WST", "WLV", "WRT", "TSUM", "DAVTMP",
    "DTR", "ROOTD", "TRAN", "EVAP", "TRANRF", "WA", "WC", "YEAR", "RAIN", "TRAIN",
)


def simulate(weather: Mapping[int, Weather]) -> list[dict[str, float]]:
    """Bereken de standaardrun; alle rates gebruiken de toestand op tijd t.

    WEATHER bevat dagweer per dagnummer. Retourneer uitvoerregels met de
    FST-kolomnamen uit COLUMNS; de eenheden staan in de README.
    """
    time = p.sttime  # FST 1
    lai = tsum = wlvd = wst = wso = wrt = train = p.zero  # FST 1, 2, 3, 5
    wlvg = p.wlvi  # FST 1, 5
    rootd = p.rootdi  # FST 1, 5
    wa = p.wai  # FST 1, 6
    rows = []
    while time <= p.fintim:  # FST 1
        met = weather[int(time)]  # FST 2
        dtr = met.rdd / 1.0e6  # FST 2
        davtmp = 0.5 * (met.tmmn + met.tmmx)  # FST 2
        dteff = max(0.0, davtmp - p.tbase)  # FST 2
        wc = 0.001 * wa / rootd  # FST 6
        # 1-op-1 port: opkomstconstructie behouden; VERBETERSUGGESTIES.md #6.
        emerg = max(reaand(time - p.doyem + 1.0, wc - p.wcwp), insw(-lai, 1.0, 0.0))  # FST 2
        rtsum = dteff * emerg  # FST 2
        # 1-op-1 port: overschrijding ROOTDM behouden; VERBETERSUGGESTIES.md #5.
        # TSUMAN houdt zijn dubbele functie; VERBETERSUGGESTIES.md #4.
        rrootd = p.rrdmax * insw(wc - p.wcwp, 0.0, 1.0) * reaand(
            p.rootdm - rootd, p.tsuman - tsum
        ) * emerg  # FST 5
        explor = 1000.0 * rrootd * p.wcfc  # FST 6
        # 1-op-1 port: vaste factoren blijven staan; VERBETERSUGGESTIES.md #2.
        rnintc = min(met.rain, 0.25 * lai)  # FST 6
        pevap, ptran = penman(davtmp, met.vp, dtr, lai, met.wn, rnintc)  # FST 6
        evap, tran = evaptr(
            pevap=pevap,
            ptran=ptran,
            rootd=rootd,
            wa=wa,
            wcad=p.wcad,
            wcwp=p.wcwp,
            wcfc=p.wcfc,
            wcwet=p.wcwet,
            wcst=p.wcst,
            tranco=p.tranco,
            delt=p.delt,
        )  # FST 6
        tranrf = tran / notnul(ptran)  # FST 6
        drain, runoff, irrig = drunir(
            rain=met.rain,
            rnintc=rnintc,
            evap=evap,
            tran=tran,
            irrigf=p.irrigf,
            drate=p.drate,
            delt=p.delt,
            wa=wa,
            rootd=rootd,
            wcfc=p.wcfc,
            wcst=p.wcst,
        )  # FST 6
        rwa = (met.rain + explor + irrig) - (rnintc + runoff + tran + evap + drain)  # FST 6
        parint = 0.5 * dtr * (1.0 - exp(-p.k * lai))  # FST 4
        gtotal = p.lue * parint * tranrf  # FST 4
        frtwet = afgen(p.frttb, tsum)  # FST 5
        frtmod = max(1.0, 1.0 / (tranrf + 0.5))  # FST 5
        frt = frtwet * frtmod  # FST 5
        fshmod = (1.0 - frt) / (1.0 - frt / frtmod)  # FST 5
        flv = afgen(p.flvtb, tsum) * fshmod  # FST 5
        fst = afgen(p.fsttb, tsum) * fshmod  # FST 5
        fso = afgen(p.fsotb, tsum) * fshmod  # FST 5
        glv = flv * gtotal  # FST 3
        glai = gla(
            time=time,
            doyem=p.doyem,
            dteff=dteff,
            tsum=tsum,
            laii=p.laii,
            rgrl=p.rgrl,
            delt=p.delt,
            sla=p.sla,
            lai=lai,
            glv=glv,
            tranrf=tranrf,
            wc=wc,
            wcwp=p.wcwp,
        )  # FST 3
        rdrdv = insw(tsum - p.tsuman, 0.0, afgen(p.rdrt, davtmp))  # FST 3
        rdrsh = limit(0.0, p.rdrshm, p.rdrshm * (lai - p.laicr) / p.laicr)  # FST 3
        rdr = max(rdrdv, rdrsh)  # FST 3
        dlai = lai * rdr  # FST 3
        dlv = wlvg * rdr  # FST 3
        rlai = glai - dlai  # FST 3
        wlv = wlvg + wlvd  # FST 5
        wsotha = wso / 100.0  # FST 5
        rwlvg = gtotal * flv - dlv  # FST 5
        rwst = gtotal * fst  # FST 5
        rwso = gtotal * fso  # FST 5
        rwrt = gtotal * frt  # FST 5
        finished = tsum > 2080.0  # FST 1
        if (time - p.sttime) % p.prdel == 0 or finished or time == p.fintim:  # FST 1
            rows.append(dict(zip(COLUMNS, (
                time, lai, wsotha, wso, wst, wlv, wrt, tsum, davtmp, dtr,
                rootd, tran, evap, tranrf, wa, wc, float(met.year), met.rain, train,
            ), strict=True)))  # FST 1
        if finished:  # FST 1
            break
        lai += rlai * p.delt  # FST 3
        tsum += rtsum * p.delt  # FST 2
        wlvg += rwlvg * p.delt  # FST 5
        wlvd += dlv * p.delt  # FST 5
        wst += rwst * p.delt  # FST 5
        wso += rwso * p.delt  # FST 5
        wrt += rwrt * p.delt  # FST 5
        rootd += rrootd * p.delt  # FST 5
        wa += rwa * p.delt  # FST 6
        train += met.rain * p.delt  # FST 2
        time += p.delt  # FST 1
    return rows
