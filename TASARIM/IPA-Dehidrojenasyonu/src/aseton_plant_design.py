# -*- coding: utf-8 -*-
"""
TASARIM I (T1-01) - ASETON TESİSİ ÖN TASARIMI | GRUP 8 | v10 (tek dosya; Colab'de tek hücreye yapıştırılır veya `python aseton_plant_design.py`)
IPA dehidrojenasyonu: (CH3)2CHOH -> (CH3)2CO + H2 (buhar fazı, Cu/Zn katalizör, 350 °C, ~2.2 bar). 85 000 t/yıl, 8000 h/yıl.

ÇIKTILAR: Aseton_Grup8_TEK_PDF.pdf (rapor + A3 PFD, tek dosya), Hesap_foyu_aseton_grup8.pdf (adım adım hesaplar), PFD_aseton_grup8.pdf/.png (A3, 1 sayfa),
          Rapor_aseton_grup8.pdf (<=5 sayfa), CSV tabloları. Colab'de otomatik indirilir.

DÜRÜSTLÜK NOTU: Ticari simülatör (HYSYS/ChemCAD) KULLANILMAMIŞTIR; kısa yol hesabı Python ile yapılmıştır.
Simülatörle karşılaştırma yapılmamıştır; dönüşüm (%90) ve seçicilik (%100) tasarım kabulüdür (raporda Bölüm 5.7).
"""
import subprocess, sys
try:
    import reportlab
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'reportlab'])
import warnings
warnings.filterwarnings('ignore')
# -*- coding: utf-8 -*-
"""
TASARIM I (T1-01) - ASETON TESİSİ ÖN TASARIMI | GRUP 8 | v3  --  HESAP ÇEKİRDEĞİ
(CH3)2CHOH -> (CH3)2CO + H2   (buhar fazı, katalizörlü, 350 °C, ~2 bar)
Etiketler:  [DOGRULANDI] kaynak sayfasından görüldü | [DOGRULA] görülmedi | [VARSAYIM] tasarım varsayımı
"""
import os, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
from scipy.optimize import brentq

MAP = {}                      # eski (iç) akım no -> PFD'deki soldan-sağa akım no
def nn(k): return MAP.get(k, k)
def f4(x):
    """4 anlamlı rakama yuvarlanmış metin (SI; örn. 1234.5678 -> 1235, 0.0123456 -> 0.01235)"""
    import math
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))): return '-'
    if x == 0: return '0'
    if abs(x) < 1e-3: return f"{x:.3g}"
    d = 3 - int(math.floor(math.log10(abs(x))))
    v = round(x, d)
    return f"{v:.0f}" if d <= 0 else f"{v:.{d}f}"

# =====================================================================
# 1) VERİ
# =====================================================================
NAMES = ['IPA', 'Aseton', 'H2', 'Su']
MW = np.array([60.095, 58.079, 2.016, 18.015])          # kg/kmol
T_REF = 298.15
HFV = np.array([-272.6e3, -217.1e3, 0.0, -241.826e3])    # J/mol gaz fazı oluşum entalpisi, 25 °C [DOGRULANDI]
# Buharlaşma entalpisi 25 °C (J/mol): IPA 45.34 (NIST/Chemeo), aseton 31.27 (NIST), su 43.99 (=40.65 kJ/mol@100 °C + ∫(Cpl-Cpg)dT, tutarlılık testi verify_data'da)
DHVAP = np.array([45.34e3, 31.27e3, 0.0, 43.99e3])
HFL = HFV - DHVAP
CPL = np.array([155.2, 125.45, 28.84, 75.3])             # sıvı Cp J/mol/K (sabit; su 75.3 = 4.18 kJ/kg/K x 18.015)
RHO = np.array([786., 790., 1., 997.])                   # kg/m3  (IPA 786 Wikipedia 20 °C [DOGRULANDI]; su 997; aseton ~790)

SHO_H2 = (33.066178, -11.363417, 11.432816, -2.772874, -0.158558)           # NIST Shomate 298-1000 K [DOGRULANDI]
SHO_H2O = (30.09200, 6.832514, 6.793435, -2.534480, 0.082139)                # NIST Shomate 500-1700 K; 298 K'de 33.59 (NIST 33.58) [DOGRULANDI/uzatma testli]
ACE_TAB = np.array([[298.15, 75.02], [300., 75.32], [400., 92.06], [500., 108.08], [600., 122.20], [700., 134.43]])
IPA_TAB = np.array([[358.72, 103.06], [373.15, 106.29], [398.15, 111.65], [423.15, 117.02], [448.15, 122.10],
                    [473.15, 127.01], [499.75, 130.30], [539.05, 137.50], [567.05, 142.60], [597.25, 148.10]])
P_ACE = np.poly1d(np.polyfit(ACE_TAB[:, 0], ACE_TAB[:, 1], 3))
P_IPA = np.poly1d(np.polyfit(IPA_TAB[:, 0], IPA_TAB[:, 1], 2))

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

# =====================================================================
# 2) PARAMETRELER
# =====================================================================
PAR = dict(
    GRUP=8, CAP_TON_YIL=85000.0, SAAT=8000.0,
    W_SU_URUN=0.004,       # [VARSAYIM] ürün suyu kütle kesri 0,4 % (şart: en çok 0,5 %; 0,1 puan emniyet payı)
    W_IPA_BESLEME=0.88,    # taze besleme azeotrop yakını IPA, kütle %88 (Turton/Rice)
    X=0.90,                # [VARSAYIM] tek geçiş dönüşümü (Turton: %85-92)
    T_R=350.0, T_6=300.0,  # reaktör sıcaklığı; E-101 soğuk çıkış (kızgın buhar)
    T_FL=40.0, T_ABS=35.0, T_SU=25.0, T_PA_HOT=40.0, T_PA_COLD=30.0,
    A_ABS=1.4,             # absorpsiyon faktörü (literatür aralığı 1,2-2 / 1,4-2, aralığın alt ucu)
    REC_ACE_ABS=0.995,     # [VARSAYIM] aseton geri kazanımı (absorber)
    REC_ACE_C1=0.999, REC_IPA_C2=0.995,
    AZ_WT=0.878,           # IPA-su azeotropu kütle kesri (patentler) -> geri dönüş bileşimi
    RR_FACTOR=1.3,         # R = 1.3 x Rmin
    ETA_POMPA=0.70, ETA_FIRIN=0.85, EXCESS_AIR=0.15,
    T_SALT_HOT=450.0, T_SALT_COLD=390.0, CP_SALT=1.56,   # [DOGRULANMADI] Hitec benzeri nitrat/nitrit tuzu Cp kJ/kg/K
    T_FLUE=250.0, T_FUEL=25.0, T_AIR=25.0,
    P={1: 1.0, 2: 1.1, 3: 1.0, 4: 3.2, 5: 2.8, 6: 2.6, 7: 2.2, 8: 2.0, 9: 1.8, 10: 1.8, 11: 1.8, 12: 3.0, 13: 1.7,
       14: 1.8, 15: 1.3, 16: 1.1, 17: 1.0, 18: 1.3, 19: 1.3, 42: 1.8, 43: 2.3, 44: 2.1,
       45: 1.1, 46: 1.1, 47: 1.1, 48: 1.3, 49: 1.3, 50: 1.1, 51: 1.1, 52: 1.1, 53: 1.3, 54: 1.3},
    P_COL1=(1.1, 1.3), P_COL2=(1.1, 1.3),
)

# =====================================================================
# 3) KISA YOL KOLON FONKSİYONLARI
# =====================================================================
def _y_eq_binary(x1, P, pair):
    """İkili denge: pair=(i,j) hafif=i. Dönüş y_i (Wilson)"""
    i, j = pair; idx = (i, j); x = np.array([x1, 1 - x1])
    T = brentq(lambda T: float(np.sum(x * gamma(x, T, idx) * np.array([Psat(k, T) for k in idx]))) - P, 1, 250)
    g = gamma(x, T, idx); return x1 * g[0] * Psat(i, T) / P, T

def rmin_binary(xD, z, q, P, pair):
    """McCabe-Thiele minimum reflü: R_min = max_x (xD - y*)/(y* - x),  x in [x_q, xD)"""
    if abs(q - 1.0) < 1e-9: xq = z
    else:
        fq = lambda x: _y_eq_binary(x, P, pair)[0] - (q * x - z) / (q - 1.0)
        xq = brentq(fq, 1e-5, min(z, xD - 1e-4)) if fq(1e-5) * fq(min(z, xD - 1e-4)) < 0 else z
    xs = np.linspace(xq, xD - 1e-3, 120)
    r = []
    for x in xs:
        y = _y_eq_binary(x, P, pair)[0]
        r.append((xD - y) / (y - x) if y > x + 1e-9 else np.inf)
    return max(r), xq

def kremser_N(A, R): return np.log((A - R) / (1 - R)) / np.log(A) - 1.0

# =====================================================================
# 4) AKIŞ ŞEMASI
# =====================================================================
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

# =====================================================================
# 5) BİRİM BAZLI KÜTLE / ENERJİ DENKLİĞİ
# =====================================================================
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

# =====================================================================
# 6) DOĞRULAMA TESTLERİ VE TASARIM KONTROLLERİ
# =====================================================================
def verify_data():
    rows = []
    for TK, Pk in [(297.8, 5.78), (313.15, 13.94), (333.15, 38.59), (355.38, 101.28), (373.5, 200.1)]:
        m = Psat(0, TK - 273.15) * 100
        rows.append(('IPA Psat %.1f K' % TK, f'{m:.2f} kPa', f'{Pk:.2f} kPa', 100 * (m / Pk - 1), 2.5))
    for Tc, Pk in [(30.0, 4.242), (100.0, 101.325)]:
        m = Psat(3, Tc) * 100; rows.append((f'Su Psat {Tc:.0f} °C', f'{m:.3f} kPa', f'{Pk:.3f} kPa', 100 * (m / Pk - 1), 2.0))
    m = Psat(1, 56.1) * 100; rows.append(('Aseton Psat 56.1 °C (nbp 329.2 K)', f'{m:.1f} kPa', '101.3 kPa', 100 * (m / 101.325 - 1), 2.0))
    for nm, P_, tab in [('Aseton Cp,gaz polinom', P_ACE, ACE_TAB), ('IPA Cp,gaz polinom', P_IPA, IPA_TAB)]:
        err = np.abs(P_(tab[:, 0]) - tab[:, 1]).max(); rows.append((nm + ' maks. sapma', f'{err:.2f} J/mol/K', 'NIST noktaları', err, 1.5))
    cp298 = _sho_cp(SHO_H2O, 298.15); rows.append(('Su buharı Cp 298 K (Shomate uzatma)', f'{cp298:.2f}', '33.58 (NIST)', 100 * (cp298 / 33.58 - 1), 1.0))
    # Hvap tutarlılığı (su 100 °C: 40.65 kJ/mol, Wikipedia/NIST)
    lam_w = (Hv_vec(100.0)[3] - Hl_vec(100.0)[3]) / 1000
    rows.append(('Su Hvap 100 °C (model: 25 °C değeri + Cp)', f'{lam_w:.2f} kJ/mol', '40.65', 100 * (lam_w / 40.65 - 1), 1.5))
    d = (Hv_vec(25.0)[1] + Hv_vec(25.0)[2] - Hv_vec(25.0)[0]) / 1000
    rows.append(('ΔH dehidrojenasyon 25 °C', f'{d:+.2f} kJ/mol', '+55.23..+55.40 (NIST ters rxn.)', 100 * (d / 55.3 - 1), 1.5))
    # Wilson: IPA-su azeotropu
    f = lambda xi: (lambda T: (np.array([xi, 1 - xi]), T))(brentq(lambda T: xi * gamma([xi, 0, 1 - xi], T)[0] * Psat(0, T) + (1 - xi) * gamma([xi, 0, 1 - xi], T)[2] * Psat(3, T) - 1.01325, 50, 110))
    def az(xi):
        _, T = f(xi); g = gamma([xi, 0, 1 - xi], T); return g[0] * Psat(0, T) - g[2] * Psat(3, T)
    xa = brentq(az, 0.4, 0.9); Ta = f(xa)[1]; wa = xa * MW[0] / (xa * MW[0] + (1 - xa) * MW[3])
    rows.append(('IPA-su azeotrop T (Wilson, 1.013 bar)', f'{Ta:.2f} °C', '80.37-80.4 °C', Ta - 80.4, 0.5))
    rows.append(('IPA-su azeotrop bileşimi (Wilson)', f'%{100 * wa:.1f} kütle', '%87.8 kütle', 100 * (wa - 0.878), 2.0))
    # aseton γ∞ Henry vs Wilson
    _, ginf25 = K_ace_henry(25.0, 1.0); gw = gamma([1e-9, 1 - 1e-9], 25.0, (1, 3))[0]
    rows.append(('Aseton γ∞(su,25 °C): Wilson / Henry', f'{gw:.1f} / {ginf25:.1f}', 'Henry (Sander) esas alındı', 100 * (gw / ginf25 - 1), 999))
    return pd.DataFrame(rows, columns=['Test', 'Model/kod', 'Kaynak değeri', 'Sapma_%', 'Sinir_%']).assign(
        Sonuc=lambda d: np.where(d['Sinir_%'] > 100, 'BİLGİ (Henry esas)', np.where(d['Sapma_%'].abs() <= d['Sinir_%'], 'GEÇTİ', 'SINIR AŞILDI')))

def exchanger_table(S, D, U, E, par):
    """Her eşanjör için terminal sıcaklıklar ve minimum yaklaşım (ΔT). Boyutlandırma değil, termodinamik uygulanabilirlik."""
    r = []
    add = lambda code, hi, ho, ci, co, note='': r.append(dict(Ekipman=code, Sicak_giris=hi, Sicak_cikis=ho, Soguk_giris=ci, Soguk_cikis=co,
                                                              dT_sicak_uc=hi - co, dT_soguk_uc=ho - ci, Not=note))
    add('E-102', T_LPS, T_LPS, S[4]['T'], S[5]['T'], 'LPS yoğuşur / karışım ısınır+buharlaşır')
    add('E-101', S[7]['T'], S[8]['T'], S[5]['T'], S[6]['T'], 'Sıcak: reaktör çıkışı (7->8), soğuk: 5->6')
    add('R-101', par['T_SALT_HOT'], par['T_SALT_COLD'], S[6]['T'], S[7]['T'], 'Tuz / proses (reaksiyon dahil)')
    add('E-103', S[8]['T'], S[9]['T'], 25, 35, 'cw 25->35 °C')
    add('E-109', S[42]['T'], S[44]['T'], 25, 35, 'cw 25->35 °C, pump-around')
    add('E-104', S[45]['T'], S[46]['T'], 25, 35, 'cw 25->35 °C')
    add('E-105', T_LPS, T_LPS, S[48]['T'], S[49]['T'], 'LPS / rebolyer')
    add('E-106', S[50]['T'], S[51]['T'], 25, 35, 'cw 25->35 °C')
    add('E-107', T_LPS, T_LPS, S[53]['T'], S[54]['T'], 'LPS / rebolyer')
    add('E-108', S[16]['T'], S[17]['T'], 7, 12, 'chw 7->12 °C (25 °C ürün için cw yetmez)')
    df = pd.DataFrame(r); df['dT_min'] = df[['dT_sicak_uc', 'dT_soguk_uc']].min(axis=1); return df

def design_checks(S, D, U, E, par, C):
    ex = exchanger_table(S, D, U, E, par)
    dewT8 = dew_T(S[8]['V'], par['P'][8])
    chk = [
     ('Ürün suyu ≤ 0,5 % (kütle)', C['w_water_prod'] * 100, '≤ 0.5', C['w_water_prod'] <= 0.005),
     ('Ürün sıvı, 25 °C', S[17]['T'], '= 25', abs(S[17]['T'] - 25) < 1e-9 and S[17]['V'].sum() == 0),
     ('Ürün debisi = kapasite (kg/h)', kg(S[17]), f"{par['CAP_TON_YIL'] * 1000 / par['SAAT']:.0f}", abs(kg(S[17]) - par['CAP_TON_YIL'] * 1000 / par['SAAT']) < 1e-6),
     ('Kütle kapanışı (kg/h)', C['mass_in'] - C['mass_out'], '|.|<1e-6', abs(C['mass_in'] - C['mass_out']) < 1e-6),
     ('Element (C,H,O) kapanışı', float(np.abs(C['el_in'] - C['el_out']).max()), '<1e-6 kmol/h', np.allclose(C['el_in'], C['el_out'], rtol=1e-9)),
     ('Enerji kapanışı (kW)', C['E_err'], '|.|<1e-6', abs(C['E_err']) < 1e-6),
     ('Dönüşüm < denge dönüşümü', par['X'], f"X_eq = {C['X_eq']:.3f}", par['X'] < C['X_eq']),
     ('Akım 5 doygun buhar; LPS - T5 ≥ 20 K', T_LPS - E['T5'], '≥ 20', T_LPS - E['T5'] >= 20),
     ('Akım 8 çiğlenme üstünde (T8 - T_çiğ ≥ 10 K)', S[8]['T'] - dewT8, '≥ 10', S[8]['T'] - dewT8 >= 10),
     ('R > R_min (C-101)', E['R1'] - E['Rmin1'], '> 0', E['R1'] > E['Rmin1']),
     ('R > R_min (C-102)', E['R2'] - E['Rmin2'], '> 0', E['R2'] > E['Rmin2']),
     ('Eşanjör yaklaşımları ΔT_min ≥ 5 K', float(ex['dT_min'].min()), '≥ 5', ex['dT_min'].min() >= 5 - 1e-9),
     ('Tuz sıcaklığı < tuz üst sınırı (≈540 °C)', par['T_SALT_HOT'], '< 540', par['T_SALT_HOT'] < 540),
     ('Reaktör sıcaklığı patent aralığında (300-550 °C)', par['T_R'], '300-550', 300 <= par['T_R'] <= 550),
     ('Kolon geri kazanımları (aseton C-101 / IPA C-102)', par['REC_ACE_C1'], f"{par['REC_IPA_C2']}", True),
    ]
    return pd.DataFrame(chk, columns=['Kontrol', 'Deger', 'Sinir', 'Sonuc']).assign(Sonuc=lambda d: np.where(d['Sonuc'], 'GEÇTİ', 'HATA')), ex

def sensitivity(par):
    out = {}
    rows = []
    for a in (1.2, 1.4, 1.6, 2.0, 2.5):
        try:
            S, D, U, E = flowsheet(dict(par, A_ABS=a))
            rows.append(dict(A=a, Yikama_suyu_kmol_h=S[12]['L'].sum(), Su_urun_oran=E['Ls'] * MW[3] / E['prod_kg_h'], N_teorik=E['N_abs'],
                             LPS_toplam_kW=D['E102'] + D['E105'] + D['E107'], E105_kW=D['E105']))
        except Exception as e:
            rows.append(dict(A=a, Yikama_suyu_kmol_h=np.nan, Su_urun_oran=np.nan, N_teorik=np.nan, LPS_toplam_kW=np.nan, E105_kW=np.nan))
    out['A'] = pd.DataFrame(rows)
    rows = []
    for x in (0.80, 0.85, 0.90, 0.92):
        S, D, U, E = flowsheet(dict(par, X=x))
        rows.append(dict(X=x, Geri_donus_kmol_h=S[2]['L'].sum(), Reaktor_girisi_kmol_h=S[6]['V'].sum(), R101_kW=D['R101'], LPS_toplam_kW=D['E102'] + D['E105'] + D['E107']))
    out['X'] = pd.DataFrame(rows)
    rows = []
    for f in (1.2, 1.3, 1.5):
        S, D, U, E = flowsheet(dict(par, RR_FACTOR=f))
        rows.append(dict(R_per_Rmin=f, R1=E['R1'], R2=E['R2'], E105_kW=D['E105'], E107_kW=D['E107']))
    out['R'] = pd.DataFrame(rows)
    return out


# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

UT = '#0b5394'      # yardımcı akışkan rengi
SALT = '#b45f06'    # erimiş tuz
DIA = []            # çizilen akım numaraları (iç no)
POS = {}            # iç no -> (x, y)
YMAX = 81

def _line(ax, pts, arrow=True, lw=1.1, color='k', ls='-', z=1):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, ls, color=color, lw=lw, zorder=z, solid_capstyle='butt')
    if arrow:
        ax.annotate('', xy=pts[-1], xytext=pts[-2], zorder=z + 1,
                    arrowprops=dict(arrowstyle='-|>', lw=lw, color=color, shrinkA=0, shrinkB=0, mutation_scale=8))
def dia(ax, x, y, n, color='k'):
    DIA.append(n); POS[n] = (x, y)
    ax.add_patch(Polygon([(x - 1.35, y), (x, y + 1.35), (x + 1.35, y), (x, y - 1.35)], closed=True, fc='white', ec=color, lw=.9, zorder=8))
    ax.text(x, y, str(nn(n)), ha='center', va='center', fontsize=5.6, zorder=9, fontweight='bold', color=color)
def hx(ax, x, y, r=2.8):
    ax.add_patch(Circle((x, y), r, fc='white', ec='k', lw=1.2, zorder=4))
    z = np.array([(-.7, 0), (-.4, .4), (-.13, -.4), (.13, .4), (.4, -.4), (.7, 0)]) * r
    ax.plot(x + z[:, 0], y + z[:, 1], 'k-', lw=1, zorder=5)
def pump(ax, x, y, r=2.2, color='k'):
    ax.add_patch(Circle((x, y), r, fc='white', ec=color, lw=1.2, zorder=4))
    ax.add_patch(Polygon([(x - .55 * r, y + .65 * r), (x - .55 * r, y - .65 * r), (x + .8 * r, y)], closed=True, fc='white', ec=color, lw=1, zorder=5))
def vessel(ax, x, y, w, h, trays=0, tubes=False, r=2.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc='white', ec='k', lw=1.3, zorder=4))
    for k in range(trays):
        yy = y - h / 2 + 3.5 + k * (h - 7) / max(trays - 1, 1)
        ax.plot([x - w / 2 + .5, x + w / 2 - .5], [yy, yy], 'k-', lw=.5, zorder=5)
    if tubes:
        for xx in np.linspace(x - w / 2 + 1.3, x + w / 2 - 1.3, 5): ax.plot([xx, xx], [y - h / 2 + 2.5, y + h / 2 - 2.5], 'k-', lw=.6, zorder=5)
def txt(ax, x, y, s, fs=6.0, ha='center', va='center', bold=False, color='k', **kw):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, fontweight='bold' if bold else 'normal', color=color, zorder=10, **kw)
def flag(ax, S, par, k, x, y, w=7.2):
    """T/P bayrağı: kritik akım için sıcaklık ve basınç kutusu (akım diyamantına yakın)"""
    t = f"{f4(S[k]['T'])} °C\n{f4(par['P'][k] * 100)} kPa"
    ax.add_patch(FancyBboxPatch((x - w / 2, y - 1.45), w, 2.9, boxstyle="round,pad=0,rounding_size=0.5", fc='#fff9d6', ec='#7f6000', lw=.6, zorder=7))
    ax.text(x, y, t, fontsize=4.6, ha='center', va='center', zorder=9, linespacing=1.05)

# üst kenar ekipman listesi (soldan sağa)
STRIP = [('V-100', 'Besleme tankı'), ('P-101A/B', 'Besleme pompası'), ('E-102', 'Buharlaştırıcı'), ('E-101', 'Besleme/çıkış ısı değiştirici'),
         ('R-101', 'Dehidrojenasyon reaktörü'), ('E-103', 'Reaktör çıkış soğutucusu'), ('V-101', 'Flaş tankı'), ('T-101', 'Gaz yıkama kolonu'),
         ('P-102', 'Tuz pompası'), ('F-101', 'Tuz ısıtıcı fırın'), ('P-103', 'Pump-around pompası'), ('E-109', 'Pump-around soğutucusu'),
         ('C-101', 'Aseton kolonu'), ('E-104', 'C-101 yoğuşturucu'), ('E-105', 'C-101 rebolyer'), ('E-108', 'Ürün soğutucu'),
         ('C-102', 'IPA kolonu'), ('E-106', 'C-102 yoğuşturucu'), ('E-107', 'C-102 rebolyer')]

def draw_strip(ax):
    n = len(STRIP); per = 10
    w = 148.4 / per; h = 3.3
    for i, (code, name) in enumerate(STRIP):
        r, c = divmod(i, per)
        x0 = 0.8 + c * w; y0 = 80.6 - (r + 1) * h - r * 0.4
        ax.add_patch(Rectangle((x0, y0), w - 0.3, h, fc='#eef3f8', ec='k', lw=.6, zorder=3))
        ax.text(x0 + (w - 0.3) / 2, y0 + h / 2, f"{code}  {name}", ha='center', va='center', fontsize=5.0, fontweight='bold', zorder=5)
    

def draw_drawing(ax, S, D, par):
    DIA.clear(); POS.clear()
    ax.set_xlim(0, 150); ax.set_ylim(0, YMAX); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(Rectangle((.3, .3), 149.4, YMAX - .6, fill=False, ec='k', lw=1.5))
    draw_strip(ax)
    y0 = 50
    cw = lambda x, y, n: (dia(ax, x, y, n, UT), txt(ax, x, y + 2.1, 'cw', fs=5.8, color=UT))
    Q = lambda key: f"Q = {f4(abs(D[key]))} kW"
    # ---------- ANA HAT (besleme -> reaktör)
    _line(ax, [(1.5, y0), (6.5, y0)]); vessel(ax, 11, y0, 9, 6, r=1.6); dia(ax, 4, y0, 1)
    _line(ax, [(15.5, y0), (20.8, y0)]); dia(ax, 18.1, y0, 3)
    pump(ax, 23, y0)
    _line(ax, [(25.2, y0), (32, y0)]); dia(ax, 28.6, y0, 4)
    hx(ax, 35, y0, 3.0)                                                                       # E-102
    _line(ax, [(38, y0), (45.8, y0)]); dia(ax, 41.9, y0, 5)
    hx(ax, 49, y0, 3.2)                                                                       # E-101
    _line(ax, [(52.2, y0), (59.5, y0)]); dia(ax, 55.8, y0, 6)
    vessel(ax, 64, y0, 9, 18, tubes=True)                                                     # R-101
    _line(ax, [(64, 59), (64, 63), (49, 63), (49, 53.2)]); dia(ax, 57, 63, 7)
    _line(ax, [(139, 60), (139, 69), (11, 69), (11, 53)]); dia(ax, 70, 69, 2)
    _line(ax, [(35, 59), (35, 53)], color=UT); dia(ax, 35, 56.2, 20, UT); txt(ax, 35, 60.2, 'LPS', fs=5.8, color=UT)
    _line(ax, [(35, 47), (35, 41)], color=UT); dia(ax, 35, 44, 21, UT); txt(ax, 35, 39.8, 'LPS yoğuşuğu', fs=5.4, color=UT)
    # ---------- SICAK TARAF
    _line(ax, [(49, 46.8), (49, 38.2)]); dia(ax, 49, 42.5, 8)
    hx(ax, 49, 35, 3.2)                                                                       # E-103
    _line(ax, [(40, 35), (45.8, 35)], color=UT); cw(42.6, 35, 26)
    _line(ax, [(52.2, 35), (57.5, 35)], color=UT); cw(54.9, 35, 27)
    _line(ax, [(49, 31.8), (49, 11), (52.5, 11)]); dia(ax, 49, 22, 9)
    vessel(ax, 56, 11, 7, 11)                                                                 # V-101
    _line(ax, [(56, 16.5), (56, 18), (68, 18)]); dia(ax, 62, 18, 10)
    vessel(ax, 72, 25, 8, 28, trays=6)                                                        # T-101 (y 11-39)
    _line(ax, [(61, 36), (68, 36)]); dia(ax, 64.5, 36, 12); txt(ax, 57.5, 38.1, 'Proses suyu (25 °C)', fs=5.8, ha='left')
    _line(ax, [(72, 39), (72, 45.5)]); dia(ax, 72, 42.0, 13); txt(ax, 73.2, 44.6, 'H2-zengin vent', fs=5.8, ha='left')
    _line(ax, [(56, 5.5), (56, 3.2), (72, 3.2)]); dia(ax, 63, 3.2, 11)
    _line(ax, [(72, 11), (72, 3.2)], arrow=False); dia(ax, 72, 7.0, 14)
    _line(ax, [(72, 3.2), (92, 3.2), (92, 18), (100, 18)]); dia(ax, 84, 3.2, 15)
    _line(ax, [(76, 22), (80.2, 22)]); dia(ax, 78.1, 22, 42)
    pump(ax, 82.5, 22, 2.2)
    _line(ax, [(84.7, 22), (88, 22), (88, 26.2)]); dia(ax, 88, 23.9, 43)
    hx(ax, 88, 29, 2.8)                                                                       # E-109
    _line(ax, [(88, 31.8), (88, 35), (76, 35)]); dia(ax, 82, 35, 44)
    _line(ax, [(96, 29), (90.8, 29)], color=UT); cw(93.4, 29, 28)
    _line(ax, [(85.2, 29), (80, 29)], color=UT); cw(82.6, 29, 29)
    # ---------- C-101
    vessel(ax, 104, 29, 8, 34, trays=9)
    _line(ax, [(104, 46), (104, 50.4)]); dia(ax, 104, 48.2, 45)
    hx(ax, 104, 53, 2.6)                                                                      # E-104
    _line(ax, [(96, 53), (101.4, 53)], color=UT); cw(98.6, 53, 30)
    _line(ax, [(106.6, 53), (112, 53)], color=UT); dia(ax, 109.3, 53, 31, UT); txt(ax, 109.3, 51.0, 'cw', fs=5.8, color=UT)
    _line(ax, [(104, 55.6), (104, 62), (118.4, 62)]); dia(ax, 104, 58.2, 46)
    _line(ax, [(113.5, 62), (113.5, 43), (108.2, 43)]); dia(ax, 113.5, 52, 47)
    ax.plot([113.5], [62], 'ko', ms=2.5, zorder=6); dia(ax, 116.0, 62, 16)
    hx(ax, 121, 62, 2.6)                                                                      # E-108
    _line(ax, [(123.6, 62), (128, 62)]); dia(ax, 125.9, 62, 17)
    _line(ax, [(121, 56.2), (121, 59.4)], color=UT); dia(ax, 121, 57.6, 34, UT); txt(ax, 122.9, 56.4, 'chw', fs=5.8, color=UT, ha='left')
    _line(ax, [(121, 64.6), (121, 65.7), (126.5, 65.7)], color=UT); dia(ax, 123.6, 65.7, 35, UT)
    _line(ax, [(104, 12), (104, 8)], arrow=False)
    _line(ax, [(104, 8), (111.4, 8)]); dia(ax, 107.7, 8, 48)
    hx(ax, 114, 8, 2.6)                                                                       # E-105
    _line(ax, [(116.6, 8), (120, 8), (120, 20), (108.2, 20)]); dia(ax, 120, 14, 49)
    _line(ax, [(114, 15.5), (114, 10.6)], color=UT); dia(ax, 114, 13.0, 22, UT); txt(ax, 115.6, 15.8, 'LPS', fs=5.8, color=UT, ha='left')
    _line(ax, [(114, 5.4), (114, 4.0)], color=UT); dia(ax, 111.0, 4.6, 23, UT); txt(ax, 116.0, 4.6, 'LPS yoğ.', fs=5.4, color=UT, ha='left')
    _line(ax, [(112.2, 6.1), (107.4, 6.1), (107.4, 2.2), (122.5, 2.2), (122.5, 18), (126, 18)]); dia(ax, 107.4, 4.2, 18)
    # ---------- C-102
    vessel(ax, 130, 29, 8, 34, trays=9)
    _line(ax, [(130, 46), (130, 50.4)]); dia(ax, 130, 48.2, 50)
    hx(ax, 130, 53, 2.6)                                                                      # E-106
    _line(ax, [(121.5, 53), (127.4, 53)], color=UT); cw(124.4, 53, 32)
    _line(ax, [(132.6, 53), (138, 53)], color=UT); dia(ax, 135.3, 53, 33, UT); txt(ax, 135.3, 51.0, 'cw', fs=5.8, color=UT)
    _line(ax, [(130, 55.6), (130, 60), (139, 60)], arrow=False); dia(ax, 130, 57.8, 51)
    _line(ax, [(139, 60), (142, 60), (142, 43), (134.2, 43)]); dia(ax, 142, 51, 52)
    ax.plot([139], [60], 'ko', ms=2.5, zorder=6)
    _line(ax, [(130, 12), (130, 8)], arrow=False)
    _line(ax, [(130, 8), (137.4, 8)]); dia(ax, 133.7, 8, 53)
    hx(ax, 140, 8, 2.6)                                                                       # E-107
    _line(ax, [(142.6, 8), (146, 8), (146, 20), (134.2, 20)]); dia(ax, 146, 14, 54)
    _line(ax, [(140, 15.5), (140, 10.6)], color=UT); dia(ax, 140, 13.0, 24, UT); txt(ax, 141.6, 15.8, 'LPS', fs=5.8, color=UT, ha='left')
    _line(ax, [(140, 5.4), (140, 4.0)], color=UT); dia(ax, 137.4, 4.6, 25, UT); txt(ax, 142.0, 4.6, 'LPS yoğ.', fs=5.4, color=UT, ha='left')
    _line(ax, [(138.2, 6.1), (133.8, 6.1), (133.8, 2.2), (148, 2.2)]); dia(ax, 133.8, 4.2, 19)
    # ---------- F-101 + tuz çevrimi
    ax.add_patch(Rectangle((78, 52.5), 12, 9, fc='white', ec='k', lw=1.3, zorder=4))
    xs = np.linspace(79.5, 88.5, 9); ax.plot(xs, 56.5 + np.array([-1.5, 1.5] * 5)[:9], 'k-', lw=1, zorder=5)
    _line(ax, [(78, 58), (68.5, 58)], color=SALT, ls='--'); dia(ax, 73.2, 58, 39, SALT)
    _line(ax, [(68.5, 49), (75.8, 49)], color=SALT, ls='--'); dia(ax, 72.2, 49, 40, SALT)
    pump(ax, 78, 49, 2.2, color=SALT)
    _line(ax, [(80.2, 49), (84, 49), (84, 52.5)], color=SALT, ls='--'); dia(ax, 82.0, 49, 41, SALT)
    _line(ax, [(96, 59.5), (90, 59.5)], color=UT); dia(ax, 93.2, 59.5, 36, UT); txt(ax, 93.2, 63.4, 'fuel gas (CH4)\n%.0f kW (yakıt gücü)' % (D['F101'] / par['ETA_FIRIN']), fs=5.4, color=UT)
    _line(ax, [(96, 55), (90, 55)], color=UT); dia(ax, 93.2, 55, 37, UT); txt(ax, 93.2, 57.1, 'hava', fs=5.8, color=UT)
    _line(ax, [(84, 61.5), (84, 66)], color=UT); dia(ax, 84, 63.6, 38, UT); txt(ax, 85.4, 65.4, 'baca gazı', fs=5.8, color=UT, ha='left')
    # ---------- ekipman kodları + ısı yükü (kW)
    L = lambda *a, **k: txt(ax, *a, **k)
    L(11, 46.2, 'V-100', fs=6.2, bold=True, va='top')
    L(23, 46.4, 'P-101A/B\n(1 çalışan + 1 yedek)\nW = ' + f4(D['P101']) + ' kW', fs=5.6, bold=True, va='top')
    L(37.6, 47.4, 'E-102\n' + Q('E102'), fs=5.8, bold=True, ha='left', va='top')
    L(45.6, 54.6, 'E-101\n' + Q('E101'), fs=5.8, bold=True, ha='right', va='bottom')
    L(69.2, 62.5, 'R-101\n' + Q('R101'), fs=5.8, bold=True, ha='left', va='top')
    L(45.4, 31.4, 'E-103\n' + Q('E103'), fs=5.8, bold=True, ha='right', va='top')
    L(59.8, 8.5, 'V-101\n(40 °C)', fs=6.0, bold=True, ha='left', va='center')
    L(67.6, 29.0, 'T-101\n' + Q('T101') + '\n(E-109 ile alınır)', fs=5.6, bold=True, ha='right', va='center')
    L(82.5, 18.7, 'P-103\nW = ' + f4(D['P103']) + ' kW', fs=5.6, bold=True); L(91.2, 25.3, 'E-109\n' + Q('E109'), fs=5.6, bold=True, ha='left')
    L(100.8, 47.0, 'C-101', fs=6.0, bold=True, ha='right', va='bottom')
    L(101.0, 56.0, 'E-104\n' + Q('E104'), fs=5.6, bold=True, ha='right', va='bottom'); L(116.8, 11.5, 'E-105\n' + Q('E105'), fs=5.6, bold=True, ha='left')
    L(124.0, 58.6, 'E-108\n' + Q('E108'), fs=5.6, bold=True, ha='left', va='top')
    L(129.4, 65.0, 'Aseton ürünü →\ndepo (sıvı, 25 °C)', fs=5.8, bold=True, ha='left', va='center')
    L(126.4, 47.0, 'C-102', fs=6.0, bold=True, ha='right', va='bottom')
    L(133.5, 56.0, 'E-106\n' + Q('E106'), fs=5.6, bold=True, ha='left', va='bottom'); L(143.5, 11.5, 'E-107\n' + Q('E107'), fs=5.6, bold=True, ha='left')
    L(84.0, 60.3, 'F-101', fs=5.8, bold=True, va='center')
    L(84.0, 53.5, Q('F101'), fs=5.4, bold=True, va='bottom') if False else L(78.5, 62.4, Q('F101'), fs=5.4, bold=True, ha='left', va='bottom')
    L(78.0, 46.2, 'P-102', fs=5.6, bold=True, va='top', color=SALT)
    L(1.2, 51.8, 'Besleme\nIPA/su', fs=5.8, bold=True, ha='left', va='bottom')
    L(148.5, 3.4, 'Atık su', fs=6.0, bold=True, ha='right', va='bottom')
    L(40, 70.3, 'Geri dönüş (IPA/su, azeotrop bileşim) → V-100', fs=5.8)
    # ---------- T/P bayrakları (kritik noktalar)
    for k, x, y in [(4, 28.6, 54.4), (6, 56.0, 46.2), (7, 53.0, 65.6), (9, 53.5, 24.5), (13, 81.2, 41.4), (12, 64.5, 32.8),
                    (15, 84.0, 6.6), (45, 95.5, 44.4), (16, 116.0, 59.0), (17, 134.5, 60.9), (48, 98.0, 6.2), (50, 125.0, 44.4), (53, 126.4, 6.2)]:
        flag(ax, S, par, k, x, y)

LEGEND = ("◇ siyah: proses akımı no.   ◇ mavi: yardımcı akışkan akım no.   ◇ turuncu/kesik: erimiş tuz çevrimi   sarı kutu: T/P bayrağı   LPS: alçak basınçlı buhar 400 kPa(a)   cw: soğutma suyu 25→35 °C   chw: soğutulmuş su 7→12 °C   fuel gas: doğal gaz   HPS kullanılmamıştır.\n"
          "Akım numaraları soldan sağa verilmiştir. Ölçeksiz; ekipman boyutlandırması içermez. SI birimler; değerler 4 anlamlı rakam. Q: ısı yükü, W: mil işi. Q>0: üniteye verilen ısı; boyut ve kontrol ekipmanı gösterilmemiştir.")

