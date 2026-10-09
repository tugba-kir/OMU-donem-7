# -*- coding: utf-8 -*-
"""Komut satırı: hesap, kontroller, PFD, rapor, hesap föyü ve CSV çıktılarını üretir.

Kullanım:  python -m aseton [--out CIKTI_KLASORU]
"""
import argparse
import os
import warnings

import pandas as pd

from .core import PAR, flowsheet, overall_checks, verify_data, design_checks, sensitivity, unit_balances
from .pfd import make_pfd, process_table_df, utility_table
from .article import build_makale
from .worksheet import build_foy

PFD_DATE = '08.10.2026'


def run_checks(S, D, U, E, par):
    """Doğrulama ve tasarım kontrollerini çalıştırır; başarısızlıkta AssertionError verir."""
    C = overall_checks(S, D, U, E, par)
    vd = verify_data()
    dchk, ex = design_checks(S, D, U, E, par, C)
    assert (dchk['Sonuc'] == 'GEÇTİ').all(), "tasarım kontrolü başarısız"
    assert (vd['Sonuc'] != 'SINIR AŞILDI').all(), "veri testi başarısız"
    return C, vd, dchk, ex


def merge_pdfs(report_pdf, pfd_pdf, out_pdf, max_pages=5):
    """Raporu ve PFD'yi tek PDF'te birleştirir; rapor sayfa sınırını denetler."""
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(report_pdf)
    n = len(r.pages)
    assert n <= max_pages, f"rapor {n} sayfa (sınır {max_pages})"
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    for p in PdfReader(pfd_pdf).pages:
        w.add_page(p)
    with open(out_pdf, 'wb') as fh:
        w.write(fh)
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(prog='aseton', description=__doc__)
    ap.add_argument('--out', default='.', help='çıktı klasörü (varsayılan: çalışma dizini)')
    args = ap.parse_args(argv)
    warnings.filterwarnings('ignore')
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.max_colwidth', 70)
    out = args.out
    os.makedirs(out, exist_ok=True)
    j = lambda f: os.path.join(out, f)

    S, D, U, E = flowsheet(PAR)
    C, vd, dchk, ex = run_checks(S, D, U, E, PAR)
    sens = sensitivity(PAR)
    make_pfd(S, D, U, E, PAR, j('PFD_aseton_grup8'), date_txt=PFD_DATE)   # akım numaralarını (MAP) soldan sağa üretir
    bal = unit_balances(S, D, U, E, PAR)

    print("=== VERİ/MODEL DOĞRULAMA ==="); print(vd.round(2).to_string(index=False))
    print("\n=== EKİPMAN BAZLI KÜTLE/ENERJİ DENKLİĞİ ===")
    print(bal[['Ekipman', 'Giris', 'Cikis', 'm_in', 'm_out', 'hata_pct', 'Q_kW', 'dE']].to_string(index=False))
    print("\n=== TASARIM KONTROLLERİ ==="); print(dchk.to_string(index=False))

    process_table_df(S, PAR).to_csv(j('akim_tablosu.csv'))
    utility_table(U, E).to_csv(j('yardimci_akimlar.csv'), index=False)
    bal.to_csv(j('ekipman_denklikleri.csv'), index=False)
    vd.to_csv(j('dogrulama_testleri.csv'), index=False)

    build_makale(S, D, U, E, C, PAR, dchk, ex, sens, vd, bal, j('Rapor_aseton_grup8.pdf'))
    build_foy(S, D, U, E, C, PAR, j('Hesap_foyu_aseton_grup8.pdf'))
    n = merge_pdfs(j('Rapor_aseton_grup8.pdf'), j('PFD_aseton_grup8.pdf'), j('Aseton_Grup8_TEK_PDF.pdf'))
    print(f"\nRapor sayfa sayısı: {n} (sınır 5); toplam (rapor + PFD): {n + 1}")
    print('Çıktılar:', os.path.abspath(out))
    return 0
