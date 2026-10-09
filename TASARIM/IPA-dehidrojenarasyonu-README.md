# Aseton Tesisi Ön Tasarımı — İzopropanolün Katalitik Dehidrojenasyonu

*Acetone plant preliminary design: catalytic dehydrogenation of isopropanol (IPA) — shortcut mass/energy balance in Python, A3 process flow diagram (PFD) and a 5-page design report.*

Üniversite dersi **Tasarım I (T1-01), Grup 8** kapsamında hazırlanmış bir ön tasarım çalışmasıdır.

## Özet

| | |
|---|---|
| Reaksiyon | (CH₃)₂CHOH → (CH₃)₂CO + H₂ (gaz fazı, endotermik, katalizörlü) |
| Kapasite | 85 000 t/yıl aseton, 8000 h/yıl → 10 625 kg/h |
| Ürün | ≥ %99.5 aseton (ağırlıkça %0.40 su), 25 °C, 100 kPa, sıvı |
| Besleme | IPA–su, ağırlıkça %88 IPA (azeotropa yakın) |
| Reaktör | 350 °C, girişte 220 kPa, tek geçiş dönüşümü %90 (Xeq = %97.6) |
| Ayırma | Flaş → gaz yıkama kolonu (H₂ vent) → aseton kolonu → IPA kolonu (azeotrop geri dönüşü) |
| Yardımcı akışkanlar | LPS 12 380 kW, soğutma suyu ≈ 10 600 kW, soğutulmuş su 216 kW, yakıt gazı 4002 kW |
| Denklik hatası | Kütle ≈ 1e-12 %, element ≈ 0, enerji ≈ 1e-11 kW (şartname sınırı < %1) |

![PFD](docs/PFD_A3.png)

## Proses akışı

1. **V-100** besleme tankı: taze besleme + geri dönen IPA/su azeotropu.
2. **P-101 → E-102 → E-101**: basınçlandırma, buharlaştırma (LPS), reaktör çıkışıyla ısı geri kazanımı.
3. **R-101 / F-101**: katalizör yatağı; ısı, yakıt gazı fırınında ısıtılan erimiş tuz döngüsünden.
4. **E-103 → V-101**: reaktör çıkışı 40 °C'ye soğutulur, gaz/sıvı ayrılır.
5. **T-101** (+ P-103, E-109): gazdaki aseton suyla yıkanır, H₂ vent edilir.
6. **C-101** (+ E-104, E-105): üstten aseton, → **E-108** ile 25 °C'ye soğutulup depoya.
7. **C-102** (+ E-106, E-107): IPA–su azeotropu V-100'e döner, dipten atık su çıkar.

## Dosyalar

```
src/aseton_plant_design.py   Tek dosya: hesap çekirdeği, PFD, rapor ve hesap föyü üretimi
docs/rapor.pdf               5 sayfalık tasarım raporu (makale formatı, kaynakçalı)
docs/PFD_A3.pdf / .png       Tek sayfa A3 akış şeması (akım tablosu ve yardımcı akışkan tablosu ile)
docs/rapor_ve_pfd_tek_pdf.pdf  Rapor + PFD tek PDF (6 sayfa)
docs/hesap_foyu.pdf          Akım ve ekipman bazında adım adım kütle/enerji denkliği
outputs/*.csv                Akım tablosu, yardımcı akışkanlar, ekipman denklikleri, doğrulama testleri
```

## Çalıştırma

```bash
pip install -r requirements.txt
python src/aseton_plant_design.py
```

Google Colab'de dosyanın içeriğini tek hücreye yapıştırıp çalıştırmak yeterlidir (çıktılar otomatik indirilir). PDF'ler için Times benzeri bir yazı tipi (FreeSerif) bulunursa o kullanılır, yoksa DejaVu Serif'e geçilir ve rapor 5 sayfaya sığacak şekilde yazı boyutu otomatik küçültülür.

## Yöntem

- **VLE:** IPA–su ve aseton–su için Wilson (ChemSep parametreleri); aseton–IPA ideal. Gaz yıkama için Henry sabiti (Sander).
- **Reaksiyon:** ΔH₂₉₈ = +55.50 kJ/mol (oluşum entalpilerinden), 350 °C'de +57.98 kJ/mol; Keq, Gibbs enerjisinden.
- **Absorber:** Absorpsiyon faktörü A = 1.4, Kremser ile N ≈ 12 teorik kademe, pump-around ile ısı çekimi.
- **Kolonlar:** McCabe–Thiele, R = 1.3 × Rmin, tam yoğuşturucu, kettle rebolyer; yükler enerji denkliğinden türetilmiştir.
- **Entalpi:** 25 °C elementlerden referans, ideal karışım, sabit sıvı Cp.
- Ekipman boyutlandırması, kontrol/sensör ve P&ID **kapsam dışıdır**.

## Sınırlamalar (dürüst not)

- **Simülatör doğrulaması yok** (HYSYS/ChemCAD ile karşılaştırılmadı); sonuçlar kısa yol hesabıdır.
- Dönüşüm (%90) ve seçicilik (%100) **tasarım kabulüdür**; kinetik model yoktur. Seçicilik %99.4 olsaydı ürün yaklaşık %0.6 azalırdı (rapor Bölüm 5.1).
- Reaksiyon ısısı kaynaklı oluşum entalpilerinden hesaplandı (+55.50 kJ/mol); bir tasarım problemi metnindeki 62.9 kJ/mol değeriyle fark vardır (sebebi: o değerin referans durumu belirtilmemiştir). Fark reaktör yükünde ≈ %7.
- Erimiş tuz Cp değeri (1.56 kJ/kg/K) kaynaktan doğrulanmadı; yalnızca tuz debisini etkiler.
- Reflü kapları, vanalar ve pompaların çoğu çizimde ve hesapta yoktur. Isı entegrasyonu yalnızca E-101'dedir.
- Rebolyer yükleri enerji denkliğinden türetildiği için "kapanma" onlar için bağımsız bir doğrulama değildir.
- Türkiye yerli aseton üretim kapasitesi için güvenilir kaynak bulunamamıştır; yalnızca dış ticaret verisi (HS 291411) kullanılmıştır.

Kaynaklar raporun sonundaki kaynakçadadır.

## Lisans

Kod MIT lisansı altındadır (`LICENSE`). Rapor ve çizimler için telif/atıf kuralları grubun kararına bağlıdır.