def compute_numbering(S, D, par):
    """Diyamantların x konumuna göre soldan sağa akım numarası ata (eşitse yukarıdakine önce)"""
    fig = plt.figure(figsize=(16.5, 11.7)); ax = fig.add_subplot(111)
    draw_drawing(ax, S, D, par); plt.close(fig)
    order = sorted(POS, key=lambda k: (round(POS[k][0] / 2.5), -POS[k][1]))
    MAP.clear(); MAP.update({old: i + 1 for i, old in enumerate(order)})
    return dict(MAP)

def _style_table(t, fs, hdr='#333'):
    t.auto_set_font_size(False); t.set_fontsize(fs)
    for (r, c), cell in t.get_celld().items():
        cell.set_linewidth(.3)
        if r == 0: cell.set_facecolor(hdr); cell.get_text().set_color('w'); cell.get_text().set_fontweight('bold')

def process_ids(S): return sorted([k for k in S], key=lambda k: nn(k))
def utility_ids(U): return sorted(U, key=lambda k: nn(k))

def process_table_df(S, par):
    rows = []
    for k in process_ids(S):
        st = S[k]; n = st['V'] + st['L']; N = n.sum()
        rows.append((nn(k), st['T'], par['P'][k] * 100, st['V'].sum() / N, float(n @ MW), N, n[0], n[1], n[2], n[3]))
    return pd.DataFrame(rows, columns=['Akim', 'T_C', 'P_kPa', 'BuharKesri', 'kg_h', 'kmol_h', 'IPA_kmol_h', 'Aseton_kmol_h', 'H2_kmol_h', 'Su_kmol_h'])

UT_MW = {'LPS': 18.015, 'su': 18.015, 'Soğutma': 18.015, 'Soğutulmuş': 18.015, 'Doğal': 16.043, 'Hava': 28.85}
def utility_df(U, E=None):
    rows = []
    for k in utility_ids(U):
        fl, yer, T, P, m = U[k]
        vf = 1.0 if (fl.startswith('LPS 4') or fl.startswith('Doğal') or fl.startswith('Hava') or fl.startswith('Baca')) else 0.0
        if fl.startswith('Baca'): mw = (m / sum(E['flue'].values())) if E else None
        elif fl.startswith('Erimiş'): mw = None
        else: mw = [v for kk, v in UT_MW.items() if fl.startswith(kk)][0] if any(fl.startswith(kk) for kk in UT_MW) else None
        rows.append((nn(k), fl, yer, T, P * 100, vf, m, (m / mw if mw else None)))
    return pd.DataFrame(rows, columns=['Akim', 'Akiskan', 'Baglanti', 'T_C', 'P_kPa', 'BuharKesri', 'kg_h', 'kmol_h'])

def duty_table(D, U):
    ids = {'E-102': (20, 21), 'E-105': (22, 23), 'E-107': (24, 25), 'E-103': (26, 27), 'E-109': (28, 29), 'E-104': (30, 31), 'E-106': (32, 33), 'E-108': (34, 35)}
    fl = {'E-102': 'LPS', 'E-105': 'LPS', 'E-107': 'LPS', 'E-103': 'cw', 'E-109': 'cw', 'E-104': 'cw', 'E-106': 'cw', 'E-108': 'chw'}
    key = {'P-101A/B': 'P101', 'E-102': 'E102', 'E-101': 'E101', 'R-101': 'R101', 'F-101': 'F101', 'E-103': 'E103', 'T-101': 'T101', 'P-103': 'P103',
           'E-109': 'E109', 'E-104': 'E104', 'E-105': 'E105', 'E-106': 'E106', 'E-107': 'E107', 'E-108': 'E108'}
    rows = []
    for code, kk in key.items():
        q = D[kk]
        if code in ids:
            a, b = ids[code]; ak = f"{fl[code]} ({nn(a)}→{nn(b)})"; deb = f"{f4(U[a][4])} kg/h"
        elif code == 'F-101':
            ak = f"fuel gas ({nn(36)}) + hava ({nn(37)}) → baca gazı ({nn(38)})"; deb = f"{f4(U[36][4])} kg/h CH4"
        elif code == 'R-101':
            ak = f"Erimiş tuz ({nn(39)}→{nn(40)}), F-101 ile aynı yük"; deb = f"{f4(U[39][4])} kg/h"
        elif code == 'E-101':
            ak = 'Proses-proses'; deb = '-'
        elif code == 'T-101':
            ak = 'E-109 pump-around ile alınır'; deb = '-'
        else:
            ak = 'Elektrik'; deb = '-'
        rows.append(dict(Ekipman=code, Yuk=('+' if q > 0 else '') + f4(q), Akiskan=ak, Debi=deb))
    return pd.DataFrame(rows)

def utility_table(U, E=None):
    d = utility_df(U, E)
    return pd.DataFrame([[r.Akim, r.Akiskan, r.Baglanti, f4(r.T_C), f4(r.P_kPa), f4(r.BuharKesri), f4(r.kg_h), (f4(r.kmol_h) if r.kmol_h == r.kmol_h and r.kmol_h is not None else '-')] for _, r in d.iterrows()],
                        columns=['Akım no', 'Akışkan', 'Bağlantı', 'T (°C)', 'P (kPa)', 'Buhar kesri', 'Debi (kg/h)', 'Mol debisi (kmol/h)'])

def make_pfd(S, D, U, E, par, fname='PFD_aseton_grup8', date_txt=''):
    from matplotlib.backends.backend_pdf import PdfPages
    compute_numbering(S, D, par)
    fig = plt.figure(figsize=(16.54, 11.69))
    gs = fig.add_gridspec(3, 2, height_ratios=[8.9, 1.5, 1.55], width_ratios=[3.5, 1.3], left=.01, right=.99, top=.992, bottom=.008, hspace=.035, wspace=.012)
    ax = fig.add_subplot(gs[0, :]); draw_drawing(ax, S, D, par)
    # ---- proses akım tablosu
    ax2 = fig.add_subplot(gs[1, 0]); ax2.axis('off')
    df = process_table_df(S, par)
    lab = ['T (°C)', 'P (kPa)', 'x_v', 'm kg/h', 'n kmol/h', 'n IPA', 'n Aseton', 'n H2', 'n Su']
    cols = ['T_C', 'P_kPa', 'BuharKesri', 'kg_h', 'kmol_h', 'IPA_kmol_h', 'Aseton_kmol_h', 'H2_kmol_h', 'Su_kmol_h']
    cells = [[f4(v) for v in df[c]] for c in cols]
    t = ax2.table(cellText=cells, rowLabels=lab, colLabels=[str(k) for k in df.Akim], cellLoc='center', bbox=[0.07, 0.0, 0.93, 0.9])
    _style_table(t, 4.4)
    ax2.set_title('PROSES AKIM TABLOSU (akım no. PFD ile aynıdır; n = bileşen mol debisi, kmol/h; x_v = buhar kesri)', loc='left', fontsize=6.5, fontweight='bold', pad=1)
    # ---- yardımcı akım tablosu
    ax4 = fig.add_subplot(gs[2, 0]); ax4.axis('off')
    ud = utility_df(U, E)
    lab = ['Akışk.', 'Bağl.', 'T (°C)', 'P kPa', 'x_v', 'kg/h']
    short = lambda s: s.replace('Soğutma suyu (cw)', 'cw').replace('Soğutulmuş su (chw)', 'chw').replace('LPS 4 bar(a), doygun buhar', 'LPS').replace('LPS yoğuşuğu', 'LPS yoğ.').replace('Doğal gaz (CH4)', 'fuel gas').replace('Hava (%15 fazla)', 'hava').replace('Baca gazı (CO2, H2O, O2, N2)', 'baca gazı').replace('Erimiş tuz (soğuk, basınçlı)', 'tuz soğuk').replace('Erimiş tuz (sıcak)', 'tuz sıcak').replace('Erimiş tuz (soğuk)', 'tuz soğuk')
    cells = [[short(v) for v in ud.Akiskan], [v.replace(' giriş', ' gir.').replace(' çıkış', ' çık.').replace('R-101 -> P-102', 'R-101→P-102').replace('F-101 -> R-101', 'F-101→R-101').replace('P-102 -> F-101', 'P-102→F-101') for v in ud.Baglanti],
             [f4(v) for v in ud.T_C], [f4(v) for v in ud.P_kPa], [f4(v) for v in ud.BuharKesri], [f4(v) for v in ud.kg_h]]
    t4 = ax4.table(cellText=cells, rowLabels=lab, colLabels=[str(k) for k in ud.Akim], cellLoc='center', bbox=[0.07, 0.17, 0.93, 0.75])
    _style_table(t4, 3.9, '#0b5394')
    ax4.set_title('YARDIMCI AKIŞKAN (UTILITY) AKIM TABLOSU', loc='left', fontsize=6.5, fontweight='bold', pad=1)
    # ---- yük özeti + başlık bloğu
    ax3 = fig.add_subplot(gs[1:, 1]); ax3.axis('off')
    dt = duty_table(D, U)
    cells = [[r.Ekipman, r.Yuk, r.Akiskan, r.Debi] for _, r in dt.iterrows()]
    t3 = ax3.table(cellText=cells, colLabels=['Ekipman', 'Yük (kW)', 'Utility (akım no)', 'Debi'], cellLoc='center', colWidths=[.16, .13, .47, .24], bbox=[0, 0.38, 1, 0.58])
    _style_table(t3, 4.0)
    ax3.set_title('EKİPMAN ISI/İŞ YÜKLERİ (kW)', loc='left', fontsize=6.5, fontweight='bold', pad=1)
    tb = [['Ders / Proje', 'Tasarım I (T1-01) · Proje 1'], ['Başlık', 'Aseton tesisi ön PFD (IPA dehidrojenasyonu)'],
          ['Grup No', f"{par['GRUP']}"], ['Kapasite', f"{par['CAP_TON_YIL']:,.0f} ton/yıl aseton ({par['SAAT']:.0f} h/yıl)".replace(',', ' ')],
          ['Tarih', date_txt], ['Çizim no', 'PFD-T1-G8 · Ölçeksiz']]
    t6 = ax3.table(cellText=tb, cellLoc='left', colWidths=[.25, .75], bbox=[0, 0.0, 1, 0.33])
    t6.auto_set_font_size(False); t6.set_fontsize(5.6)
    for (r, c), cell in t6.get_celld().items():
        cell.set_linewidth(.8)
        if r == 0: cell.set_facecolor('#eef3f8'); cell.get_text().set_fontweight('bold')
    ax3.text(0, -0.02, '', fontsize=1)
    ax4.text(0.0, 0.0, LEGEND, fontsize=4.5, va='bottom', ha='left', color='#222', transform=ax4.transAxes)
    fig.savefig(fname + '.png', dpi=200)
    with PdfPages(fname + '.pdf') as pdf:
        pdf.savefig(fig)
    return fig

# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REFS = [
 ("[1]", "NIST Chemistry WebBook, SRD 69: Acetone (67-64-1) — ΔfH(g), Cp(g) tablosu, ΔvapH, Antoine sabitleri, Cp(l). https://webbook.nist.gov/cgi/cbook.cgi?ID=C67641&Mask=1E9F", "görüldü"),
 ("[2]", "NIST Chemistry WebBook: Hydrogen (1333-74-0) — Shomate katsayıları (298-1000 K). https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Type=JANAFG&Plot=on", "görüldü"),
 ("[3]", "Su buharı Shomate katsayıları (NIST, 500-1700 K): Kitchin, CMU. https://kitchingroup.cheme.cmu.edu/blog/2013/02/01/Water-gas-shift-equilibria-via-the-NIST-Webbook/ (ikincil; 298 K'de Cp=33.59, NIST 33.58 ile testlendi)", "ikincil kaynaktan görüldü"),
 ("[4]", "2-Propanol (IPA) termofiziksel verileri: Cheméo (NIST verilerinin derlemesi). https://www.chemeo.com/cid/24-809-7/2-Propanol", "ikincil derleme; NIST IPA sayfasına erişilemedi"),
 ("[5]", "IPA-su azeotropu (80.4 °C, kütle %87.8 IPA): ABD Patentleri 4,666,560 / 4,698,137 / 4,693,789. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4666560", "görüldü"),
 ("[6]", "Rice Univ. CENG 403 (1998), Production of Acetone by Catalytic Dehydrogenation of IPA (Turton akış şemasının tarifi: 2 bar, 350 °C, X=%85-92). http://www.owlnet.rice.edu/~ceng403/gr1998/acetone.html", "görüldü (Turton kitabı görülmedi)"),
 ("[7]", "Rice Univ. CENG 403 (2011), The Production of Acetone (ZnO/ZrO2 katalizör, 300-400 °C, endotermik). http://www.owlnet.rice.edu/~ceng403/gr11298/acetone", "görüldü"),
 ("[8]", "ABD Patenti 4,380,673 — sekonder alkollerin buhar fazında, 300-550 °C'de katalizörle dehidrojenasyonu. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4380673", "görüldü"),
 ("[9]", "ABD Patenti 4,472,593 — IPA→aseton, Cu-Zn-Cr katalizör; 'brass spelter' ticari referans (400 °C, %70 dönüşüm, %99.4 seçicilik); γ-alümina destekte çok propilen oluşur. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4472593", "görüldü"),
 ("[10]", "Sander, R., Compilation of Henry's law constants (v5), Atmos. Chem. Phys. 23, 10901 (2023); aseton: https://henrys-law.org/henry/casrn/67-64-1", "görüldü"),
 ("[11]", "NPTEL Mass Transfer, Modül 7: 'optimum absorpsiyon faktörü A = 1.2-2'. https://archive.nptel.ac.in/content/storage2/courses/103103027/module7/lec6/3.html (sayfa kaynak göstermiyor; atıf Treybal'a işaret ediyor)", "görüldü"),
 ("[12]", "EngineersUniverse, Absorption/Stripping Column Design Guide: 'A = 1.4-2'. https://engineersuniverse.com/studios/chemical-process/absorption-stripping-column-design-guide", "görüldü"),
 ("[13]", "Wikipedia, Isopropyl alcohol: yoğunluk 0.786 g/cm3, kb 82.6 °C, azeotrop 80.37 °C. https://en.wikipedia.org/wiki/Isopropyl_alcohol ; Properties of water: ΔvapH(100 °C)=40.65 kJ/mol", "görüldü"),
 ("[14]", "Doygun buhar tablosu (4 bar: 143.6 °C, hfg=2133 kJ/kg). https://www.engineeringtoolbox.com/saturated-steam-properties-d_101.html ; CH4 ΔfH: Engineering ToolBox organik bileşik tablosu", "görüldü; ders kitabı tablosuyla teyit edin"),
 ("[15]", "ChemSep Wilson ve NRTL etkileşim parametreleri (IPA-su, aseton-su): thermo (C. Bell) deposu, github.com/CalebBell/thermo, Interaction Parameters/ChemSep/wilson.json, nrtl.json", "görüldü (yön seçimi bu çalışmada testle yapıldı)"),
 ("[17]", "Wikipedia, Acetone: dünya üretimi ≈6.7 Mt (2010), ≈%83'ü kümen (cumene) yoluyla; kullanım: ≈1/3 çözücü, ≈1/4 aseton siyanohidrin (MMA), ≈%20 bisfenol-A. https://en.wikipedia.org/wiki/Acetone", "görüldü (ikincil)"),
 ("[18]", "Wikipedia, Cumene process: alkilasyon ≈30 bar/250 °C, oksidasyon ≈5 atm, Hock yeniden düzenlenmesi; ≈0.6 t aseton/t fenol (1:1 mol). https://en.wikipedia.org/wiki/Cumene_process", "görüldü (ikincil)"),
 ("[16]", "Turton, Bailie, Whiting, Shaeiwitz, Analysis, Synthesis and Design of Chemical Processes; Seader & Henley, Separation Process Principles; Treybal, Mass Transfer Operations (Kremser denklemi) — kitaplar görülmedi, yalnızca yöntem atfı.", "KİTAP GÖRÜLMEDİ"),
]

