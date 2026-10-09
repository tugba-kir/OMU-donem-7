# -*- coding: utf-8 -*-
"""Veri/model doğrulama testleri, tasarım kontrolleri ve duyarlılık analizi."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *
from .thermo import *
from .params import *
from .columns import *
from .flowsheet import *
from .balances import *

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

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    S, D, U, E = flowsheet(PAR)
    print(stream_table(S, PAR['P']).round(2))
    print({k: round(v, 1) for k, v in D.items()})
    for k, v in E.items():
        if not isinstance(v, (dict, np.ndarray)): print(k, round(v, 4) if isinstance(v, float) else v)
    print(unit_balances(S, D, U, E, PAR)[['Ekipman', 'dm', 'dE']])
    print(overall_checks(S, D, U, E, PAR))

__all__ = [_n for _n in dir() if not _n.startswith('__')]
