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
