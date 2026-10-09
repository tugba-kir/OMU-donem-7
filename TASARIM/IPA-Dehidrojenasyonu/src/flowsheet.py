# -*- coding: utf-8 -*-
"""Akış şeması çözümü: akımlar, yardımcı akışkanlar, ısı yükleri."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *
from .thermo import *
from .params import *
from .columns import *

def flowsheet(par):
    X = par['X']; w = par['W_IPA_BESLEME']; P = par['P']
    f0 = np.array([w / MW[0], 0, 0, (1 - w) / MW[3]]); fresh = 100 * f0 / f0.sum()
    x_az = (par['AZ_WT'] / MW[0]) / (par['AZ_WT'] / MW[0] + (1 - par['AZ_WT']) / MW[3])
    w_ace = 1 - par['W_SU_URUN']
    rec = np.zeros(4)
    K_ace_a, gam_inf = K_ace_henry(par['T_ABS'], P[14])
    for it in range(500):
        feed = fresh + rec
        rxn = feed.copy(); r = X * feed[0]; rxn[0] -= r; rxn[1] += r; rxn[2] += r
        gas, liq = flash(rxn, par['T_FL'], P[10]); G = gas.sum()
        Ls = par['A_ABS'] * K_ace_a * G                                         # A = L/(K G)
        N = kremser_N(par['A_ABS'], par['REC_ACE_ABS'])
        rich = np.zeros(4); rich[1] = par['REC_ACE_ABS'] * gas[1]
        # IPA: aynı kademe sayısı N, kendi A_IPA (Wilson γ∞) ile Kremser geri kazanımı
        gin = gamma(np.array([1e-9, 1e-9, 1 - 2e-9]), par['T_ABS'])[0]
        A_i = Ls / (gin * Psat(0, par['T_ABS']) / P[14] * G); rec_i = (A_i ** (N + 1) - A_i) / (A_i ** (N + 1) - 1) if abs(A_i - 1) > 1e-9 else N / (N + 1)
        rich[0] = rec_i * gas[0]
        vent = np.zeros(4); vent[2] = gas[2]; vent[1] = gas[1] - rich[1]; vent[0] = gas[0] - rich[0]
        yw = Psat(3, par['T_ABS']) / P[13]; vent[3] = yw / (1 - yw) * (vent[0] + vent[1] + vent[2])
        rich[3] = Ls + gas[3] - vent[3]
        f1 = liq + rich
        D1 = np.zeros(4); D1[1] = par['REC_ACE_C1'] * f1[1]
        D1[3] = D1[1] * MW[1] * (1 - w_ace) / w_ace / MW[3]
        B1 = f1 - D1
        D2 = np.zeros(4); D2[1] = B1[1]; D2[0] = par['REC_IPA_C2'] * B1[0]; D2[3] = D2[0] * (1 - x_az) / x_az
        B2 = B1 - D2
        assert rich[3] > 0 and B1[3] > 0 and B1[0] >= 0 and B2[3] > 0
        if np.abs(D2 - rec).max() < 1e-11: break
        rec = D2
    cap = par['CAP_TON_YIL'] * 1000 / par['SAAT']; s = cap / (D1 @ MW)
    fresh, rec, feed, rxn, gas, liq, rich, vent, f1, D1, B1, D2, B2 = [v * s for v in (fresh, rec, feed, rxn, gas, liq, rich, vent, f1, D1, B1, D2, B2)]
    Ls *= s
    S = {}
    S[1] = mk(25, Z, fresh)
    # --- kolon sıcaklıkları (VLE'den) ---
    pc1, pc2 = par['P_COL1'], par['P_COL2']
    T_D1 = bubble_T(D1 / D1.sum(), pc1[0]); T_B1 = bubble_T(B1 / B1.sum(), pc1[1])
    T_D2 = bubble_T(D2 / D2.sum(), pc2[0]); T_B2 = bubble_T(B2 / B2.sum(), pc2[1])
    S[2] = mk(T_D2, Z, D2)
    S[3] = mk(T_liq_from_H(fresh + D2, Hs(S[1]) + Hs(S[2])), Z, fresh + D2)
    Vdot = float(((S[3]['L'] * MW) / RHO).sum()); dP = (P[4] - P[3]) * 100.0
    W_P101 = Vdot * dP / 3600.0 / par['ETA_POMPA']
    S[4] = mk(T_liq_from_H(feed, Hs(S[3]) + W_P101 * 3600), Z, feed)
    T5 = dew_T(feed, P[5]); S[5] = mk(T5, feed, Z)                                  # E-102 çıkışı: doygun buhar
    S[6] = mk(par['T_6'], feed, Z)                                                  # E-101 soğuk çıkış: kızgın buhar
    S[7] = mk(par['T_R'], rxn, Z)
    Q_E102 = (Hs(S[5]) - Hs(S[4])) / 3600
    Q_E101 = (Hs(S[6]) - Hs(S[5])) / 3600
    T8 = T_vap_from_H(rxn, Hs(S[7]) - Q_E101 * 3600); S[8] = mk(T8, rxn, Z)
    Q_R = (Hs(S[7]) - Hs(S[6])) / 3600; Q_F = Q_R
    S[9] = mk(par['T_FL'], gas, liq); Q_E103 = (Hs(S[8]) - Hs(S[9])) / 3600
    S[10] = mk(par['T_FL'], gas, Z); S[11] = mk(par['T_FL'], Z, liq)
    S[12] = mk(par['T_SU'], Z, np.array([0, 0, 0, Ls]))
    S[13] = mk(par['T_ABS'], vent, Z); S[14] = mk(par['T_ABS'], Z, rich)
    Q_abs = (Hs(S[10]) + Hs(S[12]) - Hs(S[13]) - Hs(S[14])) / 3600                 # absorberden çekilecek ısı (kW)
    # pump-around: 42 (T-101 -> P-103, 40 °C), 43 (P-103 -> E-109), 44 (E-109 -> T-101, 30 °C)
    c14 = rich / rich.sum(); dh = (c14 @ Hl_vec(par['T_PA_HOT']) - c14 @ Hl_vec(par['T_PA_COLD']))             # kJ/kmol... J/mol
    F_pa = Q_abs * 3600 / dh                                                         # kmol/h
    rho14 = 1.0 / np.sum((c14 * MW / (c14 @ MW)) / RHO); Vpa = F_pa * (c14 @ MW) / rho14
    W_P103 = Vpa * (0.5 * 100.0) / 3600.0 / par['ETA_POMPA']                         # ΔP=0.5 bar
    S[42] = mk(par['T_PA_HOT'], Z, F_pa * c14)
    S[43] = mk(T_liq_from_H(F_pa * c14, Hs(S[42]) + W_P103 * 3600), Z, F_pa * c14)
    S[44] = mk(par['T_PA_COLD'], Z, F_pa * c14)
    Q_E109 = (Hs(S[43]) - Hs(S[44])) / 3600
    S[15] = mk(T_liq_from_H(f1, Hs(S[11]) + Hs(S[14])), Z, f1)
    S[16] = mk(T_D1, Z, D1); S[18] = mk(T_B1, Z, B1); S[19] = mk(T_B2, Z, B2)
    lam = lambda comp, T: float(comp @ (Hv_vec(T) - Hl_vec(T)))
    # --- reflü: McCabe-Thiele Rmin (ikili Wilson) x RR_FACTOR
    z1 = f1[1] / (f1[1] + f1[3]); xD1 = D1[1] / (D1[1] + D1[3])
    Tb_f1 = bubble_T(f1 / f1.sum(), pc1[1]); q1 = 1.0 + (f1 @ CPL) * (Tb_f1 - S[15]['T']) / lam(f1, Tb_f1)
    Rmin1, xq1 = rmin_binary(xD1, z1, q1, pc1[1], (1, 3)); R1 = par['RR_FACTOR'] * Rmin1
    z2 = B1[0] / (B1[0] + B1[3]); xD2 = D2[0] / (D2[0] + D2[3])
    Tb_f2 = bubble_T(B1 / B1.sum(), pc2[1]); q2 = 1.0 + (B1 @ CPL) * (Tb_f2 - S[18]['T']) / lam(B1, Tb_f2)
    Rmin2, xq2 = rmin_binary(xD2, z2, q2, pc2[1], (0, 3)); R2 = par['RR_FACTOR'] * Rmin2
    Q_C1 = (R1 + 1) * lam(D1, T_D1) / 3600
    Q_B1 = Q_C1 + (Hs(S[16]) + Hs(S[18]) - Hs(S[15])) / 3600
    Q_C2 = (R2 + 1) * lam(D2, T_D2) / 3600
    Q_B2 = Q_C2 + (Hs(S[19]) + Hs(S[2]) - Hs(S[18])) / 3600
    S[17] = mk(25, Z, D1); Q_E108 = (Hs(S[16]) - Hs(S[17])) / 3600

    # --- kolon iç akımları: üst buhar (doygun), reflü (doygun sıvı), rebolyere sıvı, kaynatma buharı
    def col_streams(D, B, Rr, T_D, T_B, P_bot, QB_kW, ids):
        iv, ic, ir, il, ib = ids
        Sv = mk(T_D, (Rr + 1) * D, Z); Sc = mk(T_D, Z, (Rr + 1) * D); Sr = mk(T_D, Z, Rr * D)
        y = vap_eq(B, T_B, P_bot); lam_y = float(y @ (Hv_vec(T_B) - Hl_vec(T_B)))        # J/mol
        Vb = QB_kW * 3600.0 / lam_y                                                       # kmol/h
        Sb = mk(T_B, Vb * y, Z); Sl = mk(T_B, Z, Vb * y + B)
        return {iv: Sv, ic: Sc, ir: Sr, il: Sl, ib: Sb}
    S.update(col_streams(D1, B1, R1, T_D1, T_B1, pc1[1], Q_B1, (45, 46, 47, 48, 49)))
    S.update(col_streams(D2, B2, R2, T_D2, T_B2, pc2[1], Q_B2, (50, 51, 52, 53, 54)))
    # --- yardımcı akışkan akımları ---
    steam = lambda q: q * 3600 / H_FG_LPS                                 # kg/h LPS
    cw = lambda q: abs(q) * 3600 / (CP_SU * 10.0)                         # kg/h, 25->35 °C
    U = {}
    U[20] = ('LPS 4 bar(a), doygun buhar', 'E-102 giriş', T_LPS, 4.0, steam(Q_E102))
    U[21] = ('LPS yoğuşuğu', 'E-102 çıkış', T_LPS, 4.0, steam(Q_E102))
    U[22] = ('LPS 4 bar(a), doygun buhar', 'E-105 giriş', T_LPS, 4.0, steam(Q_B1))
    U[23] = ('LPS yoğuşuğu', 'E-105 çıkış', T_LPS, 4.0, steam(Q_B1))
    U[24] = ('LPS 4 bar(a), doygun buhar', 'E-107 giriş', T_LPS, 4.0, steam(Q_B2))
    U[25] = ('LPS yoğuşuğu', 'E-107 çıkış', T_LPS, 4.0, steam(Q_B2))
    for k, (code, q, fl, ti, to) in enumerate([('E-103', Q_E103, 'Soğutma suyu (cw)', 25.0, 35.0), ('E-109', Q_E109, 'Soğutma suyu (cw)', 25.0, 35.0),
                                              ('E-104', Q_C1, 'Soğutma suyu (cw)', 25.0, 35.0), ('E-106', Q_C2, 'Soğutma suyu (cw)', 25.0, 35.0),
                                              ('E-108', Q_E108, 'Soğutulmuş su (chw)', 7.0, 12.0)]):
        m_ = abs(q) * 3600 / (CP_SU * (to - ti))
        U[26 + 2 * k] = (fl, code + ' giriş', ti, 4.0, m_)
        U[27 + 2 * k] = (fl, code + ' çıkış', to, 3.7, m_)
    # fırın: yakıt (CH4), hava, baca gazı, erimiş tuz
    Q_fuel = Q_F / par['ETA_FIRIN']; n_fuel = Q_fuel * 3.6 / LHV_CH4                 # kmol/h  (kW*3.6=MJ/h ; /(kJ/mol)=kmol/h)
    n_O2 = 2 * n_fuel * (1 + par['EXCESS_AIR']); n_air = n_O2 / 0.21
    flue = dict(CO2=n_fuel, H2O=2 * n_fuel, O2=n_O2 - 2 * n_fuel, N2=n_air * 0.79)
    m_fuel = n_fuel * MW_CH4; m_air = n_air * MW_AIR
    m_flue = flue['CO2'] * 44.009 + flue['H2O'] * 18.015 + flue['O2'] * 31.998 + flue['N2'] * 28.014
    m_salt = Q_R * 3600 / (par['CP_SALT'] * (par['T_SALT_HOT'] - par['T_SALT_COLD']))
    U[36] = ('Doğal gaz (CH4)', 'F-101 giriş', par['T_FUEL'], 4.0, m_fuel)
    U[37] = ('Hava (%15 fazla)', 'F-101 giriş', par['T_AIR'], 1.0, m_air)
    U[38] = ('Baca gazı (CO2, H2O, O2, N2)', 'F-101 çıkış', par['T_FLUE'], 1.0, m_flue)
    U[39] = ('Erimiş tuz (sıcak)', 'F-101 -> R-101', par['T_SALT_HOT'], 2.0, m_salt)
    U[40] = ('Erimiş tuz (soğuk)', 'R-101 -> P-102', par['T_SALT_COLD'], 1.5, m_salt)
    U[41] = ('Erimiş tuz (soğuk, basınçlı)', 'P-102 -> F-101', par['T_SALT_COLD'], 3.0, m_salt)
    duties = dict(P101=W_P101, E102=Q_E102, E101=Q_E101, R101=Q_R, F101=Q_F, E103=-Q_E103, T101=-Q_abs, P103=W_P103, E109=-Q_E109,
                  E104=-Q_C1, E105=Q_B1, E106=-Q_C2, E107=Q_B2, E108=-Q_E108)
    extra = dict(R1=R1, Rmin1=Rmin1, R2=R2, Rmin2=Rmin2, q1=q1, q2=q2, xD1=xD1, xD2=xD2, z1=z1, z2=z2, N_abs=N, A=par['A_ABS'],
                 gam_inf_ace=gam_inf, K_ace=K_ace_a, rec_ipa_abs=rec_i, Q_fuel=Q_fuel, n_fuel=n_fuel, flue=flue, m_fuel=m_fuel, m_air=m_air,
                 m_flue=m_flue, m_salt=m_salt, F_pa=F_pa, x_az=x_az, T5=T5, T8=T8, T_D1=T_D1, T_B1=T_B1, T_D2=T_D2, T_B2=T_B2,
                 scale=s, iters=it, recycle_ratio=rec[0] / fresh[0], Ls=Ls, prod_kg_h=D1 @ MW, fresh=fresh, W_P103=W_P103)
    return S, duties, U, extra


__all__ = [_n for _n in dir() if not _n.startswith('__')]
