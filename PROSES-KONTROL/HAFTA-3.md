# KMB401 Proses Kontrol - Sınav Hazırlık ve Çalışma Portfolyosu[cite: 1]
> **Yazar / Mühendis:** [tugba-kir](https://github.com/tugba-kir)
> **Ders:** KMB401 Proses Kontrol (Ondokuz Mayıs Üniversitesi Kimya Mühendisliği Bölümü)[cite: 1, 3]

---

## ADIM 1: KAPSAMLI HAFTALIK DERS NOTU (Hafta 01-03)

### Hafta 1: Proses Dinamiği için Modelleme Araçları ve Temel Kavramlar[cite: 2]
Proses kontrol, endüstriyel sistemlerde belirlenen değişkenlerin (sıcaklık, basınç, debi vb.) istenen referans değerlerde (Set Point) tutulmasını sağlayan mühendislik disiplinidir[cite: 1, 5]. 

**Kritik Değişken Tanımları:**
*   **Ölçülen Değişken (PV - Process Variable):** Sistemden anlık olarak okunan değer[cite: 5, 6].
*   **Referans Değer (SP - Set Point):** Sistemin ulaşması istenen hedef değer[cite: 5, 6].
*   **Kontrol Edilen Değişken:** Üzerinde doğrudan denetim kurulan parametre (Örn: Çıkış sıcaklığı $T$)[cite: 5, 6].
*   **Ayar Değişkeni (Manipulated Variable):** Kontrolü sağlamak için müdahale edilen parametre (Örn: Su buharı debisi)[cite: 5, 6].
*   **Bozucu Etken (Load/Yük Değişkeni):** Kontrol dışı değişerek sistemi saptıran etken (Örn: Besleme debisi $F$)[cite: 6].
*   **Hata Fonksiyonu ($\epsilon$):** $\epsilon(t) = SP - PV$ formülü ile hesaplanan, sistemin hedefinden sapma miktarıdır[cite: 6].

**Endüstriyel Ölçüm Enstrümantasyonu:**
Kontrol döngüsünün (özellikle kapalı çevrim) en önemli aşaması doğru ölçümdür[cite: 5, 7].
*   **Sıcaklık:** Termometre, direnç termometresi, termokupl, bimetal termometre, radyasyon pirometreleri.
*   **Basınç:** Manometre, diyaframlı elemanlar, piezoelektrik sensörler[cite: 5].
*   **Debi:** Orifismetre, venturimetre, sıcak tel anemometresi, ultrases[cite: 6].
*   **Sıvı Seviyesi:** Şamandıralı aletler, sıvı basıncı ölçen aletler, iletkenlik ölçümü, ses rezonansı[cite: 6].
*   **Konsantrasyon:** Kromatografik analizörler, potansiyometrik analizörler, spektrofotometre, TGA[cite: 6].

**Matematiksel Modelleme Temelleri:**
Kimyasal proseslerin dinamik modelleri şu korunum yasalarına dayanır[cite: 3, 5]:
1.  Kütle Denkliği[cite: 5]
2.  Enerji Denkliği[cite: 5]
3.  Momentum Denkliği[cite: 5]

Bu denklikler **Kararlı Durum (Steady-State)** ve zamana bağlı türevlerin bulunduğu **Kararlı Olmayan Durum (Unsteady-State / Dinamik)** için ayrı ayrı yazılır[cite: 3, 5]. Kararsız durum diferansiyel denklemlerini çözmek için Laplace dönüşümleri uygulanır[cite: 5, 8].

---

### Hafta 2: Proses Dinamiği ve Matematiksel Modelleme Araçları (Laplace Dönüşümleri)[cite: 2]
Laplace dönüşümü, zaman domeni ($t$) diferansiyel denklemlerini, karmaşık $s$ domeninde cebirsel denklemlere indirgeyerek analitik çözümü kolaylaştırır[cite: 8].

**Tanım Bağıntısı:**
$$ F(s) = \mathcal{L}\{f(t)\} = \int_{0}^{\infty} e^{-st} f(t) dt $$[cite: 8, 9]
Laplace dönüşümleri daima doğrusal (lineer) diferansiyel denklemlere uygulanır ve zaman aralığı $0 < t < \infty$ olarak kabul edilir[cite: 9].

**Otomatik Kontrol Sistemleri İçin Temel Giriş Fonksiyonları ve Laplace Dönüşümleri:**
*   **Basamak (Step) Fonksiyonu:** Sisteme anlık ve sabit bir sinyal uygulamasını ifade eder[cite: 9, 10]. 
    *   $f(t) = h \cdot u(t)$ (Birim basamak için $h=1$)[cite: 10]
    *   $\mathcal{L}\{h \cdot u(t)\} = \frac{h}{s}$[cite: 10]
*   **Darbe (Pulse) Fonksiyonu:** Belirli bir $t_0$ anına kadar sabit uygulanıp sonra sıfırlanan sinyaldir[cite: 9, 10].
    *   $f(t) = h \cdot u(t) - h \cdot u(t-t_0)$[cite: 10]
    *   $\mathcal{L}\{f(t)\} = \frac{h}{s}(1 - e^{-t_0 s})$[cite: 10]
*   **Rampa (Ramp) Fonksiyonu:** Sisteme zamanla lineer artan bir etki geldiğinde kullanılır[cite: 9, 11].
    *   $f(t) = A \cdot t$[cite: 11]
    *   $\mathcal{L}\{A \cdot t\} = \frac{A}{s^2}$[cite: 11] (Genel kural: $\mathcal{L}\{t^n\} = \frac{n!}{s^{n+1}}$)[cite: 11]

**Türev ve İntegral Dönüşümleri:**
*   $\mathcal{L}\{f'(t)\} = sF(s) - f(0)$
*   $\mathcal{L}\{f''(t)\} = s^2F(s) - s f(0) - f'(0)$
*   $\mathcal{L}\{\int_0^t f(t)dt\} = \frac{F(s)}{s}$

---

### Hafta 3: Doğrusal Açık Döngü Sistemler ve Karıştırıcılı Tank Modeli[cite: 2]
Proses kontrol senaryolarında, kontrol edicinin etkisinin (geri besleme) olmadığı durumlara *Açık Çevrim (Open Loop)* denir[cite: 5]. Endüstride en sık karşılaşılan açık çevrim kütle/enerji aktarım modellerinden biri **Isıtmalı Karıştırıcılı Tank** sistemidir.

```mermaid
flowchart LR
    A[Besleme: Debi F, Sıcaklık Ti] --> B(Karıştırıcılı Isıtma Tankı, Hacim V, Sıcaklık T)
    B --> C[Çıkış: Debi F, Çıkış Sıcaklığı Tç = T]
    D[Buhar Girişi: Debi mb, Isı Q] --> B
    
    style B fill:#f9f,stroke:#333,stroke-width:2px

### Hafta 1 Ek Notlar: Proses Türleri ve Sapma Değişkenleri (Tahta Notları)[cite: 15]

Hocanın ilk hafta tahtada özellikle vurguladığı üzere, proses kontrol hesaplamalarında sistemlerin termodinamik ve kinetik davranışları belirli çalışma rejimlerine ayrılır.

**1. Proses Türleri Sınıflandırması:**[cite: 15]
*   **Kesikli (Batch) Prosesler:** Sisteme başlangıçta reaktantların yüklendiği ve işlemin sonunda ürünlerin alındığı, zamanla değişimin sürekli olduğu sistemler.
*   **Sürekli (Continuous) Prosesler:** Sisteme kütle ve enerji giriş-çıkışının aralıksız devam ettiği sistemler.
*   **Karma / Yarı Kesikli (Semi-batch) Prosesler:** Sürekli ve kesikli operasyonların bir arada kullanıldığı sistemler.

**2. Kararlı ve Kararlı Olmayan Durum Analizi:**[cite: 15]
*   **Kararlı Hal (Steady-State / Yatışkın / Stabil):** Sistem değişkenlerinin (sıcaklık, seviye vb.) zamana bağlı değişiminin olmadığı durumdur. Matematiksel olarak giren ve çıkan kütle/enerji birbirine eşittir (Üretim veya tüketim yoksa Giren = Çıkan)[cite: 15].
*   **Kararlı Olmayan Hal (Unsteady-State / Dinamik / Yatışkın Olmayan):** Değişkenlerin zamanın bir fonksiyonu olarak değiştiği durumdur[cite: 15]. Dinamik modellerin çözümü bu hal üzerinden yapılır.

**3. Sapma Değişkeni (Deviation Variable) ve Hata Kavramı:**[cite: 15]
Proses kontrolünde sistemin hedeften ne kadar uzaklaştığını belirlemek için "Kararlı Olmayan Hal - Kararlı Hal" farkı alınır. Elde edilen bu fark, **Sapma Değişkeni (Hata)** cinsinden ifade edilir. Transfer fonksiyonları elde edilirken diferansiyel denklemler bu sapma değişkenleri cinsinden yazılır ve ardından $s$-domenine geçiş için Laplace Dönüşümleri, zaman domenine geri dönmek için ise Ters Laplace Dönüşümleri uygulanır[cite: 15]. Tipik proses uygulamaları ısıtma, sıvı seviyesi ve sıcaklık ölçümü üzerinedir[cite: 15].

---

## ADIM 2: KRİTİK HESAPLAMA VE SINAV SENARYOLARI (Kalan Kısım)

### Senaryo 1: Diferansiyel Denklem Çözümü ve Kısmi Kesirlere Ayırma Yöntemi (Hesaplama)

*(...Çözüm Adım 2'den devam)*
2.  **Başlangıç koşullarını yerine koy ve denklemi düzenle:**
    $$s^2X(s) + 6sX(s) + 8X(s) = \frac{2}{s}$$
[cite: 12]
    $$X(s)(s^2 + 6s + 8) = \frac{2}{s} \implies X(s) = \frac{2}{s(s^2+6s+8)} = \frac{2}{s(s+4)(s+2)}$$
[cite: 12]

3.  **Kısmi Kesirlere Ayırma (Partial Fractions):**
    $$\frac{2}{s(s+4)(s+2)} = \frac{A}{s} + \frac{B}{s+4} + \frac{C}{s+2}$$
[cite: 12]
    Payları eşitlersek: $A(s^2+6s+8) + B(s^2+2s) + C(s^2+4s) = 2$[cite: 12]
    *   $s = 0 \text{ için } \implies 8A = 2 \implies A = 1/4$[cite: 13]
    *   $s = -4 \text{ için } \implies 8B = 2 \implies B = 1/4$[cite: 13]
    *   $s = -2 \text{ için } \implies -4C = 2 \implies C = -1/2$[cite: 13]
    Bulunan katsayıları yerine koyduğumuzda:
    $$X(s) = \frac{1/4}{s} + \frac{1/4}{s+4} - \frac{1/2}{s+2}$$
[cite: 13]

4.  **Ters Laplace (Inverse Laplace) Dönüşümü ile zaman domenine geçiş:**
    Standart tablo kuralı: $\mathcal{L}^{-1}\left\{\frac{1}{s+a}\right\} = e^{-at}$[cite: 13]
    $$x(t) = \frac{1}{4} + \frac{1}{4}e^{-4t} - \frac{1}{2}e^{-2t}$$
[cite: 13]

### Senaryo 2: Termodinamik Enerji Denkliği Kurulumu (Kavramsal / Tasarım)

**Soru:** Isıtmalı, tam karıştırmalı sürekli bir tank (CSTR idealizasyonu) için; giriş debisi ($F$), giriş sıcaklığı ($T_i$), tank hacmi ($V$), sıvı yoğunluğu ($\rho$) ve özgül ısı kapasitesi ($C_p$) sabit kabul edilerek genel dinamik (unsteady-state) enerji denklemini kurunuz. Buhardan sisteme aktarılan birim zamandaki ısı akısını $Q$ alınız.[cite: 6, 7]

**Mühendislik Çözüm Şablonu:**
1.  **Genel Korunum Prensibi:** $Giren Enerji - Çıkan Enerji + Üretilen Enerji = Birikim$[cite: 5]
2.  Sistemde kimyasal reaksiyon yoktur, bu sebeple üretim terimi sıfırdır.
3.  **Giren Enerji Hızı:** $\rho F C_p (T_i - T_{ref}) + Q$
4.  **Çıkan Enerji Hızı:** $\rho F C_p (T - T_{ref})$ (Tank içi homojen karıştığı için reaktör içi sıcaklık ve çıkış sıcaklığı aynıdır ve $T$'ye eşittir)[cite: 7].
5.
