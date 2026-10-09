# -*- coding: utf-8 -*-
"""Birim bazlı kütle/enerji denklikleri, genel kontroller, akım ve ekipman tabloları."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *
from .thermo import *
from .params import *
from .columns import *
from .flowsheet import *

def unit_balances(S, D, U, E, par):
    """Her ekipman için: giriş/çıkış akımları, ısı/iş (kW, + = üniteye giriş), kütle ve enerji kapanışı"""
    h = lambda ks: sum(Hs(S[k]) for k in ks) / 3600.0          # kW
    m = lambda ks: sum(kg(S[k]) for k in ks)
    units = [
     ('V-100',       'Besleme tankı: taze besleme ile geri dönüşü karıştırır (adyabatik)', [1, 2], [3], 0.0),
     ('P-101',       'Besleme pompası: 1 -> 3,2 bar (mil işi tüm akışkana)', [3], [4], D['P101']),
     ('E-102',       'Buharlaştırıcı: LPS ile doygun buhar', [4], [5], D['E102']),
     ('E-101',       'Besleme/çıkış ısı değiştirici (soğuk: 5->6, sıcak: 7->8)', [5, 7], [6, 8], 0.0),
     ('R-101',       'Reaktör: kızgın buhar + tuzdan ısı; IPA -> aseton + H2', [6], [7], D['R101']),
     ('E-103',       'Reaktör çıkış soğutucusu/yoğuşturucusu (cw)', [8], [9], D['E103']),
     ('V-101',       'Flaş tankı: 40 °C, buhar-sıvı ayrımı (adyabatik)', [9], [10, 11], 0.0),
     ('T-101+E-109+P-103', 'Gaz yıkama kolonu (pump-around soğutuculu): H2 vent, aseton suda', [10, 12, 44], [13, 14, 42], 0.0),
     ('P-103',       'Pump-around pompası', [42], [43], D['P103']),
     ('E-109',       'Pump-around soğutucusu (cw)', [43], [44], D['E109']),
     (f'Karışım({nn(15)})', 'Akım 11 + 14 birleşimi (adyabatik, C-101 beslemesi)', [11, 14], [15], 0.0),
     ('C-101+E-104+E-105', 'Aseton kolonu (kolon+yoğuşturucu+rebolyer): üst ürün aseton, dip su/IPA', [15], [16, 18], D['E105'] + D['E104']),
     ('E-104', 'C-101 tam yoğuşturucu: 45 -> 46 (doygun sıvı, cw)', [45], [46], D['E104']),
     (f'Ayrım({nn(46)})', 'Yoğuşan sıvının ayrımı: 46 -> 47 (reflü) + 16 (ürün)', [46], [47, 16], 0.0),
     ('E-105', 'C-101 rebolyer: 48 -> 49 + 18 (LPS)', [48], [49, 18], D['E105']),
     ('E-108',       'Ürün soğutucusu: 16 -> 25 °C (cw)', [16], [17], D['E108']),
     ('C-102+E-106+E-107', 'IPA kolonu (kolon+yoğuşturucu+rebolyer): üst azeotrop (geri dönüş), dip atık su', [18], [2, 19], D['E107'] + D['E106']),
     ('E-106', 'C-102 tam yoğuşturucu: 50 -> 51 (doygun sıvı, cw)', [50], [51], D['E106']),
     (f'Ayrım({nn(51)})', 'Yoğuşan sıvının ayrımı: 51 -> 52 (reflü) + 2 (geri dönüş)', [51], [52, 2], 0.0),
     ('E-107', 'C-102 rebolyer: 53 -> 54 + 19 (LPS)', [53], [54, 19], D['E107']),
    ]
    rows = []
    for name, why, ins, outs, q in units:
        mi, mo = m(ins), m(outs); ei = h(ins) + q; eo = h(outs)
        rows.append(dict(Ekipman=name, Neden=why, Giris=','.join(str(nn(k)) for k in ins), Cikis=','.join(str(nn(k)) for k in outs), Q_kW=q,
                         m_in=mi, m_out=mo, dm=mi - mo, hata_pct=100 * (mi - mo) / mi, E_in=ei, E_out=eo, dE=ei - eo))
    return pd.DataFrame(rows)

def overall_checks(S, D, U, E, par):
    # tüm sistem: giriş = S1+S12 + (P101+P103 işi) + E102+R101(F101)+E105+E107 ; çıkış = S13+S17+S19 + soğutmalar(E103,E109,E104,E106,E108)
    inn = Hs(S[1]) / 3600 + Hs(S[12]) / 3600 + D['P101'] + D['P103'] + D['E102'] + D['R101'] + D['E105'] + D['E107']
    out = Hs(S[13]) / 3600 + Hs(S[17]) / 3600 + Hs(S[19]) / 3600 - D['E103'] - D['E109'] - D['E104'] - D['E106'] - D['E108']
    ELEM = np.array([[3, 3, 0, 0], [8, 6, 2, 2], [1, 1, 0, 1]], float)
    el_in = ELEM @ (mol(S[1]) + mol(S[12])); el_out = ELEM @ (mol(S[13]) + mol(S[17]) + mol(S[19]))
    # reaksiyon denge kontrolü
    dH = lambda T: Hv_vec(T)[1] + Hv_vec(T)[2] - Hv_vec(T)[0]
    SH2 = (SHO_H2[0] * np.log(0.29815) + SHO_H2[1] * 0.29815 + SHO_H2[2] * 0.29815 ** 2 / 2 + SHO_H2[3] * 0.29815 ** 3 / 3
           - SHO_H2[4] / (2 * 0.29815 ** 2) + 172.707974)
    dS = S298['ACE'] + SH2 - S298['IPA']; dG298 = dH(25.0) - T_REF * dS
    Ts = np.linspace(T_REF, par['T_R'] + 273.15, 400)
    integ = (getattr(np, 'trapezoid', None) or np.trapz)([dH(t - 273.15) / (R_GAS * t ** 2) for t in Ts], Ts)
    Keq = np.exp(-dG298 / (R_GAS * T_REF) + integ); Pr = par['P'][7]; n0 = S[6]['V']
    fe = lambda e: (n0[1] + e) * (n0[2] + e) * Pr / ((n0[0] - e) * (n0.sum() + e)) - Keq
    X_eq = brentq(fe, 1e-9, n0[0] - 1e-9) / n0[0]
    Keq25 = np.exp(-dG298 / (R_GAS * T_REF))
    w_water = float(S[17]['L'][3] * MW[3] / kg(S[17]))
    return dict(E_in=inn, E_out=out, E_err=inn - out, mass_in=kg(S[1]) + kg(S[12]), mass_out=kg(S[13]) + kg(S[17]) + kg(S[19]),
                el_in=el_in, el_out=el_out, dH25=dH(25.0) / 1000, dH350=dH(par['T_R']) / 1000, Keq=Keq, X_eq=X_eq, Keq25=Keq25, dG298=dG298 / 1000,
                w_water_prod=w_water, w_ipa_prod=float(S[17]['L'][0] * MW[0] / kg(S[17])))

def stream_table(S, P):
    rows = []
    for k in sorted(S):
        st = S[k]; n = st['V'] + st['L']; N = n.sum()
        rows.append(dict(AkimNo=k, T_C=st['T'], P_bar=P.get(k, np.nan), BuharOrani=st['V'].sum() / N, kg_h=float(n @ MW), kmol_h=N,
                         IPA=n[0], Aseton=n[1], H2=n[2], Su=n[3]))
    return pd.DataFrame(rows).set_index('AkimNo')



EQUIP = [  # kod, ad, tip, işlev, görev anahtarı, utility
 ('V-100', 'Besleme tankı', 'Yatay tank', 'IPA/su besleme ve geri dönüşü karıştırır', None, '-'),
 ('P-101A/B', 'Besleme pompası', 'Santrifüj pompa (1 çalışan + 1 yedek)', 'Sıvı beslemeyi 100 kPa → 320 kPa basar', 'P101', 'Elektrik'),
 ('E-102', 'Buharlaştırıcı', 'Kabuk-boru ısı değiştirici', 'Beslemeyi doygun buhara çevirir', 'E102', 'LPS'),
 ('E-101', 'Besleme/çıkış ısı değiştirici', 'Kabuk-boru ısı değiştirici', 'Besleme buharını reaktör çıkışıyla kızdırır', 'E101', 'Proses-proses'),
 ('R-101', 'Dehidrojenasyon reaktörü', 'Çok borulu katalitik reaktör', 'IPA → aseton + H2, 350 °C, X=%90', 'R101', 'Erimiş tuz'),
 ('F-101', 'Tuz ısıtıcı fırın', 'Gaz yakıtlı fırın', 'Erimiş tuzu ısıtır', 'F101', 'Fuel gas + hava'),
 ('P-102', 'Tuz pompası', 'Pompa', 'Erimiş tuzu dolaştırır', None, 'Elektrik'),
 ('E-103', 'Reaktör çıkış soğutucusu', 'Kabuk-boru ısı değiştirici', 'Çıkışı 40 °C\'ye soğutur, kısmen yoğuşturur', 'E103', 'cw'),
 ('V-101', 'Flaş tankı', 'Dikey ayırıcı', 'Gaz ve sıvıyı ayırır (40 °C)', None, '-'),
 ('T-101', 'Gaz yıkama kolonu', 'Dolgulu/tepsili absorber', 'Gazdaki asetonu suyla yıkar', 'T101', 'E-109 ile soğutulur'),
 ('P-103', 'Pump-around pompası', 'Pompa', 'T-101 soğutma devrini dolaştırır', 'P103', 'Elektrik'),
 ('E-109', 'Pump-around soğutucusu', 'Kabuk-boru ısı değiştirici', 'Absorber ısısını alır', 'E109', 'cw'),
 ('C-101', 'Aseton kolonu', 'Tepsili damıtma kolonu', 'Üstten aseton (%99,6), dipten su/IPA', None, '-'),
 ('E-104', 'C-101 yoğuşturucu', 'Kabuk-boru ısı değiştirici', 'Üst buharı tam yoğuşturur', 'E104', 'cw'),
 ('E-105', 'C-101 rebolyer', 'Kabuk-boru ısı değiştirici', 'Kaynatma buharı üretir', 'E105', 'LPS'),
 ('E-108', 'Ürün soğutucu', 'Kabuk-boru ısı değiştirici', 'Asetonu 25 °C\'ye soğutur', 'E108', 'chw'),
 ('C-102', 'IPA kolonu', 'Tepsili damıtma kolonu', 'Üstten IPA/su azeotropu, dipten su', None, '-'),
 ('E-106', 'C-102 yoğuşturucu', 'Kabuk-boru ısı değiştirici', 'Üst buharı tam yoğuşturur', 'E106', 'cw'),
 ('E-107', 'C-102 rebolyer', 'Kabuk-boru ısı değiştirici', 'Kaynatma buharı üretir', 'E107', 'LPS'),
]
def equipment_table(D, ex):
    dtm = {r.Ekipman: r.dT_min for _, r in ex.iterrows()}
    rows = []
    for code, ad, tip, isl, key, ut in EQUIP:
        q = D[key] if key else None
        rows.append(dict(Kod=code, Ad=ad, Tip=tip, Islev=isl, Gorev_kW=(f4(q) if q is not None else '-'), Utility=ut,
                         dTmin=(f4(dtm[code]) if code in dtm else '-')))
    return pd.DataFrame(rows)


__all__ = [_n for _n in dir() if not _n.startswith('__')]
