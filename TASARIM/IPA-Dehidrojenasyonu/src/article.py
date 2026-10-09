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
from .core import *

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

__all__ = [_n for _n in dir() if not _n.startswith('__')]
