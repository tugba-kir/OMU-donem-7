# -*- coding: utf-8 -*-
"""Termodinamik: buhar basıncı, Wilson aktivite katsayısı, kabarcık/çiğ noktası, flaş, entalpi."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *

def _sho_int(c, TK):
    A, B, C, D, E = c
    I = lambda t: A * t + B * t ** 2 / 2 + C * t ** 3 / 3 + D * t ** 4 / 4 - E / t
    return (I(TK / 1000.) - I(T_REF / 1000.)) * 1000.0
def _sho_cp(c, TK):
    A, B, C, D, E = c; t = TK / 1000.
    return A + B * t + C * t ** 2 + D * t ** 3 + E / t ** 2
def cpv(i, TK): return [P_IPA(TK), P_ACE(TK), _sho_cp(SHO_H2, TK), _sho_cp(SHO_H2O, TK)][i]
def _poly_int(P, TK): return P.integ()(TK) - P.integ()(T_REF)
def Hv_vec(Tc):
    TK = Tc + 273.15
    return HFV + np.array([_poly_int(P_IPA, TK), _poly_int(P_ACE, TK), _sho_int(SHO_H2, TK), _sho_int(SHO_H2O, TK)])
def Hl_vec(Tc): return HFL + CPL * (Tc - 25.0)

# Buhar basıncı (bar)
def Psat(i, Tc):
    if i == 0: return 10 ** (8.11778 - 1580.92 / (219.61 + Tc)) * 0.00133322          # IPA
    if i == 3: return 10 ** (8.07131 - 1730.63 / (233.426 + Tc)) * 0.00133322         # su
    if i == 1: return 10 ** (4.42448 - 1312.253 / (Tc + 273.15 - 32.445))             # aseton (NIST/Ambrose) bar,K
    raise ValueError
R_GAS = 8.314
S298 = dict(IPA=309.2, ACE=295.35)         # J/mol/K  (IPA 309.2, aseton 295.3: NIST gaz S°)
H_FG_LPS, T_LPS = 2133.0, 143.6            # kJ/kg, °C  4 bar(a) doygun buhar (buhar tablosu) [DOGRULANDI]
CP_SU = 4.18                               # kJ/kg/K
# Doğal gaz (CH4) alt ısıl değeri: dfH(CH4)=-74.6, CO2=-393.5, H2O(g)=-241.83 kJ/mol => LHV = 802.6 kJ/mol
LHV_CH4 = 393.5 + 2 * 241.826 - 74.6       # kJ/mol  (= 802.6)
MW_CH4, MW_AIR = 16.043, 0.21 * 31.998 + 0.79 * 28.014

# --- Sıvı faz aktivite katsayıları (Wilson). Sıra: [IPA, Aseton, Su] -> indeks 0,1,3
# ChemSep Wilson (Λij = exp(a + b/T), T[K]):  IPA-su  (a=-1.4484, b=-220.40 ; a=+1.4484, b=-623.49)
#   aseton-su (a=-1.4078, b=-221.24 ; a=+1.4078, b=-707.27): IPA-su ile aynı yön kuralı; ters yön 0,88 mol kesrinde sahte azeotrop verir (fiziksel değil) -> bu yön.
#   Bu parametreler seyreltik uçta aseton γ∞'yi (16) Henry verisinden (6.7) yüksek verir -> absorber K'sı Henry'den alınır.
#   aseton-IPA: parametre bulunamadı -> ideal (Λ=1)  [SINIRLAMA]
_WL = {(0, 3): (-1.448381062348813, -220.3995377403026), (3, 0): (1.448381062348813, -623.4872910585569),
       (1, 3): (-1.4077724207419025, -221.2354357073974), (3, 1): (1.4077724207419027, -707.2700221371804)}
def _Lam(T, idx):
    n = len(idx); L = np.ones((n, n))
    for a, i in enumerate(idx):
        for b, j in enumerate(idx):
            if a != b and (i, j) in _WL:
                A, B = _WL[(i, j)]; L[a, b] = np.exp(A + B / T)
    return L
def gamma(x, Tc, idx=(0, 1, 3)):
    """x: sıvı mol kesirleri (idx sırasında, toplam=1). Dönüş: γ"""
    x = np.asarray(x, float); L = _Lam(Tc + 273.15, idx); s = L @ x
    return np.exp(-np.log(s) + 1 - np.array([np.sum(x * L[:, i] / s) for i in range(len(x))]))
def Kfun(x, Tc, P, idx=(0, 1, 3)):
    g = gamma(x, Tc, idx); return np.array([g[k] * Psat(i, Tc) / P for k, i in enumerate(idx)])

def bubble_T(x_full, P):
    """Sıvı kompozisyonu (4'lü, H2 yok sayılır) için kabarcık noktası, °C"""
    idx = [i for i in (0, 1, 3) if x_full[i] > 0]; x = np.array([x_full[i] for i in idx]); x = x / x.sum()
    return brentq(lambda T: float(np.sum(x * gamma(x, T, tuple(idx)) * np.array([Psat(i, T) for i in idx]))) - P, 1, 250)
def dew_T(y_full, P):
    """Buhar kompozisyonu (yoğuşabilir bileşenler + H2 seyreltici) için çiğlenme noktası, °C (γ iterasyonlu)"""
    idx = (0, 1, 3); yk = np.array([y_full[i] for i in idx]); yk = yk / np.sum(y_full)       # H2 dahil toplam üzerinden
    def f(T):
        x = yk / 1.0
        for _ in range(100):
            ps = np.array([Psat(i, T) for i in idx]); xn = yk * P / (gamma(x / x.sum(), T, idx) * ps)
            if np.abs(xn - x).max() < 1e-13: break
            x = 0.5 * x + 0.5 * xn
        return x.sum() - 1.0
    return brentq(f, 1, 300)

def vap_eq(x_full, Tc, P):
    """Sıvı (4'lü) ile dengedeki buhar kompozisyonu (mol kesri, 4'lü; H2=0)"""
    idx = (0, 1, 3); x = np.array([x_full[i] for i in idx]); x = x / x.sum()
    y = x * gamma(x, Tc, idx) * np.array([Psat(i, Tc) for i in idx]) / P
    out = np.zeros(4); out[0], out[1], out[3] = y; return out / out.sum()

def flash(n, T, P):
    """V-101: Wilson γ'lı flaş. IPA, aseton, su yoğuşabilir; H2 yoğuşmaz ve çözünmez (ihmal)."""
    idx = (0, 1, 3); H = n[2]; c = np.array([n[i] for i in idx]); Nc = c.sum()
    xs = {'x': c / c.sum()}
    def liq(L):
        x = xs['x']
        for _ in range(300):
            K = Kfun(x, T, P, idx); l = c / (1 + K * (Nc - L + H) / L); xn = l / l.sum()
            if np.abs(xn - x).max() < 1e-12: break
            x = 0.5 * x + 0.5 * xn
        xs['x'] = x; return l
    L = brentq(lambda L: liq(L).sum() - L, 1e-7 * Nc, Nc * (1 - 1e-9), xtol=1e-12)
    l = liq(L); liqv = np.array([l[0], l[1], 0.0, l[2]])
    return n - liqv, liqv

def Hs(st): return float(st['V'] @ Hv_vec(st['T']) + st['L'] @ Hl_vec(st['T']))      # kJ/h
def T_liq_from_H(comp, Ht): return brentq(lambda T: comp @ Hl_vec(T) - Ht, -20, 250)
def T_vap_from_H(comp, Ht): return brentq(lambda T: comp @ Hv_vec(T) - Ht, 20, 600)
def mk(T, V, L): return dict(T=float(T), V=np.array(V, float), L=np.array(L, float))
Z = np.zeros(4)
mol = lambda st: st['V'] + st['L']
kg = lambda st: float(mol(st) @ MW)

# Henry sabiti (Sander derlemesi): aseton, su içinde Hcp(298.15 K)=0.27 mol/(m3 Pa), d ln H/d(1/T)=5500 K [DOGRULANDI]
def K_ace_henry(Tc, P_bar):
    TK = Tc + 273.15; Hcp = 0.27 * np.exp(5500.0 * (1 / TK - 1 / 298.15))     # mol/m3/Pa
    Hx = (997.0 / 18.015 * 1000.0) / Hcp                                       # Pa  (y = Hx x / P)
    return Hx / (P_bar * 1e5), Hx / Psat(1, Tc) / 1e5                          # K, γ∞

__all__ = [_n for _n in dir() if not _n.startswith('__')]
