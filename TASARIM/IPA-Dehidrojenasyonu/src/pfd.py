# -*- coding: utf-8 -*-
import numpy as np, pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle
from .core import *

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

__all__ = [_n for _n in dir() if not _n.startswith('__')]