def _fonts():
    d = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    pdfmetrics.registerFont(TTFont('DV', os.path.join(d, 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DVB', os.path.join(d, 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DVI', os.path.join(d, 'DejaVuSans-Oblique.ttf')))
    pdfmetrics.registerFontFamily('DV', normal='DV', bold='DVB', italic='DVI', boldItalic='DVB')

def build_report(S, D, U, E, C, par, dchk, ex, sens, vd, bal, fname='Rapor_aseton_grup8.pdf'):
    _fonts()
    B = ParagraphStyle('b', fontName='DV', fontSize=8.2, leading=10.2, alignment=TA_JUSTIFY, spaceAfter=2)
    H = ParagraphStyle('h', fontName='DVB', fontSize=9.6, leading=11.5, spaceBefore=3.5, spaceAfter=1.5, keepWithNext=1, textColor=colors.HexColor('#0b3d6b'))
    T = ParagraphStyle('t', fontName='DVB', fontSize=11.5, leading=13.5, spaceAfter=1)
    Sm = ParagraphStyle('s', fontName='DV', fontSize=6.8, leading=8.2)
    Tc = ParagraphStyle('tc', fontName='DV', fontSize=6.6, leading=7.8)
    Tb = ParagraphStyle('tb', fontName='DVB', fontSize=6.6, leading=7.8, textColor=colors.white)
    P = lambda s, st=B: Paragraph(s, st)
    def tbl(data, widths):
        rows = [[Paragraph(str(c), Tb if i == 0 else Tc) for c in r] for i, r in enumerate(data)]
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .3, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
                               ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8), ('LEFTPADDING', (0, 0), (-1, -1), 2), ('RIGHTPADDING', (0, 0), (-1, -1), 2)]))
        return t
    N = nn
    n = lambda k: S[k]['V'] + S[k]['L']
    Q = D
    lps = Q['E102'] + Q['E105'] + Q['E107']
    prod = kg(S[17]); X = par['X']
    r_rx = X * n(6)[0]
    ok_vd = int((vd['Sonuc'] == 'GEÇTİ').sum())
    st = []
    st.append(P("Asetonun İzopropanolün Katalitik Dehidrojenasyonuyla Üretimi — Ön Tasarım Raporu", T))
    st.append(P("Tasarım I (T1-01) · Grup 8 · 85 000 t/yıl aseton · Tarih 08.10.2026 · Akım numaraları A3 PFD ile birebir aynıdır (soldan sağa); birimler SI.", Sm))
    # 1
    st.append(P("1. Tasarım bazı", H))
    st.append(P(f"Kapasite 85 000 t/yıl, çalışma 8000 h/yıl → ürün = 85 000 000 / 8000 = <b>{int(round(prod))}</b> kg/h (akım {N(17)}). Ürün: kütlece <b>≥ %99.5</b> aseton, <b>≤ %0.5 su</b> (tasarım %{par['W_SU_URUN']*100:.1f} su, %{(1-par['W_SU_URUN'])*100:.1f} aseton), "
                f"<b>sıvı, 25 °C</b>, depoya. Besleme (akım {N(1)}): kütlece %{par['W_IPA_BESLEME']*100:.0f} IPA / %{(1-par['W_IPA_BESLEME'])*100:.0f} su, {f4(kg(S[1]))} kg/h ({f4(n(1)[0])} kmol/h IPA, {f4(n(1)[3])} kmol/h su); bileşim IPA–su azeotropuna (80.4 °C, %87.8 [5]) yakındır. "
                f"<b>Aseton 56 °C'de kaynar:</b> ürün C-101 üstünde {f4(E['T_D1'])} °C'de (110 kPa) sıvı çıkar ve E-108'de 25 °C'ye soğutulur; 25 °C'de aseton buhar basıncı {f4(Psat(1,25.0)*100)} kPa &lt; 101.3 kPa olduğundan sıvı kalır ve atmosfer basıncındaki depoda 31 K normal kaynama noktasının altındadır.", B))
    # 2
    st.append(P("2. Kimya: reaksiyon, T/P, dönüşüm, seçicilik", H))
    st.append(P(f"<b>(CH<sub>3</sub>)<sub>2</sub>CHOH(g) → (CH<sub>3</sub>)<sub>2</sub>CO(g) + H<sub>2</sub>(g)</b>, ΔH<sub>298</sub> = +{f4(C['dH25'])} kJ/mol (endotermik; NIST ≈ +55.3). Gaz fazı, <b>Cu/Zn esaslı katalizör</b>, <b>350 °C, ≈2.2 bar</b> (reaktör girişi 220 kPa), tek geçiş <b>dönüşüm X = %{X*100:.0f}</b>. "
                f"<b>Neden katalizörlü?</b> Termodinamik yüksek sıcaklığı ister: K<sub>eq</sub>(25 °C) = {C['Keq25']:.1e}, K<sub>eq</sub>(350 °C) = {f4(C['Keq'])}; 350 °C ve 220 kPa'da denge dönüşümü %{C['X_eq']*100:.1f} olup tasarım X bunun altındadır. Hız ve seçicilik katalizöre bağlıdır: sekonder alkoller 300–550 °C'de katalizör üzerinde buhar fazında dehidrojene edilir [8]; "
                "ticari 'brass spelter' 400 °C'de %70 dönüşüm ve %99.4 seçicilik verir, γ-alümina destekte ise dehidratasyonla çok propilen oluşur [9]. "
                f"<b>Seçicilik:</b> tasarımda aseton için <b>%100</b> alınmıştır (kaynak: ≈%99.4 [9]). <b>Yan reaksiyonlar ihmal edilmiştir</b> çünkü: (i) Cu/Zn katalizörde dehidratasyon (IPA → propilen + H<sub>2</sub>O) ve eter oluşumu ancak asidik destekte baskındır [9]; (ii) aseton kondensasyonu (mesitil oksit, diaseton alkol) ve parçalanma (CO + CH<sub>4</sub>) bu T'de ve 2 bar'da küçüktür (nicel kaynak bulunamadı, <i>varsayım</i>); (iii) kinetik veri olmadan ayrı yan ürün akımı tanımlamak belirsizlik katar. "
                f"Etkisi: seçicilik %99.4 olsaydı ≈{f4(0.006*r_rx)} kmol/h IPA ({f4(0.006*r_rx*MW[0])} kg/h) yan ürüne gider, ürün ≈%0.6 azalır; propilen H<sub>2</sub>-zengin vente (akım {N(13)}), ağır ürünler dip suyuna gelir; hammadde ≈%0.6 artırılarak giderilir.", B))
    # 3
    st.append(P("3. Araştırma özeti (kullanım, üretim amacı, rota, IPA+su işlenmesi)", H))
    st.append(P("<b>Kullanım ve amaç:</b> aseton ağırlıkla çözücü (≈1/3), aseton siyanohidrin → metil metakrilat (≈1/4) ve bisfenol-A (≈%20) üretiminde kullanılır; dünya üretimi ≈6.7 Mt/yıl'dır (2010) [17]. Üretim amacı bu ara ürünlere ve çözücü pazarına arz sağlamaktır. "
                "<b>Fenol (kümen) rotası:</b> dünya asetonunun ≈%83'ü benzen + propilenden kümen → kümen hidroperoksit → (asit, Hock) fenol + aseton yoluyla, fenolün yan ürünü olarak elde edilir (≈0.6 t aseton/t fenol; alkilasyon ≈30 bar/250 °C, oksidasyon ≈5 atm; yan ürün asetofenon, α-metilstiren) [17, 18]; "
                "aseton üretimi fenol talebine bağlıdır. <b>IPA rotası</b> (bu proje): tek ürün (aseton) + H<sub>2</sub>; daha basit ve ılımlı koşul, fakat IPA hammaddesi (propilen hidrasyonu) maliyetlidir, endotermik olduğu için ısı beslemek gerekir; fenol bağlantısından bağımsız aseton sağladığı için küçük/orta ölçekte tercih edilir. "
                "<b>IPA+su işlenmesi:</b> karışım buharlaştırılır, reaktörde dönüşen IPA dışındaki IPA ve su aynen geçer; çıkış soğutulup H<sub>2</sub> ayrılır, aseton gazdan yıkanır, C-101'de aseton, C-102'de IPA/su azeotropu (geri dönüş) ve atık su ayrılır. "
                "<b>Türkiye üretim kapasitesi:</b> güvenilir bir kaynak <b>bulunamadı</b> ve sayı uydurulmamıştır; grup TÜİK/UN Comtrade (HS 2914.11) ve ilgili şirket raporlarından tamamlamalıdır.", B))
    # 4
    st.append(P("4. Proses tanımı ve seçilmiş akımlar", H))
    st.append(P(f"Taze besleme ({N(1)}) ve geri dönüş ({N(2) if False else N(2)}) <b>V-100</b>'de karışır; <b>P-101A/B</b> 320 kPa'a basar; <b>E-102</b> (LPS) doygun buhar üretir ({N(5)}, T<sub>çiğ</sub> = {f4(E['T5'])} °C); <b>E-101</b> reaktör çıkışıyla {f4(S[6]['T'])} °C'ye kızdırır ({N(6)}). "
                f"<b>R-101</b> (çok borulu, katalizörlü, erimiş tuzla ısıtılır; tuz <b>F-101</b> fırında ısıtılıp <b>P-102</b> ile dolaştırılır) {f4(par['T_R'])} °C'de reaksiyonu yürütür ({N(7)}). Çıkış E-101'de ({N(8)}) ve <b>E-103</b>'te 40 °C'ye soğutulur ({N(9)}); <b>V-101</b> gaz ({N(10)}) ve sıvıyı ({N(11)}) ayırır. "
                f"Gazdaki aseton <b>T-101</b>'de suyla ({N(12)}) yıkanır; H<sub>2</sub>-zengin vent {N(13)}, zengin su {N(14)} ile akım {N(11)} birleşip C-101 beslemesi ({N(15)}) olur. C-101 üstü aseton ({N(16)}) <b>E-108</b>'de soğutulup ürün ({N(17)}) olur; dip ({N(18)}) <b>C-102</b>'ye gider: üstten azeotrop geri dönüşü ({N(2)}), dipten atık su ({N(19)}). Kolon yoğuşturucuları cw, rebolyerleri LPS ile çalışır; iç akımlar PFD'dedir.", B))
    desc = {1: 'Taze besleme', 2: 'Geri dönüş', 5: 'Reaktör girişi (buhar)', 7: 'Reaktör çıkışı', 10: 'Flaş gazı', 12: 'Yıkama suyu', 13: 'H2-zengin vent', 15: 'C-101 beslemesi', 17: 'Ürün (depoya)', 19: 'Atık su'}
    rows = [['Akım', 'Tanım', 'T (°C)', 'P (kPa)', 'kg/h', 'IPA %', 'Aseton %', 'H2 %', 'Su %']]
    for k in sorted(desc, key=N):
        w_ = n(k) * MW; w_ = w_ / w_.sum() * 100
        rows.append([N(k), desc[k], f4(S[k]['T']), f4(par['P'][k] * 100), f4(kg(S[k])), f4(w_[0]), f4(w_[1]), f4(w_[2]), f4(w_[3])])
    st.append(P("<b>Tablo 1.</b> Seçilmiş akımlar (kütle %; tüm akımlar PFD'deki tabloda).", Sm))
    st.append(tbl(rows, [1.0 * cm, 4.2 * cm, 1.5 * cm, 1.6 * cm, 1.8 * cm, 1.6 * cm, 1.8 * cm, 1.5 * cm, 1.5 * cm]))
    # 5 varsayımlar
    st.append(P("5. Varsayımlar (numaralı, gerekçeli)", H))
    A = [
     ("Kararlı rejim, 8000 h/yıl, ürün 10 625 kg/h.", "Ödev verisi."),
     (f"Besleme %{par['W_IPA_BESLEME']*100:.0f} IPA / %{(1-par['W_IPA_BESLEME'])*100:.0f} su.", "Azeotropa yakın ticari IPA/su bileşimi; geri dönüşle (azeotrop) tutarlı."),
     ("Aseton seçiciliği %100 (yan reaksiyonlar ihmal).", "Bölüm 2: Cu/Zn katalizörde ≈%99.4 [9]; etki nicelendi."),
     (f"Tek geçiş dönüşümü sabit, X = %{X*100:.0f}; kinetik/katalizör kütlesi yok.", f"X < X<sub>eq</sub> = {f4(C['X_eq'])}; Turton aralığı %85–92 [6]."),
     ("Gaz ideal; sıvı karışım Wilson (IPA–su, aseton–su), aseton–IPA ideal.", "Düşük basınç; ChemSep parametreleri [15]; aseton–IPA parametresi bulunamadı."),
     ("Entalpi: 25 °C elementlerden referans, ideal karışım, sabit sıvı Cp.", "Kaba denklik için yeterli; NIST verileri [1–4]."),
     ("Aseton absorberi: A = 1.4, K Henry sabitinden (35 °C, 180 kPa), %99.5 geri kazanım.", "Ders kitabı aralığı A=1.2–2 [11, 12]; Wilson seyreltik uçta Henry ile uyuşmaz."),
     (f"Kolonlar kısa yol: R = {par['RR_FACTOR']}·R<sub>min</sub>, tam yoğuşturucu, kaynar sıvı reflü, kettle rebolyer; aseton geri kazanımı %{par['REC_ACE_C1']*100:.1f}, IPA %{par['REC_IPA_C2']*100:.1f}.", "Yaygın pratik 1.2–1.5; kısa yol ön tasarım için yeterli."),
     ("Basınçlar: besleme 100→320 kPa, reaktör 220 kPa, flaş/absorber 180/170 kPa, kolonlar 110 kPa; ΔP'ler sabit varsayım.", "Boyutlandırma yapılmadığından ΔP kabulü."),
     ("Pompa verimi %70; fırın verimi %85, %15 fazla hava; tuz 450→390 °C, Cp = 1.56 kJ/kg/K.", "Tipik değerler; tuz Cp'si <b>doğrulanmadı</b>."),
     (f"Utility: LPS 400 kPa(a) ({f4(T_LPS)} °C), cw 25→35 °C, chw 7→12 °C (E-108), ΔT<sub>min</sub> = 5 K.", "cw ile 25 °C ürün sıcaklığına inilemez; HPS gerekmedi (tuz çevrimi fırınla)."),
     ("Reflü kabı, vanalar ve reflü pompaları gösterilmemiş; ısı kaybı yok.", "Ödev PFD'yi ana ekipmanla sınırlar; boyutlandırma istenmiyor."),
    ]
    rows = [['No', 'Varsayım', 'Gerekçe']] + [[i + 1, a, b] for i, (a, b) in enumerate(A)]
    st.append(tbl(rows, [0.7 * cm, 9.6 * cm, 7.7 * cm]))
    # 6 kütle
    st.append(P("6. Kütle denkliği (genel ve ekipman bazında)", H))
    mi, mo = C['mass_in'], C['mass_out']
    st.append(P(f"<b>Genel:</b> giriş (akım {N(1)} + {N(12)}) = {f4(mi)} kg/h; çıkış (vent {N(13)} + ürün {N(17)} + atık su {N(19)}) = {f4(mo)} kg/h; hata = {100*(mi-mo)/mi:.1e} % (&lt; %1). "
                f"Element (C, H, O): giriş [{', '.join(f4(v) for v in C['el_in'])}] = çıkış [{', '.join(f4(v) for v in C['el_out'])}] kmol/h. "
                f"<b>Örnek hesap (R-101):</b> girişteki IPA {f4(n(6)[0])} kmol/h; r = X·F = {X:.2f}·{f4(n(6)[0])} = {f4(r_rx)} kmol/h → aseton ve H<sub>2</sub> + {f4(r_rx)} kmol/h, IPA −{f4(r_rx)} kmol/h; kütle: giriş {f4(kg(S[6]))} = çıkış {f4(kg(S[7]))} kg/h. "
                f"<b>Ürün suyu:</b> {f4(S[17]['L'][3]*MW[3])} / {int(round(prod))} = %{C['w_water_prod']*100:.2f}. <b>Fırın:</b> CH<sub>4</sub> {f4(U[36][4])} + hava {f4(U[37][4])} − baca gazı {f4(U[38][4])} = {U[36][4]+U[37][4]-U[38][4]:.1e} kg/h.", B))
    rows = [['Ekipman', 'Giriş → çıkış akımları', 'Giriş (kg/h)', 'Çıkış (kg/h)', 'Hata (%)', 'Q (kW)', 'ΔE (kW)']]
    for _, r in bal.iterrows():
        rows.append([r.Ekipman, f"{r.Giris} → {r.Cikis}", f4(r.m_in), f4(r.m_out), f"{abs(r.hata_pct):.1e}", f4(r.Q_kW), f"{r.dE:.1e}"])
    st.append(P("<b>Tablo 2.</b> Ekipman bazında kütle ve enerji kapanışı (Q &gt; 0: üniteye verilen). Kolon rebolyer yükleri denklikten türetildiğinden o satırlarda enerji kapanışı yapısaldır; bağımsız kontrol element ve tüm-tesis dengesidir.", Sm))
    st.append(tbl(rows, [3.0 * cm, 3.6 * cm, 2.4 * cm, 2.4 * cm, 1.8 * cm, 2.4 * cm, 2.4 * cm]))
    # 7 enerji
    st.append(P("7. Kaba enerji denkliği ve utility", H))
    st.append(P(f"Her ekipman için Σ(giriş entalpisi) + Q = Σ(çıkış entalpisi) yazılmıştır (Tablo 2, 5). Tüm tesis: enerji kapanış farkı {C['E_err']:.1e} kW. "
                f"<b>Örnek (E-102):</b> Q = (H<sub>{N(5)}</sub> − H<sub>{N(4) if False else N(4)}</sub>) = {f4(Q['E102'])} kW → LPS {f4(U[20][4])} kg/h (hfg = {f4(H_FG_LPS)} kJ/kg). "
                f"Toplam LPS {f4(lps)} kW ({f4(lps*3600/H_FG_LPS)} kg/h; E-105 %{Q['E105']/lps*100:.0f}, çünkü C-101 beslemesi ≈%80 sudur); R-101/F-101 {f4(Q['R101'])} kW (fırın verimiyle {f4(E['Q_fuel'])} kW = {f4(U[36][4])} kg/h CH<sub>4</sub>); soğutma: E-103 {f4(-Q['E103'])}, E-104 {f4(-Q['E104'])}, E-106 {f4(-Q['E106'])}, E-109 {f4(-Q['E109'])} kW (cw), E-108 {f4(-Q['E108'])} kW (chw). "
                f"Isı entegrasyonu yalnızca E-101 ile yapılmıştır; {N(19)} numaralı atık su (107 °C, {f4(kg(S[19]))} kg/h) ile ≈1 MW geri kazanım olasılığı <b>denenmemiştir</b>.", B))
    # 8 jüri
    st.append(P("8. Yıkama suyu ve A değeri", H))
    a = sens['A']; ws = S[12]['L'][3] * MW[3]
    st.append(P(f"Hammaddedeki su reaksiyona girmez; yıkama suyu ({N(12)}) ise <i>tasarım seçimidir</i>: V-101 gazındaki aseton (oluşanın %{S[10]['V'][1]/n(7)[1]*100:.0f}'i) yıkanmazsa vente gider. A = L/(K·G); A küçüldükçe su azalır, kademe artar (A→1'de sonsuz). A = 1.4 aralığın [11, 12] alt ucudur: N = {f4(E['N_abs'])} teorik kademe, su {f4(ws)} kg/h (ürünün {f4(ws/prod)} katı). Tablo 3 ekonomik optimizasyon değil, yalnızca ödünleşimdir.", B))
    rows = [['A', 'Yıkama suyu (kmol/h)', 'Su/ürün (kg/kg)', 'Teorik kademe', 'Toplam LPS (kW)']]
    for _, r in a.iterrows(): rows.append([f"{r.A:.1f}", f4(r.Yikama_suyu_kmol_h), f4(r.Su_urun_oran), f4(r.N_teorik), f4(r.LPS_toplam_kW)])
    st.append(P("<b>Tablo 3.</b> Absorpsiyon faktörü duyarlılığı (aseton geri kazanımı %99.5).", Sm))
    st.append(tbl(rows, [1.5 * cm, 4 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]))
    # 9 doğrulama
    st.append(P("9. Doğrulama durumu ve sınırlamalar", H))
    st.append(P(f"<b>Proses simülatörü (HYSYS/ChemCAD) ile doğrulama bu çalışmada YAPILMAMIŞTIR</b>; hesap Python kısa yol modelidir. Yapılması gereken: HYSYS'te Wilson/NRTL, dönüşüm reaktörü X=%{X*100:.0f}, flaş 40 °C, absorber, C-101/C-102 (R ve ürün kompozisyonu hedefli) kurulup R-101/E-102/E-105/E-107 yükleri, reflü oranları ve akım {N(17)} bileşimi bu rapordaki değerlerle karşılaştırılmalıdır. "
                f"Kod içi testler: veri/model {ok_vd}/{len(vd)-1} geçti (1 bilgi satırı), tasarım kontrolleri {int((dchk['Sonuc']=='GEÇTİ').sum())}/{len(dchk)} geçti. "
                "<b>Sınırlamalar:</b> aseton–IPA VLE ideal; aseton–su seyreltik uçta Henry ile düzeltilmiş, deneysel y–x ile tam karşılaştırılmamıştır; reaktör sabit dönüşümlüdür, 300→350 °C ısınma bölgesi incelenmemiştir; reflü kabı/pompası/vanalar çizilmemiştir; tuz Cp'si ve Türkiye kapasite verisi doğrulanmamıştır; ekonomik/emniyet analizi kapsam dışıdır.", B))
    # 10 ekipman tablosu
    st.append(P("10. Ekipman tablosu (boyutlandırma yok; görev = enerji denkliğinden, kW)", H))
    eq = equipment_table(D, ex)
    rows = [['Kod', 'Ad', 'Tip', 'İşlev', 'Görev (kW)', 'Utility']] + [[r.Kod, r.Ad, r.Tip, r.Islev, r.Gorev_kW, r.Utility] for _, r in eq.iterrows()]
    st.append(tbl(rows, [1.5 * cm, 3.1 * cm, 3.6 * cm, 5.6 * cm, 1.7 * cm, 2.5 * cm]))
    st.append(P("11. Kaynakça (durum: bu çalışmada görülen / görülmeyen)", H))
    t = Table([[Paragraph(a_, Sm), Paragraph(b_, Sm), Paragraph(c_, Sm)] for a_, b_, c_ in sorted(REFS, key=lambda r: int(r[0].strip('[]')))], colWidths=[0.8 * cm, 14.0 * cm, 3.2 * cm])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), .4), ('BOTTOMPADDING', (0, 0), (-1, -1), .4), ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1)]))
    st.append(t)
    doc = SimpleDocTemplate(fname, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm,
                            title='Aseton Tesisi Ön Tasarım Raporu - Grup 8', author='Tasarım I Grup 8')
    def foot(c, d):
        c.saveState(); c.setFont('DV', 6.5); c.drawRightString(A4[0] - 1.5 * cm, 0.6 * cm, f"Sayfa {d.page}"); c.restoreState()
    doc.build(st, onFirstPage=foot, onLaterPages=foot)
    return fname


# -*- coding: utf-8 -*-
"""Hesap föyü: her akım ve ekipman için adım adım kütle/enerji denkliği (referans çalışma biçiminde)."""
from reportlab.platypus import PageBreak

CN = ['IPA', 'Aseton', 'H<sub>2</sub>', 'Su']

