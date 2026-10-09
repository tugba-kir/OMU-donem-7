# -*- coding: utf-8 -*-
"""Hesap föyü: her akım ve ekipman için adım adım kütle/enerji denkliği (referans çalışma biçiminde)."""
from .pdfutil import *
from .pdfutil import _fonts
from reportlab.lib.pagesizes import A4
from reportlab.platypus import PageBreak, KeepTogether

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

__all__ = [_n for _n in dir() if not _n.startswith('__')]