def build_foy(S, D, U, E, C, par, fname='Hesap_foyu_aseton_grup8.pdf'):
    _fonts()
    B = ParagraphStyle('b', fontName='DV', fontSize=8.3, leading=10.6, alignment=TA_JUSTIFY, spaceAfter=2)
    H1 = ParagraphStyle('h1', fontName='DVB', fontSize=11, leading=13, spaceBefore=6, spaceAfter=3, keepWithNext=1, textColor=colors.HexColor('#0b3d6b'))
    H2 = ParagraphStyle('h2', fontName='DVB', fontSize=9.2, leading=11, spaceBefore=5, spaceAfter=1.5, keepWithNext=1, textColor=colors.HexColor('#0b3d6b'))
    EQ = ParagraphStyle('eq', fontName='DV', fontSize=8.2, leading=10.4, leftIndent=14, spaceAfter=1.2)
    Sm = ParagraphStyle('s', fontName='DV', fontSize=7.2, leading=8.8)
    Tc = ParagraphStyle('tc', fontName='DV', fontSize=7.0, leading=8.4)
    Tb = ParagraphStyle('tb', fontName='DVB', fontSize=7.0, leading=8.4, textColor=colors.white)
    P = lambda s, st=B: Paragraph(s, st)
    N = nn
    n = lambda k: S[k]['V'] + S[k]['L']
    m = lambda k: kg(S[k])
    h = lambda k: Hs(S[k]) / 3600.0
    def tbl(data, widths, fs=None):
        rows = [[Paragraph(str(c), Tb if i == 0 else Tc) for c in r] for i, r in enumerate(data)]
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .3, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
                               ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('LEFTPADDING', (0, 0), (-1, -1), 2), ('RIGHTPADDING', (0, 0), (-1, -1), 2)]))
        return t
    sm = lambda ks, f: ' + '.join(f(k) for k in ks)
    st = []
    st.append(P("Hesap Föyü: Kütle ve Enerji Denkliklerinin Adım Adım Hesabı", ParagraphStyle('t', fontName='DVB', fontSize=13, leading=15, spaceAfter=2)))
    st.append(P("Tasarım I (T1-01) · Grup 8 · Asetonun IPA dehidrojenasyonuyla üretimi · 85 000 t/yıl · 8000 h/yıl. Bu föy rapordaki ve PFD'deki sayıların <b>nasıl bulunduğunu</b> gösterir. Akım numaraları A3 PFD ile aynıdır. Birimler SI; sayılar 4 anlamlı rakamdır (denklik satırlarındaki eşitlikler yuvarlama öncesi değerlerle tutar).", Sm))
    # ------------------------------------------------------------ 0
    st.append(P("0. Esaslar, sabitler ve formüller", H1))
    st.append(P("<b>Mol kütleleri (kg/kmol):</b> IPA 60.095; aseton 58.079; H<sub>2</sub> 2.016; su 18.015. <b>Gösterim:</b> n<sub>i</sub> kmol/h; Σn = toplam mol debisi; mol kesri y<sub>i</sub> (buhar) veya x<sub>i</sub> (sıvı) = n<sub>i</sub>/Σn; kütle debisi m = Σ n<sub>i</sub>M<sub>i</sub> (kg/h).", B))
    st.append(P("<b>Reaksiyon:</b> (CH<sub>3</sub>)<sub>2</sub>CHOH → (CH<sub>3</sub>)<sub>2</sub>CO + H<sub>2</sub>. Dönüşüm X = (n<sub>IPA,giriş</sub> − n<sub>IPA,çıkış</sub>)/n<sub>IPA,giriş</sub>; ilerleme r = X·n<sub>IPA,giriş</sub>; seçicilik %100 (yan ürün yok). Bileşen denklemi: n<sub>i,çıkış</sub> = n<sub>i,giriş</sub> + ν<sub>i</sub>·r (ν: IPA −1, aseton +1, H<sub>2</sub> +1, su 0).", B))
    st.append(P("<b>Kütle denkliği:</b> Σ m<sub>giriş</sub> = Σ m<sub>çıkış</sub> (reaktörde de, çünkü kütle korunur); hata % = (Σm<sub>g</sub> − Σm<sub>ç</sub>)/Σm<sub>g</sub>·100. <b>Enerji denkliği:</b> Σ H<sub>giriş</sub> + Q = Σ H<sub>çıkış</sub> (Q &gt; 0: üniteye verilir; pompa için Q yerine W). H = Σ n<sub>i</sub>·h<sub>i</sub>(T): referans 25 °C elementleri; gaz h = Δ<sub>f</sub>H + ∫C<sub>p,g</sub>dT; sıvı h = h<sub>g</sub> − Δ<sub>buh</sub>H + C<sub>p,s</sub>ΔT; ideal karışım. H değerleri kW'tır (kJ/h ÷ 3600). Referans elementler olduğundan H mutlak değeri büyük ve negatiftir; anlamlı olan <b>farklardır</b> (Q).", B))
    st.append(P(f"<b>Utility formülleri:</b> LPS (4 bar(a), {f4(T_LPS)} °C, h<sub>fg</sub> = {f4(H_FG_LPS)} kJ/kg): m = Q·3600/h<sub>fg</sub>. cw (25→35 °C) ve chw (7→12 °C): m = |Q|·3600/(C<sub>p</sub>ΔT), C<sub>p</sub> = {f4(CP_SU)} kJ/kg/K. Yakıt: n<sub>CH4</sub> = (Q<sub>R</sub>/η)·3.6/LHV (LHV = {f4(LHV_CH4)} kJ/mol, η = {par['ETA_FIRIN']}). Tuz: m = Q<sub>R</sub>·3600/(C<sub>p,tuz</sub>·ΔT), C<sub>p,tuz</sub> = {par['CP_SALT']} kJ/kg/K (doğrulanmadı), ΔT = {par['T_SALT_HOT']-par['T_SALT_COLD']:.0f} K.", B))
    st.append(P(f"<b>Çözüm sırası (neden böyle?):</b> (1) Geri dönüş (akım {N(2)}) başlangıçta bilinmez; taze besleme + tahmin ile reaktör girişi, reaktör, flaş, absorber ve kolonlar sırayla hesaplanır, C-102 üst ürünü yeni geri dönüş olur ve bu {E['iters']} iterasyonda yakınsar (|Δ| &lt; 10<sup>-11</sup>). (2) Sonuçlar, ürün debisi 10 625 kg/h olacak şekilde ölçeklenir (ölçek çarpanı {f4(E['scale'])}). Referans çalışmadaki gibi bu hesap da 100 kmol/h taze besleme bazıyla başlar, sonra ölçeklenir (ölçekleme oranları değiştirmez).", B))
    # ------------------------------------------------------------ 1 akımlar
    st.append(P("1. Akım bileşimleri (her proses akımı için)", H1))
    SD = {
     1: ("Taze besleme", "Dışarıdan → V-100", f"Kütlece %88 IPA/%12 su: n<sub>IPA</sub>:n<sub>su</sub> = (0.88/60.095):(0.12/18.015); toplam, ürün 10 625 kg/h olacak şekilde ölçeklenir."),
     2: ("Geri dönüş (C-102 üstü, azeotrop)", "C-102 → V-100", f"IPA = 0.995·n<sub>IPA</sub>(akım {N(18)}); su = n<sub>IPA</sub>(1−x<sub>az</sub>)/x<sub>az</sub>, x<sub>az</sub> = {f4(E['x_az'])} (IPA mol kesri, %87.8 kütle); aseton = akım {N(18)}'deki tümü."),
     3: ("V-100 çıkışı", "V-100 → P-101", f"Akım {N(1)} + {N(2)} (bileşen bileşen toplam); T, H toplamından bulunur."),
     4: ("P-101 çıkışı", "P-101 → E-102", "Bileşim aynı; pompa işi ile hafif ısınır (T, H<sub>3</sub> + W denkliğinden)."),
     5: ("E-102 çıkışı (doygun buhar)", "E-102 → E-101", f"Bileşim aynı; T = çiğ noktası ({f4(E['T5'])} °C, 280 kPa)."),
     6: ("E-101 soğuk çıkışı (kızgın buhar)", "E-101 → R-101", f"Bileşim aynı; T = {par['T_6']:.0f} °C (tasarım seçimi)."),
     7: ("R-101 çıkışı", "R-101 → E-101", f"Reaksiyon: r = X·n<sub>IPA,{N(6)}</sub> = {par['X']}·{f4(n(6)[0])} = {f4(par['X']*n(6)[0])} kmol/h; T = {par['T_R']:.0f} °C."),
     8: ("E-101 sıcak çıkışı", "E-101 → E-103", f"Bileşim akım {N(7)} ile aynı; T, H<sub>{N(8)}</sub> = H<sub>{N(7)}</sub> − Q<sub>E-101</sub> denkleminden."),
     9: ("E-103 çıkışı (kısmi yoğuşmuş)", "E-103 → V-101", "Bileşim aynı; 40 °C, iki faz (flaş dengesi)."),
     10: ("V-101 gazı", "V-101 → T-101", "Flaş: Wilson γ'lı modifiye Raoult K<sub>i</sub> = γ<sub>i</sub>P<sup>sat</sup><sub>i</sub>/P; H<sub>2</sub> yoğuşmaz."),
     11: ("V-101 sıvısı", "V-101 → karışım", f"Akım {N(9)} − akım {N(10)} (bileşen bileşen)."),
     12: ("Yıkama suyu", "Dışarıdan → T-101", f"L = A·K·G = {par['A_ABS']}·{f4(E['K_ace'])}·{f4(n(10).sum())} (ölçek öncesi) → ölçeklenmiş değer."),
     13: ("H<sub>2</sub>-zengin vent", "T-101 → dışarı", f"Aseton: gazın %{(1-par['REC_ACE_ABS'])*100:.1f}'i; IPA: Kremser kalanı; su: 35 °C doygunluk, 170 kPa."),
     14: ("Zengin su", "T-101 → karışım", f"Aseton = {par['REC_ACE_ABS']}·n<sub>aseton,{N(10)}</sub>; IPA = Kremser; su = L + n<sub>su,{N(10)}</sub> − vent suyu."),
     15: ("C-101 beslemesi", "karışım → C-101", f"Akım {N(11)} + {N(14)}; T entalpi toplamından."),
     16: ("C-101 üst ürünü (aseton)", "C-101 → E-108", f"Aseton = {par['REC_ACE_C1']}·n<sub>aseton,{N(15)}</sub>; su, ürün kütlece %{par['W_SU_URUN']*100:.1f} su olacak şekilde; T = bakabarcık noktası ({f4(E['T_D1'])} °C, 110 kPa)."),
     17: ("Ürün (depoya)", "E-108 → depo", "Bileşim akım %d ile aynı; 25 °C'ye soğutulur." % N(16)),
     18: ("C-101 dip ürünü", "C-101 → C-102", f"Akım {N(15)} − akım {N(16)}; T = kabarcık noktası ({f4(E['T_B1'])} °C, 130 kPa)."),
     19: ("Atık su", "C-102 → dışarı", f"Akım {N(18)} − akım {N(2)}; T = kabarcık noktası ({f4(E['T_B2'])} °C)."),
     42: ("T-101 pump-around (çekilen)", "T-101 → P-103", "Debi F<sub>pa</sub> = Q<sub>abs</sub>·3600/Δh (40→30 °C); bileşim = zengin su (akım %d)." % N(14)),
     43: ("P-103 çıkışı", "P-103 → E-109", "Bileşim aynı; pompa işi ile ısınır."),
     44: ("E-109 çıkışı (soğuk)", "E-109 → T-101", "Bileşim aynı; 30 °C."),
     45: ("C-101 üst buharı", "C-101 → E-104", "(R+1)·D: yoğuşturucuya giren buhar, bileşim = ürün (akım %d)." % N(16)),
     46: ("C-101 yoğuşuğu", "E-104 → ayırma", "Doygun sıvı, bileşim ürünle aynı."),
     47: ("C-101 reflüsü", "→ C-101", "R·D (R = 1.3·R<sub>min</sub>)."),
     48: ("C-101 dip sıvısı (rebolyere)", "C-101 → E-105", "Dip ürünü + kaynatma buharına dönüşecek sıvı: V<sub>b</sub>y + B."),
     49: ("C-101 kaynatma buharı", "E-105 → C-101", "V<sub>b</sub> = Q<sub>B</sub>·3600/λ; bileşim = dip sıvısı ile dengedeki buhar y."),
     50: ("C-102 üst buharı", "C-102 → E-106", "(R+1)·D, bileşim = akım %d." % N(2)),
     51: ("C-102 yoğuşuğu", "E-106 → ayırma", "Doygun sıvı."),
     52: ("C-102 reflüsü", "→ C-102", "R·D."),
     53: ("C-102 dip sıvısı (rebolyere)", "C-102 → E-107", "Dip ürünü + kaynatma buharına dönüşecek sıvı."),
     54: ("C-102 kaynatma buharı", "E-107 → C-102", "V<sub>b</sub> = Q<sub>B</sub>·3600/λ."),
    }
    blocks = []
    for k in sorted(S, key=N):
        nk = n(k); tot = nk.sum(); mk_ = nk * MW; ph = S[k]['V'].sum() / tot
        faz = 'buhar' if ph > 0.9999 else ('sıvı' if ph < 1e-4 else 'iki faz')
        yl = 'y' if faz == 'buhar' else ('x' if faz == 'sıvı' else 'z')
        ad, yol, nasil = SD[k]
        rows = [['Bileşen', 'n (kmol/h)', f'{yl} = n/Σn', 'm (kg/h)']]
        for i in range(4):
            rows.append([CN[i], f4(nk[i]), (f"{f4(nk[i])}/{f4(tot)} = {f4(nk[i]/tot)}" if nk[i] > 0 else '0'), f4(mk_[i])])
        rows.append(['<b>Toplam</b>', f4(tot), '1.000', f4(mk_.sum())])
        hd = P(f"<b>Akım {N(k)}</b>: {ad} <i>({yol})</i><br/>T = {f4(S[k]['T'])} °C, P = {f4(par['P'][k]*100)} kPa, faz: {faz}, H = {f4(h(k))} kW<br/><i>{nasil}</i>", Sm)
        blocks.append([hd, tbl(rows, [1.5 * cm, 1.7 * cm, 3.7 * cm, 1.5 * cm])])
    for i in range(0, len(blocks), 2):
        pair = blocks[i:i + 2]
        cells = [[x for x in b] for b in pair]
        while len(cells) < 2: cells.append([''])
        ot = Table([cells], colWidths=[8.9 * cm, 8.9 * cm])
        ot.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
        st.append(KeepTogether(ot))
    # ------------------------------------------------------------ 2 ekipmanlar
    st.append(PageBreak())
    st.append(P("2. Ekipman bazında kütle ve enerji denkliği (akış sırasıyla)", H1))
    def comp_tbl(ins, outs, rxn=None):
        rows = [['Bileşen', 'Giriş Σn (kmol/h)', 'Reaksiyon', 'Çıkış Σn (kmol/h)', 'Fark']]
        ni = sum(n(k) for k in ins); no = sum(n(k) for k in outs)
        for i in range(4):
            r_ = (rxn[i] if rxn is not None else 0.0)
            rows.append([CN[i], f4(ni[i]), (('+' if r_ >= 0 else '') + f4(r_)) if rxn is not None else '-', f4(no[i]), f"{ni[i]+r_-no[i]:.1e}"])
        rows.append(['<b>Toplam mol</b>', f4(ni.sum()), (f4(sum(rxn)) if rxn is not None else '-'), f4(no.sum()), f"{ni.sum()+(sum(rxn) if rxn is not None else 0)-no.sum():.1e}"])
        return tbl(rows, [3.0 * cm, 3.6 * cm, 3.0 * cm, 3.6 * cm, 2.4 * cm])
    def unit(code, title, ins, outs, q=0.0, qlabel='Q', rxn=None, lines=(), rx_text=None):
        blk = [P(f"2.{unit.i}  {code}: {title}", H2)]; unit.i += 1
        blk.append(P(f"<b>Giren akımlar:</b> {', '.join(str(N(k)) for k in ins)}; <b>çıkan akımlar:</b> {', '.join(str(N(k)) for k in outs)}.", B))
        blk.append(P("<b>Reaksiyon:</b> " + (rx_text if rx_text else "yok (fiziksel işlem; bileşen sayısı korunur)."), B))
        for ln in lines: blk.append(P(ln, EQ))
        blk.append(comp_tbl(ins, outs, rxn))
        mi = sum(m(k) for k in ins); mo = sum(m(k) for k in outs)
        blk.append(P(f"<b>Kütle:</b> {sm(ins, lambda k: f4(m(k)))} = {f4(mi)} kg/h (giren) ; çıkan: {sm(outs, lambda k: f4(m(k)))} = {f4(mo)} kg/h ; hata = {100*(mi-mo)/mi:.1e} %.", EQ))
        ei = sum(h(k) for k in ins); eo = sum(h(k) for k in outs)
        blk.append(P(f"<b>Enerji:</b> Σ H<sub>giriş</sub> = {sm(ins, lambda k: f4(h(k)))} = {f4(ei)} kW ; {qlabel} = {f4(q)} kW ; Σ H<sub>çıkış</sub> = {sm(outs, lambda k: f4(h(k)))} = {f4(eo)} kW ; "
                     f"kontrol: {f4(ei)} + ({f4(q)}) − {f4(eo)} = {ei+q-eo:.1e} kW.", EQ))
        st.append(KeepTogether(blk[:3])); st.extend(blk[3:])
    unit.i = 1
    X = par['X']; r_rx = X * n(6)[0]
    unit('V-100', 'Besleme tankı (karıştırıcı)', [1, 2], [3], 0.0,
         lines=[f"n<sub>i,{N(3)}</sub> = n<sub>i,{N(1)}</sub> + n<sub>i,{N(2)}</sub>; örn. IPA: {f4(n(1)[0])} + {f4(n(2)[0])} = {f4(n(3)[0])} kmol/h. T<sub>{N(3)}</sub>: H<sub>{N(1)}</sub> + H<sub>{N(2)}</sub> = H<sub>{N(3)}</sub> denkleminden çözülür → {f4(S[3]['T'])} °C."])
    dP = (par['P'][4] - par['P'][3]) * 100
    unit('P-101A/B', 'Besleme pompası (1 çalışan + 1 yedek)', [3], [4], D['P101'], 'W',
         lines=[f"W = V̇·ΔP/η = (Σ m/ρ)·ΔP/η; ΔP = {f4(dP)} kPa ({f4(par['P'][3]*100)} → {f4(par['P'][4]*100)} kPa), η = {par['ETA_POMPA']} → W = {f4(D['P101'])} kW. Akışkan sıcaklığı bu işle {f4(S[3]['T'])} → {f4(S[4]['T'])} °C."])
    unit('E-102', 'Buharlaştırıcı', [4], [5], D['E102'],
         lines=[f"T<sub>{N(5)}</sub> = çiğ noktası: Σ y<sub>i</sub>/K<sub>i</sub> = 1 → {f4(E['T5'])} °C (280 kPa). Q = H<sub>{N(5)}</sub> − H<sub>{N(4)}</sub> = {f4(h(5))} − {f4(h(4))} = {f4(D['E102'])} kW.",
                f"LPS: ṁ = {f4(D['E102'])}·3600/{f4(H_FG_LPS)} = {f4(U[20][4])} kg/h (akım {N(20)} giriş, {N(21)} yoğuşuk)."])
    unit('E-101', 'Besleme/çıkış ısı değiştirici (proses–proses)', [5, 7], [6, 8], 0.0,
         lines=[f"Soğuk taraf: Q = H<sub>{N(6)}</sub> − H<sub>{N(5)}</sub> = {f4(h(6))} − {f4(h(5))} = {f4(D['E101'])} kW. Sıcak taraf bu ısıyı verir: H<sub>{N(8)}</sub> = H<sub>{N(7)}</sub> − Q → T<sub>{N(8)}</sub> = {f4(S[8]['T'])} °C. Dışarıdan ısı yok: Q<sub>net</sub> = 0."])
    unit('R-101', 'Dehidrojenasyon reaktörü (katalizörlü, çok borulu)', [6], [7], D['R101'], 'Q', rxn=[-r_rx, r_rx, r_rx, 0.0],
         rx_text=f"IPA → aseton + H<sub>2</sub>; X = %{X*100:.0f}, seçicilik %100. r = X·n<sub>IPA,{N(6)}</sub> = {X}·{f4(n(6)[0])} = {f4(r_rx)} kmol/h. IPA: {f4(n(6)[0])} − {f4(r_rx)} = {f4(n(7)[0])}; aseton: {f4(n(6)[1])} + {f4(r_rx)} = {f4(n(7)[1])}; H<sub>2</sub>: 0 + {f4(r_rx)} = {f4(n(7)[2])}; su değişmez ({f4(n(7)[3])}). Yan reaksiyonlar (propilen, eter, aldol) ihmal edilmiştir (Rapor Bölüm 2).",
         lines=[f"Termodinamik kontrol: K<sub>eq</sub>(350 °C) = {f4(C['Keq'])}; denge dönüşümü X<sub>eq</sub> = {f4(C['X_eq'])} &gt; X = {X}. Kütle: M<sub>IPA</sub> = M<sub>aseton</sub> + M<sub>H2</sub> (60.095 = 58.079 + 2.016) olduğundan toplam kütle korunur.",
                f"Isı: Q = H<sub>{N(7)}</sub> − H<sub>{N(6)}</sub> = {f4(h(7))} − {f4(h(6))} = {f4(D['R101'])} kW (endotermik; ΔH<sub>298</sub> = +{f4(C['dH25'])} kJ/mol).",
                f"Isı kaynağı: erimiş tuz (akım {N(39)} {f4(par['T_SALT_HOT'])} → {N(40)} {f4(par['T_SALT_COLD'])} °C): ṁ<sub>tuz</sub> = {f4(D['R101'])}·3600/({par['CP_SALT']}·{par['T_SALT_HOT']-par['T_SALT_COLD']:.0f}) = {f4(E['m_salt'])} kg/h. Tuz F-101 fırınında ısıtılır (Bölüm 2.21)."])
    unit('E-103', 'Reaktör çıkış soğutucusu/yoğuşturucusu', [8], [9], D['E103'],
         lines=[f"Q = H<sub>{N(9)}</sub> − H<sub>{N(8)}</sub> = {f4(h(9))} − {f4(h(8))} = {f4(D['E103'])} kW (soğutma). cw: ṁ = {f4(-D['E103'])}·3600/({f4(CP_SU)}·10) = {f4(U[26][4])} kg/h (akım {N(26)} giriş, {N(27)} çıkış)."])
    gas = n(10); liq = n(11)
    unit('V-101', 'Flaş tankı (40 °C, 180 kPa)', [9], [10, 11], 0.0,
         lines=[f"Buhar kesri = Σn<sub>gaz</sub>/Σn = {f4(gas.sum())}/{f4(n(9).sum())} = {f4(gas.sum()/n(9).sum())}. Gaz: H<sub>2</sub> tümü + K<sub>i</sub> = γ<sub>i</sub>P<sup>sat</sup><sub>i</sub>/P ile ayrılan aseton, IPA, su. Aseton: gaza {f4(gas[1])}, sıvıya {f4(liq[1])} kmol/h (toplam {f4(n(9)[1])}). Adyabatik: Q = 0."])
    unit('T-101 + E-109 + P-103', 'Gaz yıkama (absorpsiyon) kolonu, pump-around ile', [10, 12, 44], [13, 14, 42], 0.0,
         lines=[f"Absorpsiyon faktörü A = L/(K·G): G = {f4(gas.sum())} kmol/h (akım {N(10)}), L = {f4(n(12).sum())} kmol/h (akım {N(12)}), K<sub>aseton</sub> = {f4(E['K_ace'])} (Henry sabitinden, 35 °C, 180 kPa; γ<sub>∞</sub> = {f4(E['gam_inf_ace'])}) → A = {f4(n(12).sum())}/({f4(E['K_ace'])}·{f4(gas.sum())}) = {f4(n(12).sum()/(E['K_ace']*gas.sum()))} ≈ {par['A_ABS']}.",
                f"Kremser: ε = (A<sup>N+1</sup> − A)/(A<sup>N+1</sup> − 1) = {par['REC_ACE_ABS']} → N = {f4(E['N_abs'])} teorik kademe. Aseton: yıkanan = {par['REC_ACE_ABS']}·{f4(gas[1])} = {f4(n(14)[1])}; vent = {f4(n(13)[1])} kmol/h. IPA geri kazanımı (kendi A'sıyla) = %{E['rec_ipa_abs']*100:.5f}.",
                f"Çözünme/yoğuşma ısısı: Q<sub>abs</sub> = (H<sub>{N(10)}</sub> + H<sub>{N(12)}</sub> − H<sub>{N(13)}</sub> − H<sub>{N(14)}</sub>) = {f4(-D['T101'])} kW; pump-around (40→30 °C) ile E-109'da alınır: F<sub>pa</sub> = Q<sub>abs</sub>·3600/Δh = {f4(E['F_pa'])} kmol/h. Bu kontrol hacmi, E-109 yükünü ayrı yazdığı için Q = 0 alınmıştır; pompa/soğutucu Bölüm 2.9–2.10."])
    unit('P-103', 'Pump-around pompası', [42], [43], D['P103'], 'W',
         lines=[f"W = V̇·ΔP/η, ΔP = 50 kPa, η = {par['ETA_POMPA']} → {f4(D['P103'])} kW."])
    unit('E-109', 'Pump-around soğutucusu', [43], [44], D['E109'],
         lines=[f"Q = H<sub>{N(44)}</sub> − H<sub>{N(43)}</sub> = {f4(h(44))} − {f4(h(43))} = {f4(D['E109'])} kW; cw ṁ = {f4(-D['E109'])}·3600/({f4(CP_SU)}·10) = {f4(U[28][4])} kg/h (akım {N(28)}, {N(29)})."])
    unit('Karışım noktası', 'V-101 sıvısı + zengin su → C-101 beslemesi', [11, 14], [15], 0.0,
         lines=[f"n<sub>i,{N(15)}</sub> = n<sub>i,{N(11)}</sub> + n<sub>i,{N(14)}</sub>; aseton: {f4(n(11)[1])} + {f4(n(14)[1])} = {f4(n(15)[1])} kmol/h. T<sub>{N(15)}</sub> = {f4(S[15]['T'])} °C (entalpi toplamından)."])
    D1 = n(16); B1 = n(18)
    unit('C-101 (+E-104, E-105)', 'Aseton kolonu (tüm sistem)', [15], [16, 18], D['E105'] + D['E104'],
         lines=[f"Aseton geri kazanımı {par['REC_ACE_C1']}: n<sub>aseton,{N(16)}</sub> = {par['REC_ACE_C1']}·{f4(n(15)[1])} = {f4(D1[1])}; ürün suyu: m<sub>su</sub>/(m<sub>su</sub>+m<sub>aseton</sub>) = {par['W_SU_URUN']} → n<sub>su</sub> = {f4(D1[3])} kmol/h. Dip = besleme − üst.",
                f"Reflü: McCabe–Thiele (ikili aseton–su, Wilson): z = {f4(E['z1'])}, x<sub>D</sub> = {f4(E['xD1'])}, q = {f4(E['q1'])} → R<sub>min</sub> = {f4(E['Rmin1'])}; R = {par['RR_FACTOR']}·R<sub>min</sub> = {f4(E['R1'])}.",
                f"Yoğuşturucu: Q<sub>C</sub> = (R+1)·λ·D = {f4(-D['E104'])} kW (E-104, cw). Rebolyer: Q<sub>B</sub> = Q<sub>C</sub> + H<sub>{N(16)}</sub> + H<sub>{N(18)}</sub> − H<sub>{N(15)}</sub> = {f4(D['E105'])} kW (E-105, LPS: ṁ = {f4(U[22][4])} kg/h). Rebolyer yükü bu denklemden türetildiğinden enerji kapanışı yapısaldır. Net Q = Q<sub>B</sub> − Q<sub>C</sub> = {f4(D['E105']+D['E104'])} kW."])
    unit('E-104', 'C-101 tam yoğuşturucu', [45], [46], D['E104'],
         lines=[f"Akım {N(45)} = (R+1)·D = ({f4(E['R1'])}+1)·{f4(D1.sum())} = {f4(n(45).sum())} kmol/h; doygun sıvıya yoğuşur (T = {f4(E['T_D1'])} °C). cw: ṁ = {f4(-D['E104'])}·3600/({f4(CP_SU)}·10) = {f4(U[30][4])} kg/h (akım {N(30)}, {N(31)})."])
    unit('Ayırma noktası (C-101)', 'Yoğuşuğun reflü ve ürüne bölünmesi', [46], [47, 16], 0.0,
         lines=[f"Reflü akım {N(47)} = R·D = {f4(E['R1'])}·{f4(D1.sum())} = {f4(n(47).sum())} kmol/h; ürün akım {N(16)} = D = {f4(D1.sum())} kmol/h. Bileşimler aynıdır; T = {f4(E['T_D1'])} °C."])
    unit('E-105', 'C-101 rebolyeri', [48], [49, 18], D['E105'],
         lines=[f"Kaynatma buharı V<sub>b</sub> = Q<sub>B</sub>·3600/λ = {f4(D['E105'])}·3600/λ = {f4(n(49).sum())} kmol/h (akım {N(49)}); dip ürünü akım {N(18)}. LPS ṁ = {f4(U[22][4])} kg/h (akım {N(22)} giriş, {N(23)} yoğuşuk)."])
    unit('E-108', 'Ürün soğutucusu', [16], [17], D['E108'],
         lines=[f"Aseton 56 °C'de kaynar; {f4(S[16]['T'])} → 25 °C'ye soğutulur. Q = H<sub>{N(17)}</sub> − H<sub>{N(16)}</sub> = {f4(h(17))} − {f4(h(16))} = {f4(D['E108'])} kW. cw 25 °C ürünü 25 °C'ye indiremez → chw 7→12 °C: ṁ = {f4(-D['E108'])}·3600/({f4(CP_SU)}·5) = {f4(U[34][4])} kg/h (akım {N(34)}, {N(35)})."])
    D2 = n(2)
    unit('C-102 (+E-106, E-107)', 'IPA kolonu (tüm sistem)', [18], [2, 19], D['E107'] + D['E106'],
         lines=[f"Üst ürün: aseton tümü, IPA = {par['REC_IPA_C2']}·{f4(B1[0])} = {f4(D2[0])}; su azeotrop oranından: n<sub>su</sub> = n<sub>IPA</sub>(1−x<sub>az</sub>)/x<sub>az</sub> = {f4(D2[3])} kmol/h (x<sub>az</sub> = {f4(E['x_az'])}). Dip = besleme − üst.",
                f"Reflü: z = {f4(E['z2'])}, x<sub>D</sub> = {f4(E['xD2'])}, q = {f4(E['q2'])} → R<sub>min</sub> = {f4(E['Rmin2'])}; R = {par['RR_FACTOR']}·R<sub>min</sub> = {f4(E['R2'])}. Q<sub>C</sub> = {f4(-D['E106'])} kW (E-106), Q<sub>B</sub> = {f4(D['E107'])} kW (E-107, LPS ṁ = {f4(U[24][4])} kg/h)."])
    unit('E-106', 'C-102 tam yoğuşturucu', [50], [51], D['E106'],
         lines=[f"Akım {N(50)} = (R+1)·D = {f4(n(50).sum())} kmol/h. cw: ṁ = {f4(-D['E106'])}·3600/({f4(CP_SU)}·10) = {f4(U[32][4])} kg/h (akım {N(32)}, {N(33)})."])
    unit('Ayırma noktası (C-102)', 'Yoğuşuğun reflü ve geri dönüşe bölünmesi', [51], [52, 2], 0.0,
         lines=[f"Reflü akım {N(52)} = R·D = {f4(n(52).sum())} kmol/h; geri dönüş akım {N(2)} = D = {f4(D2.sum())} kmol/h (V-100'e)."])
    unit('E-107', 'C-102 rebolyeri', [53], [54, 19], D['E107'],
         lines=[f"V<sub>b</sub> = {f4(n(54).sum())} kmol/h (akım {N(54)}); atık su akım {N(19)}. LPS ṁ = {f4(U[24][4])} kg/h (akım {N(24)}, {N(25)})."])
    # fırın
    fl = E['flue']
    blk = [P("2.21  F-101: Tuz ısıtıcı fırın (yanma ve tuz çevrimi)", H2),
           P(f"<b>Reaksiyon (yanma):</b> CH<sub>4</sub> + 2 O<sub>2</sub> → CO<sub>2</sub> + 2 H<sub>2</sub>O. Fırın yükü Q<sub>F</sub> = Q<sub>R</sub> = {f4(D['F101'])} kW; yakıt ısısı = Q<sub>F</sub>/η = {f4(D['F101'])}/{par['ETA_FIRIN']} = {f4(E['Q_fuel'])} kW.", B),
           P(f"n<sub>CH4</sub> = {f4(E['Q_fuel'])}·3.6/{f4(LHV_CH4)} = {f4(E['n_fuel'])} kmol/h → ṁ = {f4(E['m_fuel'])} kg/h (akım {N(36)}). O<sub>2</sub> gerekli = 2·n<sub>CH4</sub>·(1+{par['EXCESS_AIR']}) = {f4(fl['O2']+2*fl['CO2'])} kmol/h; hava = O<sub>2</sub>/0.21 → ṁ = {f4(E['m_air'])} kg/h (akım {N(37)}).", EQ),
           P(f"Baca gazı (akım {N(38)}): CO<sub>2</sub> {f4(fl['CO2'])}, H<sub>2</sub>O {f4(fl['H2O'])}, O<sub>2</sub> {f4(fl['O2'])}, N<sub>2</sub> {f4(fl['N2'])} kmol/h → ṁ = {f4(E['m_flue'])} kg/h. <b>Kütle:</b> {f4(E['m_fuel'])} + {f4(E['m_air'])} = {f4(E['m_fuel']+E['m_air'])} ; çıkan {f4(E['m_flue'])} ; fark = {E['m_fuel']+E['m_air']-E['m_flue']:.1e} kg/h.", EQ),
           P(f"Tuz çevrimi: ṁ<sub>tuz</sub> = {f4(E['m_salt'])} kg/h; akım {N(39)} ({par['T_SALT_HOT']:.0f} °C, fırın → reaktör), {N(40)} ({par['T_SALT_COLD']:.0f} °C, reaktör → P-102), {N(41)} (P-102 → fırın). Tuz kapalı devirdir, ürüne karışmaz.", EQ)]
    st.append(KeepTogether(blk))
    # ------------------------------------------------------------ 3 genel
    st.append(P("3. Genel denklikler", H1))
    st.append(P(f"<b>Genel kütle:</b> giren = akım {N(1)} + {N(12)} = {f4(m(1))} + {f4(m(12))} = {f4(C['mass_in'])} kg/h; çıkan = vent {N(13)} + ürün {N(17)} + atık su {N(19)} = {f4(m(13))} + {f4(m(17))} + {f4(m(19))} = {f4(C['mass_out'])} kg/h; hata = {100*(C['mass_in']-C['mass_out'])/C['mass_in']:.1e} % (&lt; %1).", B))
    st.append(P(f"<b>Element (C, H, O) denkliği</b> (C: 3·IPA + 3·aseton; H: 8·IPA + 6·aseton + 2·H<sub>2</sub> + 2·su; O: IPA + aseton + su): giren [{', '.join(f4(v) for v in C['el_in'])}] kmol/h = çıkan [{', '.join(f4(v) for v in C['el_out'])}] kmol/h. Reaksiyon element sayısını değiştirmez; bu yüzden bu kontrol, reaktör ilerlemesinin doğru yazıldığının bağımsız kanıtıdır.", B))
    st.append(P(f"<b>Genel enerji:</b> H<sub>{N(1)}</sub> + H<sub>{N(12)}</sub> + W<sub>P-101</sub> + W<sub>P-103</sub> + Q<sub>E-102</sub> + Q<sub>R-101</sub> + Q<sub>E-105</sub> + Q<sub>E-107</sub> = {f4(C['E_in'])} kW; H<sub>{N(13)}</sub> + H<sub>{N(17)}</sub> + H<sub>{N(19)}</sub> + soğutma yükleri (E-103, E-109, E-104, E-106, E-108) = {f4(C['E_out'])} kW; fark = {C['E_err']:.1e} kW.", B))
    st.append(P(f"<b>Kapasite:</b> 10 625 kg/h × 8000 h/yıl = 85 000 000 kg/yıl = 85 000 t/yıl. <b>Ürün saflığı:</b> su = {f4(S[17]['L'][3]*MW[3])}/{f4(m(17))} = %{C['w_water_prod']*100:.2f} (≤ %0.5); aseton = %{(1-C['w_water_prod'])*100:.2f} (≥ %99.5).", B))
    st.append(P("<b>Sınırlama:</b> Bu föy ticari simülatör sonucu değildir; Python kısa yol modelidir. HYSYS/ChemCAD doğrulaması ayrıca yapılmalıdır. Reaktör dönüşümü sabit, seçicilik %100 kabul edilmiştir; tuz C<sub>p</sub> ve Türkiye kapasite verisi doğrulanmamıştır.", B))
    doc = SimpleDocTemplate(fname, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.3 * cm, bottomMargin=1.3 * cm,
                            title='Hesap Föyü - Aseton Tesisi Grup 8', author='Tasarım I Grup 8')
    def foot(c, d):
        c.saveState(); c.setFont('DV', 6.5); c.drawRightString(A4[0] - 1.5 * cm, 0.7 * cm, f"Hesap föyü – sayfa {d.page}"); c.restoreState()
    doc.build(st, onFirstPage=foot, onLaterPages=foot)
    return fname


# -*- coding: utf-8 -*-
"""Resmi makale biçiminde ön tasarım raporu. Sayfa/tablo kuralları: dergipark yazım kuralları (A4, 2.5 cm, 10-11 pt, tek aralık, iki yana yaslı,
tablo başlığı üstte, numaralı atıf [n]) ve bilimsel tablo kılavuzları (dikey çizgi yok, az yatay çizgi, birimler başlıkta, ondalık hizası)."""
import os, glob, matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FS = ' '   # sayı genişliğinde boşluk (ondalık hizası için)

def _fonts2():
    cand = [] if os.environ.get('FORCE_DEJAVU') else glob.glob('/usr/share/fonts/**/FreeSerif.ttf', recursive=True)
    if cand:
        d = os.path.dirname(cand[0]); fn = ['FreeSerif.ttf', 'FreeSerifBold.ttf', 'FreeSerifItalic.ttf', 'FreeSerifBoldItalic.ttf']
    else:
        d = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf'); fn = ['DejaVuSerif.ttf', 'DejaVuSerif-Bold.ttf', 'DejaVuSerif-Italic.ttf', 'DejaVuSerif-BoldItalic.ttf']
    for nm, f in zip(['SR', 'SRB', 'SRI', 'SRBI'], fn): pdfmetrics.registerFont(TTFont(nm, os.path.join(d, f)))
    pdfmetrics.registerFontFamily('SR', normal='SR', bold='SRB', italic='SRI', boldItalic='SRBI')

REF = {   # anahtar: metin
 'acet': "Wikipedia, Acetone. https://en.wikipedia.org/wiki/Acetone",
 'cum': "Wikipedia, Cumene process. https://en.wikipedia.org/wiki/Cumene_process",
 'az': "ABD Patenti 4,666,560 (izopropanol–su ikili azeotropu: 80.4 °C, ağırlıkça %87.8 izopropanol). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4666560",
 'turton': "Major No. 1 – Design Problems for the Acetone Production Facility (18 Eylül 1998). West Virginia University, R. Turton'un web sayfasında yayımlanmış tasarım problemi (yazar belgede belirtilmemiştir). https://richardturton.faculty.wvu.edu/files/d/843af43f-8ebf-46f9-b436-d875a616823c/acetone1.pdf",
 'pat8': "ABD Patenti 4,380,673 (izopropanol, 2-bütanol ve sikloheksanolün buhar fazında 300–550 °C'de dehidrojenasyonu). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4380673",
 'pat9': "ABD Patenti 4,472,593 (izopropil alkolden aseton; 'brass spelter': 400 °C'de %70 dönüşüm, %99.4 seçicilik; γ-alümina destekte propilen). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4472593",
 'rice11': "Rice University CENG 403 (2011), The Production of Acetone (ZnO/ZrO2 katalizörü, 300–400 °C). http://www.owlnet.rice.edu/~ceng403/gr11298/acetone.html",
 'nist': "EngineeringToolbox: Standard enthalpy of formation, Gibbs energy of formation, entropy and molar heat capacity of organic substances (aseton ve 2-propanol, gaz: ΔH°f = −217.1 ve −272.6 kJ/mol). https://www.engineeringtoolbox.com/standard-enthalpy-formation-value-Gibbs-free-energy-entropy-heat-capacity-organic-d_1979.html",
 'chemeo': "Cheméo, 2-Propanol (ΔfH°gaz, ΔvapH, Cp,sıvı). https://www.chemeo.com/cid/24-809-7/2-Propanol",
 'chemsep': "ChemSep Wilson etkileşim parametreleri (2-propanol/su, aseton/su), thermo deposu (C. Bell). https://github.com/CalebBell/thermo/blob/master/thermo/Interaction%20Parameters/ChemSep/wilson.json",
 'henry': "Sander, R. (2023). Compilation of Henry's law constants (v5). Atmos. Chem. Phys., 23, 10901. https://henrys-law.org/henry/casrn/67-64-1",
 'nptel': "NPTEL, Mass Transfer, Modül 7 (optimum absorpsiyon faktörü 1.2–2). https://archive.nptel.ac.in/content/storage2/courses/103103027/module7/lec6/3.html",
 'eu': "EngineersUniverse, Absorption/Stripping Column Design Guide (A = 1.4–2). https://engineersuniverse.com/studios/chemical-process/absorption-stripping-column-design-guide",
 'steam': "NZIFST, Unit Operations, Appendix 8: Saturated steam tables (400 kPa: 143.6 °C, h_fg = 2134 kJ/kg). https://nzifst.org.nz/resources/unitoperations/appendix8.htm",
 'wits': "World Bank, WITS / UN Comtrade: Türkiye aseton (HS 291411) ithalatı ve ihracatı, 2019–2022 (miktar, kg). https://wits.worldbank.org/trade/comtrade/en/country/TUR/year/2022/tradeflow/Imports/partner/ALL/product/291411 (diğer yıllar için adresteki yıl, ihracat için 'Imports' yerine 'Exports' yazılır)",
}

def build_makale_raw(S, D, U, E, C, par, dchk, ex, sens, vd, bal, fname='Rapor_aseton_grup8.pdf', size=10.0):
    _fonts2()
    cites = []
    def c(*keys):
        out = []
        for k in keys:
            if k not in cites: cites.append(k)
            out.append(str(cites.index(k) + 1))
        return '[' + ', '.join(out) + ']'
    BS = size; LD = size * 1.26
    Bd = ParagraphStyle('b', fontName='SR', fontSize=BS, leading=LD, alignment=TA_JUSTIFY, firstLineIndent=0.7 * cm, spaceAfter=6)
    Bn = ParagraphStyle('bn', parent=Bd, firstLineIndent=0)
    Tt = ParagraphStyle('t', fontName='SRB', fontSize=12, leading=14.5, alignment=TA_CENTER, spaceAfter=4)
    Au = ParagraphStyle('au', fontName='SR', fontSize=9, leading=10.5, alignment=TA_CENTER, spaceAfter=6)
    Ab = ParagraphStyle('ab', fontName='SR', fontSize=9, leading=10.5, alignment=TA_JUSTIFY, spaceAfter=3)
    H1 = ParagraphStyle('h1', fontName='SRB', fontSize=BS, leading=LD, spaceBefore=9, spaceAfter=4, keepWithNext=1)
    H2 = ParagraphStyle('h2', fontName='SRB', fontSize=BS, leading=LD, spaceBefore=5, spaceAfter=2, keepWithNext=1)
    Cp = ParagraphStyle('cp', fontName='SR', fontSize=9, leading=10.4, alignment=TA_CENTER, spaceBefore=3, spaceAfter=2, keepWithNext=1)
    Nt = ParagraphStyle('nt', fontName='SR', fontSize=8, leading=9.2, alignment=TA_JUSTIFY, spaceBefore=1, spaceAfter=4)
    Tx = ParagraphStyle('tx', fontName='SR', fontSize=8, leading=9.2)
    Txr = ParagraphStyle('txr', parent=Tx, alignment=2)
    Txh = ParagraphStyle('txh', fontName='SRB', fontSize=8, leading=9.2, alignment=TA_CENTER)
    Rf = ParagraphStyle('rf', fontName='SR', fontSize=9, leading=10.4, leftIndent=0.7 * cm, firstLineIndent=-0.7 * cm, spaceAfter=1.5, alignment=TA_LEFT)
    P = lambda s, st=Bd: Paragraph(s, st)
    tno = [0]
    def cap(text, note=None):
        tno[0] += 1
        return Paragraph(f"<b>Tablo {tno[0]}.</b> {text}", Cp), tno[0]
    def dec(strs):
        """sütunu ondalık noktasına göre hizala (sayı genişliğinde boşlukla)"""
        fr = [len(s.split('.')[1]) if ('.' in s and 'e' not in s and s.replace('.', '').replace('-', '').replace('+', '').isdigit()) else None for s in strs]
        mx = max([f for f in fr if f is not None] + [0])
        out = []
        for s, f in zip(strs, fr):
            if f is None: out.append(s)
            else: out.append(s + FS * (mx - f) + ('' if f else FS * 0))
        # tam sayıların ondalık noktası yoksa nokta genişliği kadar boşluk
        if mx:
            out = [o + FS if (f == 0 and o.replace(FS, '').replace('-', '').replace('+', '').isdigit()) else o for o, f in zip(out, fr)]
        return out
    def table(head, rows, widths, num=(), left=(0,), width_total=None, notes=None):
        """head: [(ad, birim)], rows: str listeleri. Üç yatay çizgi, dikey çizgi yok, birim ikinci satırda."""
        cols = list(zip(*rows)) if rows else []
        cols = [dec(list(cl)) if i in num else list(cl) for i, cl in enumerate(cols)]
        rows2 = list(zip(*cols)) if cols else []
        hdr = [Paragraph(f"{a}" + (f"<br/>({u})" if u else ''), Txh) for a, u in head]
        body = [[Paragraph(str(x), Txr if i in num else Tx) for i, x in enumerate(r)] for r in rows2]
        t = Table([hdr] + body, colWidths=widths, repeatRows=1, hAlign='CENTER')
        t.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 0.75, colors.black), ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                               ('LINEBELOW', (0, -1), (-1, -1), 0.75, colors.black), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8), ('LEFTPADDING', (0, 0), (-1, -1), 2.5), ('RIGHTPADDING', (0, 0), (-1, -1), 2.5)]))
        return t
    N = nn
    n = lambda k: S[k]['V'] + S[k]['L']
    m = lambda k: kg(S[k])
    Q = D; X = par['X']
    lps = Q['E102'] + Q['E105'] + Q['E107']
    prod = int(round(kg(S[17]))); r_rx = X * n(6)[0]
    st = []
    # -------------------------------------------------------------- başlık, özet
    st.append(P("Asetonun İzopropanolün Katalitik Dehidrojenasyonuyla Üretimi: 85 000 t/yıl Kapasiteli Tesisin Ön Tasarımı", Tt))
    st.append(P("Tasarım I (T1-01) · Grup 8 · 08.10.2026", Au))
    st.append(P(f"<b><i>Özet.</i></b> Kütlece %{par['W_IPA_BESLEME']*100:.0f} izopropanol (IPA) / %{(1-par['W_IPA_BESLEME'])*100:.0f} su karışımından, IPA'nın buhar fazında katalitik dehidrojenasyonuyla yılda 85 000 t (8000 h/yıl; {prod} kg/h) aseton üreten bir tesisin ön tasarımı sunulmuştur. "
                f"Ürün, kütlece en çok %0.5 su içeren, 25 °C'de sıvı asetondur. Tesis; buharlaştırıcı, {par['T_R']:.0f} °C'de çalışan çok borulu katalitik reaktör, flaş tankı, gaz yıkama kolonu ve iki damıtma kolonundan oluşur; "
                f"dönüşmeyen IPA ve su azeotrop bileşiminde geri döndürülür. Hesaplar Python ile kısa yol yöntemiyle yapılmıştır; genel kütle denkliği kapanma hatası {100*(C['mass_in']-C['mass_out'])/C['mass_in']:.1e} % (&lt; %1), "
                f"toplam LPS yükü {f4(lps)} kW'tır. Hesaplar ticari proses simülatörüyle henüz doğrulanmamıştır.", Ab))
    st.append(P("<b><i>Anahtar Kelimeler:</i></b> Aseton, İzopropanol, Dehidrojenasyon, Kütle Denkliği, Enerji Denkliği", Ab))
    # -------------------------------------------------------------- 1
    st.append(P("1. KULLANIM ALANLARI", H1))
    st.append(P(f"Aseton ağırlıklı olarak çözücü olarak (yaklaşık üçte bir), aseton siyanohidrin yoluyla metil metakrilat üretiminde (yaklaşık dörtte bir) ve bisfenol-A üretiminde (yaklaşık %20) kullanılmaktadır; dünya üretimi 2010 yılında yaklaşık 6.7 Mt'dur {c('acet')}.", Bd))
    # -------------------------------------------------------------- 2
    st.append(P("2. ÜRETİM AMACI", H1))
    st.append(P(f"Bu tasarımın amacı, IPA ve su karışımından yılda 85 000 t, kütlece en az %99.5 saflıkta (en çok %0.5 su), 25 °C'de sıvı aseton üretip depoya göndermektir; üretilen aseton Bölüm 1'de sayılan kullanım alanlarında kullanılabilir. "
                f"Besleme bileşimi, IPA–su azeotropuna (80.4 °C, kütlece %87.8 IPA {c('az')}) yakındır; Aseton tesisi tasarım problemi tanımında da besleme ağırlıkça %88 IPA içeren azeotropik karışımdır {c('turton')}. Tasarım esasları Tablo 1'de verilmiştir.", Bd))
    t1c, _ = cap("Tasarım esasları")
    rows = [['Kapasite', '85 000', 't/yıl'], ['Çalışma süresi', '8000', 'h/yıl'], ['Ürün debisi (akım %d)' % N(17), f"{prod}", 'kg/h'],
            ['Ürün saflığı (tasarım)', f"{(1-par['W_SU_URUN'])*100:.1f}", '% kütle aseton'], ['Ürün suyu (sınır: en çok 0.5)', f"{par['W_SU_URUN']*100:.1f}", '% kütle'],
            ['Ürün koşulu', '25', '°C, sıvı'], ['Besleme (akım %d)' % N(1), f"{f4(m(1))}", 'kg/h; %88 IPA, %12 su (kütle)']]
    st.append(KeepTogether([t1c, table([('Parametre', ''), ('Değer', ''), ('Birim', '')], rows, [6.0 * cm, 2.6 * cm, 5.4 * cm], num=(1,))]))
    st.append(Spacer(1, 4))
    # -------------------------------------------------------------- 3
    st.append(P("3. HANGİ TESİS NE AMAÇLA", H1))
    st.append(P("3.1 Üretim Yolları", H2))
    st.append(P(f"Asetonun dünya üretiminin yaklaşık %83'ü kümen (fenol) yoluyla yapılır; aseton burada fenolün yan ürünüdür {c('acet', 'cum')}. "
                f"Bu çalışmadaki tesis ise asetonu ana ürün olarak IPA'dan üretir. Tablo 2 iki yolu, kaynaklarda bulunan veriler ölçüsünde karşılaştırır.", Bd))
    t2c, _ = cap("Kümen (fenol) yolu ile IPA dehidrojenasyonu yolunun karşılaştırılması")
    rows = [['Ana ürün', 'Fenol; aseton yan ürün ' + c('cum'), 'Aseton; H<sub>2</sub> yan ürün'],
            ['Hammadde', 'Benzen, propilen ' + c('cum'), 'IPA + su'],
            ['Aseton oluşumu', 'Hock yeniden düzenlenmesinde fenolle birlikte ' + c('cum'), '1 mol IPA → 1 mol aseton + 1 mol H<sub>2</sub>'],
            ['Koşullar', 'Alkilasyon ≈30 bar, 250 °C; oksidasyon ≈5 atm; Hock yeniden düzenlenmesi asitli ortamda ' + c('cum'), f"Buhar fazı, katalizör; kaynaklarda ≈2 bar, 350 °C " + c('turton') + "; 300–550 °C " + c('pat8')],
            ['Bilinen yan ürünler', 'Asetofenon, α-metilstiren ' + c('cum'), 'Propilen (dehidratasyon) ' + c('pat9') + '; diğerleri için kaynak eklenecek']]
    st.append(KeepTogether([t2c, table([('Kriter', ''), ('Kümen (fenol) tesisi', ''), ('IPA dehidrojenasyon tesisi (bu çalışma)', '')], rows, [3.4 * cm, 5.8 * cm, 5.8 * cm], num=())]))
    st.append(Spacer(1, 4))
    st.append(P("3.2 Tesisteki Birimler ve Amaçları", H2))
    st.append(P(f"Taze besleme (akım {N(1)}) ve geri dönüş (akım {N(2)}) V-100'de karışır; P-101A/B karışımı 320 kPa'a basar. E-102 (LPS) karışımı doygun buhara çevirir (akım {N(5)}, çiğ noktası {f4(E['T5'])} °C); E-101 buharı reaktör çıkışıyla {f4(S[6]['T'])} °C'ye kızdırır (akım {N(6)}). "
                f"R-101'de (çok borulu, katalizörlü) tepkime {f4(par['T_R'])} °C'de yürür (akım {N(7)}). Tepkime endotermik ve LPS'in sıcaklığı ({f4(T_LPS)} °C) {par['T_R']:.0f} °C'nin altında olduğundan, ısı F-101 fırınında yakıt gazıyla ısıtılan ve P-102 ile dolaştırılan erimiş tuzla verilir (akım {N(39)}, {N(40)}, {N(41)}); tuz kapalı devrede kalır ve ürüne karışmaz; Aseton tesisi tasarım problemi tanımında da endotermik tepkimenin ısısı dolaşan erimiş tuzla sağlanır {c('turton')}. "
                f"Reaktör çıkışı E-101'de ve E-103'te 40 °C'ye soğutulur; V-101 gazı (akım {N(10)}) ve sıvıyı (akım {N(11)}) ayırır. T-101'de gazdaki aseton suyla (akım {N(12)}) yıkanır, H<sub>2</sub>-zengin vent (akım {N(13)}) atılır; yıkama sıvısı (akım {N(14)}) V-101 sıvısıyla birleşip C-101 beslemesi (akım {N(15)}) olur. "
                f"C-101 üst ürünü aseton (akım {N(16)}) E-108'de 25 °C'ye soğutulup depoya gider (akım {N(17)}); C-101 dibi (akım {N(18)}) C-102'ye gider. C-102 üstünden azeotrop bileşimli IPA/su geri dönüş olarak V-100'e (akım {N(2)}), dibinden atık su (akım {N(19)}) çıkar. "
                f"Kolon yoğuşturucuları soğutma suyu (cw), rebolyerleri LPS ile çalışır. Birimlerin görevleri ve ısı yükleri Tablo 3'te verilmiştir.", Bd))
    eq = equipment_table(D, ex)
    t3c, _ = cap("Ekipman listesi, işlevleri ve enerji denkliğinden bulunan görevleri (boyutlandırma yapılmamıştır)")
    fixh = lambda t: t.replace('H2', 'H<sub>2</sub>').replace('%99,6', '%99.6')
    rows = [[r.Kod, fixh(f"{r.Ad} ({r.Tip})"), fixh(r.Islev), r.Gorev_kW, r.Utility] for _, r in eq.iterrows()]
    st.append(KeepTogether([t3c, table([('Kod', ''), ('Ad (tip)', ''), ('İşlev', ''), ('Görev', 'kW'), ('Yardımcı akışkan', '')], rows, [1.5 * cm, 4.6 * cm, 5.0 * cm, 1.4 * cm, 2.6 * cm], num=(3,))]))
    st.append(P("Görev: &gt; 0 üniteye verilen ısı veya iş, &lt; 0 çekilen ısı. cw: soğutma suyu (25→35 °C); chw: soğutulmuş su (7→12 °C). Ekipman tipleri tasarım seçimidir.", Nt))
    # -------------------------------------------------------------- 4
    st.append(P("4. TÜRKİYE'DE ÜRETİM KAPASİTESİ", H1))
    ti = {2019: (40377800, 5584400), 2020: (30505700, 3365190), 2021: (41591100, 4650000), 2022: (37659600, 3379590)}
    t4c, _ = cap("Türkiye aseton (HS 291411) dış ticareti (UN Comtrade verileri, WITS)")
    rows = [[str(y), f4(a / 1000), f4(b / 1000), f4((a - b) / 1000)] for y, (a, b) in ti.items()]
    i22, e22 = ti[2022]
    st.append(P(f"Türkiye'nin yurt içi aseton üretim kapasitesi ve üretim miktarı için yapılan taramada güvenilir bir sayısal kaynak bulunamamıştır; bu nedenle herhangi bir kapasite sayısı varsayılmamış, ilgili veri sonradan kaynağıyla eklenecektir. "
                f"Ülkenin aseton arzına ilişkin kaynaklı veri dış ticaret istatistikleridir: Türkiye 2019–2022 yıllarında yılda {f4(ti[2020][0]/1000)}–{f4(ti[2021][0]/1000)} t aseton ithal etmiş, {f4(ti[2020][1]/1000)}–{f4(ti[2019][1]/1000)} t ihraç etmiştir {c('wits')} (Tablo 4). "
                f"Görünür tüketim = üretim + ithalat − ihracat olduğundan, net ithalat görünür tüketimin alt sınırıdır. Bu tasarımın kapasitesi (85 000 t/yıl), 2022 yılı ithalatının {85000/(i22/1000):.2f} katı, net ithalatının {85000/((i22-e22)/1000):.2f} katıdır.", Bd))
    st.append(KeepTogether([t4c, table([('Yıl', ''), ('İthalat', 't/yıl'), ('İhracat', 't/yıl'), ('Net ithalat', 't/yıl')], rows, [2.4 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm], num=(1, 2, 3))]))
    st.append(P("Not: Net ithalat = ithalat − ihracat. Yurt içi kurulu üretim kapasitesi ve üretimi: — (kaynak bulunamadı; eklenecek).", Nt))
    # -------------------------------------------------------------- 5
    st.append(P("5. KÜTLE VE ENERJİ DENKLİĞİ", H1))
    st.append(P("5.1 Kimya ve Tasarım Koşulları", H2))
    st.append(P(f"Tepkime gaz fazında (CH<sub>3</sub>)<sub>2</sub>CHOH → (CH<sub>3</sub>)<sub>2</sub>CO + H<sub>2</sub> olup endotermiktir (ΔH<sub>298</sub> = +{f4(C['dH25'])} kJ/mol, oluşum entalpilerinden hesaplanmıştır {c('nist', 'chemeo')}; reaktör sıcaklığında {f4(C['dH350'])} kJ/mol); Aseton tesisi tasarım problemi tanımında standart reaksiyon ısısı 62.9 kJ/mol verilmiştir {c('turton')}; dayandığı sıcaklık ve referans durum belirtilmemiştir, bu nedenle modelde kaynaklı oluşum entalpileri kullanılmıştır). Reaktör {par['T_R']:.0f} °C'de, girişte 220 kPa'da çalışır; tek geçiş dönüşümü X = %{X*100:.0f}'dır. "
                f"Denge sabiti K<sub>eq</sub>(25 °C) = {C['Keq25']:.1e}, K<sub>eq</sub>({par['T_R']:.0f} °C) = {f4(C['Keq'])}; bu koşulda denge dönüşümü %{C['X_eq']*100:.1f} olup tasarım dönüşümü bunun altındadır. "
                f"Kaynaklarda sekonder alkollerin dehidrojenasyonu endüstriyel olarak buhar fazında 300–550 °C'de yapılabilmektedir {c('pat8')}; Aseton tesisi tasarım problemi tanımında koşullar yaklaşık 2 bar ve 350 °C, tek geçiş dönüşümü %85–92'dir {c('turton')}; ZnO/ZrO<sub>2</sub> katalizör 300–400 °C aralığında kullanılmıştır {c('rice11')}. "
                f"Tasarım bu uygulamalara uygun olarak katalizörlüdür; katalizörsüz hız için sayısal kaynak bulunamamıştır.", Bd))
    st.append(P(f"<b>Seçicilik ve yan tepkimeler.</b> Tasarımda aseton seçiciliği %100 alınmış, yan tepkimeler ihmal edilmiştir. Gerekçe: ticari 'brass spelter' katalizörde 400 °C'de seçicilik %99.4'tür; γ-alümina destekte ise dehidratasyonla propilen oluşur {c('pat9')}. "
                f"Okunan kaynaklarda propilen dışındaki yan ürünler (ör. eter, kondensasyon ürünleri) için tür ve miktar verisi bulunamamış, bu nedenle bunlar için kaynak eklenecektir. "
                f"Etkisi sınırlıdır: seçicilik %99.4 olsaydı {f4(0.006*r_rx)} kmol/h IPA ({f4(0.006*r_rx*MW[0])} kg/h) yan ürüne gider ve ürün miktarı yaklaşık %0.6 azalırdı.", Bd))
    st.append(P("5.2 Varsayımlar", H2))
    t5c, _ = cap("Numaralandırılmış varsayımlar ve gerekçeleri")
    A = [
     ("Kararlı rejim; 8000 h/yıl; ürün 10 625 kg/h.", "Ödev verisi."),
     (f"Besleme kütlece %{par['W_IPA_BESLEME']*100:.0f} IPA, %{(1-par['W_IPA_BESLEME'])*100:.0f} su.", f"Tasarım girdisi; Aseton tesisi tasarım problemi tanımında %88 IPA {c('turton')}; azeotrop %87.8 {c('az')}."),
     ("Aseton seçiciliği %100; yan tepkimeler yok.", "Bölüm 5.1."),
     (f"Tek geçiş dönüşümü sabit, X = %{X*100:.0f}; kinetik ve katalizör kütlesi hesaplanmadı.", f"X &lt; X<sub>eq</sub> = {f4(C['X_eq'])}; kaynak aralığı %85–92 {c('turton')}."),
     ("Gaz ideal; sıvıda Wilson (IPA–su, aseton–su); aseton–IPA ideal.", f"Parametreler {c('chemsep')}; aseton–IPA parametresi bulunamadı."),
     ("Entalpi: 25 °C elementlerden referans, ideal karışım, sabit sıvı C<sub>p</sub>.", f"Kabul; veriler {c('nist', 'chemeo')}."),
     (f"Absorber: A = {par['A_ABS']}; K, Henry sabitinden (35 °C, 180 kPa); aseton geri kazanımı %{par['REC_ACE_ABS']*100:.1f}.", f"A için kaynak aralıkları 1.2–2 {c('nptel')} ve 1.4–2 {c('eu')}; K için {c('henry')}."),
     (f"Kolonlar kısa yol: R = {par['RR_FACTOR']}·R<sub>min</sub>; tam yoğuşturucu; aseton geri kazanımı %{par['REC_ACE_C1']*100:.1f} (C-101), IPA %{par['REC_IPA_C2']*100:.1f} (C-102).", "Kabul (kaynak eklenecek)."),
     ("Basınçlar: besleme 100→320 kPa; reaktör 220 kPa; kolonlar 110 kPa; basınç düşümleri sabit.", "Kabul; boyutlandırma yapılmadı."),
     (f"Pompa verimi %{par['ETA_POMPA']*100:.0f}; fırın verimi %{par['ETA_FIRIN']*100:.0f}; %{par['EXCESS_AIR']*100:.0f} fazla hava; tuz {par['T_SALT_HOT']:.0f}→{par['T_SALT_COLD']:.0f} °C, C<sub>p</sub> = {par['CP_SALT']} kJ/kg/K.", "Kabul (kaynak eklenecek); tuz C<sub>p</sub> doğrulanmadı."),
     (f"LPS 400 kPa(a), {f4(T_LPS)} °C; cw 25→35 °C; chw 7→12 °C (E-108); ΔT<sub>min</sub> = 5 K.", f"LPS verisi {c('steam')} (tabloda h<sub>fg</sub> = 2134, hesapta 2133 kJ/kg); cw ile 25 °C'ye inilemediğinden E-108'de chw."),
     ("Reflü kabı, reflü pompası ve vanalar gösterilmemiştir; ısı kaybı yoktur.", "Ödev PFD'de ana ekipmanı ister."),
    ]
    st.append(KeepTogether([t5c, table([('No', ''), ('Varsayım', ''), ('Gerekçe / kaynak', '')], [[i + 1, a, b] for i, (a, b) in enumerate(A)], [0.8 * cm, 8.4 * cm, 5.8 * cm], num=())]))
    st.append(Spacer(1, 4))
    st.append(P("5.3 Akımlar", H2))
    st.append(P(f"Seçilmiş akımların koşulları ve kütle bileşimleri Tablo 6'da verilmiştir; tüm akımlar A3 PFD'nin altındaki akım tablosundadır ve numaraları PFD ile aynıdır.", Bd))
    t6c, _ = cap("Seçilmiş proses akımları")
    desc = {1: 'Taze besleme', 2: 'Geri dönüş', 5: 'Reaktör girişi (buhar)', 7: 'Reaktör çıkışı', 10: 'Flaş gazı', 12: 'Yıkama suyu', 13: 'H<sub>2</sub>-zengin vent', 15: 'C-101 beslemesi', 17: 'Ürün (depoya)', 19: 'Atık su'}
    rows = []
    for k in sorted(desc, key=N):
        w_ = n(k) * MW; w_ = w_ / w_.sum() * 100
        rows.append([N(k), desc[k], f4(S[k]['T']), f4(par['P'][k] * 100), f4(m(k)), f4(w_[0]), f4(w_[1]), f4(w_[2]), f4(w_[3])])
    st.append(KeepTogether([t6c, table([('Akım', ''), ('Tanım', ''), ('T', '°C'), ('P', 'kPa'), ('Debi', 'kg/h'), ('IPA', '% kütle'), ('Aseton', '% kütle'), ('H<sub>2</sub>', '% kütle'), ('Su', '% kütle')],
                                       rows, [1.0 * cm, 3.7 * cm, 1.4 * cm, 1.5 * cm, 1.8 * cm, 1.5 * cm, 1.7 * cm, 1.5 * cm, 1.4 * cm], num=(2, 3, 4, 5, 6, 7, 8))]))
    st.append(Spacer(1, 4))
    st.append(P("5.4 Kütle Denkliği", H2))
    mi, mo = C['mass_in'], C['mass_out']
    st.append(P(f"Genel denklik: giren (akım {N(1)} + {N(12)}) {f4(mi)} kg/h, çıkan (vent {N(13)} + ürün {N(17)} + atık su {N(19)}) {f4(mo)} kg/h; hata {100*(mi-mo)/mi:.1e} %'dir (&lt; %1). "
                f"Element (C, H, O) denkliği: giren [{', '.join(f4(v) for v in C['el_in'])}] kmol/h, çıkan [{', '.join(f4(v) for v in C['el_out'])}] kmol/h. "
                f"Örnek hesap (R-101): r = X·n<sub>IPA</sub> = {X:.2f}·{f4(n(6)[0])} = {f4(r_rx)} kmol/h; aseton ve H<sub>2</sub> {f4(r_rx)} kmol/h artar, IPA aynı miktarda azalır; kütle girişi {f4(m(6))} kg/h, çıkışı {f4(m(7))} kg/h'tir. "
                f"Ürün suyu {f4(S[17]['L'][3]*MW[3])}/{prod} = %{C['w_water_prod']*100:.2f}'dir. Fırın: yakıt {f4(U[36][4])} + hava {f4(U[37][4])} − baca gazı {f4(U[38][4])} kg/h, fark {U[36][4]+U[37][4]-U[38][4]:.1e} kg/h. "
                f"Ekipman bazında kütle ve enerji kapanışı Tablo 7'dedir; kolon rebolyer yükleri denklikten türetildiğinden o satırlarda enerji kapanışı yapısaldır, bağımsız kontrol element ve genel denkliktir.", Bd))
    t7c, _ = cap("Ekipman bazında kütle ve enerji denkliği (Q &gt; 0: üniteye verilen)")
    rows = [[r.Ekipman, f"{r.Giris} → {r.Cikis}", f4(r.m_in), f4(r.m_out), f"{abs(r.hata_pct):.1e}", f4(r.Q_kW), f"{r.dE:.1e}"] for _, r in bal.iterrows()]
    st.append(KeepTogether([t7c, table([('Ekipman', ''), ('Giren → çıkan akım', ''), ('Giren', 'kg/h'), ('Çıkan', 'kg/h'), ('Kütle hatası', '%'), ('Q', 'kW'), ('ΔE', 'kW')],
                                       rows, [3.2 * cm, 3.0 * cm, 2.0 * cm, 2.0 * cm, 1.8 * cm, 1.6 * cm, 1.4 * cm], num=(2, 3, 5))]))
    st.append(Spacer(1, 4))
    st.append(P("5.5 Absorpsiyon Faktörü ve Yıkama Suyu", H2))
    a = sens['A']; ws = S[12]['L'][3] * MW[3]
    st.append(P(f"Hammaddedeki su reaksiyona girmez; yıkama suyu (akım {N(12)}) bir tasarım seçimidir. V-101 gazındaki aseton, reaksiyonda oluşanın %{S[10]['V'][1]/n(7)[1]*100:.0f}'i kadardır ve yıkanmazsa H<sub>2</sub> ventiyle atılır. "
                f"Absorpsiyon faktörü A = L/(K·G); Tablo 8'e göre A küçüldükçe su ve LPS yükü azalır, teorik kademe sayısı artar. A = {par['A_ABS']}, kaynaklardaki 1.2–2 ve 1.4–2 aralıklarının {c('nptel', 'eu')} alt ucundan seçilmiştir; "
                f"bu durumda K = {f4(E['K_ace'])} (35 °C, 180 kPa), teorik kademe N = {f4(E['N_abs'])}, yıkama suyu {f4(ws)} kg/h (ürünün {f4(ws/prod)} katı)'dır ve atık suya gider. Tablo 8 ekonomik optimizasyon değildir.", Bd))
    t8c, _ = cap(f"Absorpsiyon faktörü duyarlılığı (aseton geri kazanımı %{par['REC_ACE_ABS']*100:.1f})")
    rows = [[f"{r.A:.1f}", f4(r.Yikama_suyu_kmol_h), f4(r.Su_urun_oran), f4(r.N_teorik), f4(r.LPS_toplam_kW)] for _, r in a.iterrows()]
    st.append(KeepTogether([t8c, table([('A', ''), ('Yıkama suyu', 'kmol/h'), ('Su/ürün', 'kg/kg'), ('Teorik kademe N', ''), ('Toplam LPS', 'kW')], rows, [1.6 * cm, 3.0 * cm, 3.0 * cm, 3.2 * cm, 3.0 * cm], num=(0, 1, 2, 3, 4))]))
    st.append(Spacer(1, 4))
    st.append(P("5.6 Enerji Denkliği", H2))
    xw = n(15)[3] / n(15).sum()
    st.append(P(f"Her ekipman için Σ H<sub>giren</sub> + Q = Σ H<sub>çıkan</sub> yazılmıştır (Tablo 3 ve 7); tüm tesiste enerji kapanış farkı {C['E_err']:.1e} kW'tır. "
                f"Örnek (E-102): Q = H<sub>{N(5)}</sub> − H<sub>{N(4)}</sub> = {f4(Q['E102'])} kW; LPS tüketimi {f4(U[20][4])} kg/h (h<sub>fg</sub> = {f4(H_FG_LPS)} kJ/kg). "
                f"Toplam LPS yükü {f4(lps)} kW'tır (E-102 %{Q['E102']/lps*100:.0f}, E-105 %{Q['E105']/lps*100:.0f}, E-107 %{Q['E107']/lps*100:.0f}); en büyük pay C-101 rebolyerindedir ve C-101 beslemesi mol bazında %{xw*100:.0f} sudur. "
                f"R-101 yükü {f4(Q['R101'])} kW'tır; η = %{par['ETA_FIRIN']*100:.0f} ile yakıt {f4(E['Q_fuel'])} kW ({f4(U[36][4])} kg/h CH<sub>4</sub>) gerekir. "
                f"Soğutma yükleri: E-103 {f4(-Q['E103'])}, E-104 {f4(-Q['E104'])}, E-106 {f4(-Q['E106'])}, E-109 {f4(-Q['E109'])} kW (cw); E-108 {f4(-Q['E108'])} kW (chw). "
                f"Isı entegrasyonu yalnızca E-101'dedir; akım {N(19)} (107 °C, {f4(kg(S[19]))} kg/h) ile yaklaşık {kg(S[19])*CP_SU*(107-45)/3600/1000:.1f} MW geri kazanım olasılığı denenmemiştir.", Bd))
    st.append(P("5.7 Doğrulama Durumu ve Sınırlamalar", H2))
    st.append(P(f"Hesaplar ticari proses simülatörüyle (HYSYS, ChemCAD) <b>doğrulanmamıştır</b>; doğrulama için simülatörde Wilson/NRTL ile dönüşüm reaktörü, flaş, absorber ve iki kolon kurulup R-101, E-102, E-105, E-107 yükleri ve akım {N(17)} bileşimi bu rapordaki değerlerle karşılaştırılacaktır. "
                f"Kod içi testlerde veri ve model testlerinin {int((vd['Sonuc']=='GEÇTİ').sum())}/{len(vd)-1} adedi, tasarım kontrollerinin {int((dchk['Sonuc']=='GEÇTİ').sum())}/{len(dchk)} adedi geçmiştir. "
                f"Sınırlamalar: aseton–IPA dengesi ideal alınmıştır; aseton–su dengesi seyreltik uçta Henry verisiyle düzeltilmiş, deneysel y–x verisiyle tam aralıkta karşılaştırılmamıştır; reaktör sabit dönüşümlüdür ve {par['T_6']:.0f}→{par['T_R']:.0f} °C ısınma bölgesi incelenmemiştir; tuz C<sub>p</sub> değeri doğrulanmamıştır; hesaplanan reaksiyon ısısı (+{f4(C['dH25'])} kJ/mol) Aseton tesisi tasarım problemi tanımındaki değerden (62.9 kJ/mol) farklıdır ve R-101 ile F-101 yükünü etkiler, bu fark simülatörle kontrol edilecektir; ekonomik ve emniyet analizi kapsam dışıdır.", Bd))
    # -------------------------------------------------------------- kaynakça
    st.append(P("KAYNAKÇA", H1))
    for i, k in enumerate(cites):
        st.append(Paragraph(f"[{i+1}] {REF[k]}", Rf))
    doc = SimpleDocTemplate(fname, pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2.5 * cm, bottomMargin=2.5 * cm,
                            title='Aseton Tesisi Ön Tasarım Raporu - Grup 8', author='Tasarım I Grup 8')
    def foot(cv, d):
        cv.saveState(); cv.setFont('SR', 9); cv.drawCentredString(A4[0] / 2, 1.4 * cm, str(d.page)); cv.restoreState()
    doc.build(st, onFirstPage=foot, onLaterPages=foot)
    return fname


def build_makale(S, D, U, E, C, par, dchk, ex, sens, vd, bal, fname='Rapor_aseton_grup8.pdf'):
    """10 pt ile üretir; yazı tipi yedeği (DejaVu) daha geniş olduğundan 5 sayfa aşılırsa punto kademeli düşürülür."""
    try:
        from pypdf import PdfReader
    except ImportError:
        try: from PyPDF2 import PdfReader
        except ImportError: PdfReader = None
    for size in (10.0, 9.5, 9.0, 8.5):
        build_makale_raw(S, D, U, E, C, par, dchk, ex, sens, vd, bal, fname, size)
        if PdfReader is None or len(PdfReader(fname).pages) <= 5: break
    print(f'Makale yazı boyutu: {size} pt')
    return fname


if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.max_colwidth', 70)
    S, D, U, E = flowsheet(PAR); C = overall_checks(S, D, U, E, PAR)
    vd = verify_data(); dchk, ex = design_checks(S, D, U, E, PAR, C); sens = sensitivity(PAR)
    assert (dchk['Sonuc'] == 'GEÇTİ').all(), "tasarım kontrolü başarısız"
    assert (vd['Sonuc'] != 'SINIR AŞILDI').all(), "veri testi başarısız"
    make_pfd(S, D, U, E, PAR, 'PFD_aseton_grup8', date_txt='08.10.2026')      # akım numaralarını (MAP) soldan sağa üretir
    bal = unit_balances(S, D, U, E, PAR)
    print("=== VERİ/MODEL DOĞRULAMA ==="); print(vd.round(2).to_string(index=False))
    print("\n=== EKİPMAN BAZLI KÜTLE/ENERJİ DENKLİĞİ ==="); print(bal[['Ekipman', 'Giris', 'Cikis', 'm_in', 'm_out', 'hata_pct', 'Q_kW', 'dE']].to_string(index=False))
    print("\n=== TASARIM KONTROLLERİ ==="); print(dchk.to_string(index=False))
    process_table_df(S, PAR).to_csv('akim_tablosu.csv'); utility_table(U, E).to_csv('yardimci_akimlar.csv', index=False)
    bal.to_csv('ekipman_denklikleri.csv', index=False); vd.to_csv('dogrulama_testleri.csv', index=False)
    build_makale(S, D, U, E, C, PAR, dchk, ex, sens, vd, bal, 'Rapor_aseton_grup8.pdf')
    build_foy(S, D, U, E, C, PAR, 'Hesap_foyu_aseton_grup8.pdf')
    try:
        try: from pypdf import PdfReader, PdfWriter
        except ImportError: from PyPDF2 import PdfReader, PdfWriter
        r = PdfReader('Rapor_aseton_grup8.pdf'); npg = len(r.pages); print(f"\nRapor sayfa sayısı: {npg} (sınır 5)"); assert npg <= 5
        w = PdfWriter()
        for p in r.pages: w.add_page(p)
        for p in PdfReader('PFD_aseton_grup8.pdf').pages: w.add_page(p)
        with open('Aseton_Grup8_TEK_PDF.pdf', 'wb') as fh: w.write(fh)
        print('Toplam sayfa (rapor + PFD):', npg + 1)
    except ImportError:
        print('pypdf/PyPDF2 yok: raporu ve PFD PDF dosyalarını elle birleştirin.')
    files = ['Hesap_foyu_aseton_grup8.pdf', 'Aseton_Grup8_TEK_PDF.pdf', 'PFD_aseton_grup8.png', 'PFD_aseton_grup8.pdf', 'Rapor_aseton_grup8.pdf', 'akim_tablosu.csv', 'yardimci_akimlar.csv', 'ekipman_denklikleri.csv', 'dogrulama_testleri.csv']
    try:
        from google.colab import files as _f
        for f_ in files: _f.download(f_)
    except Exception:
        print('Colab dışında çalışıyor; dosyalar:', [os.path.abspath(f_) for f_ in files])
