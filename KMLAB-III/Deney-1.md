# KMB405 - Kimya Mühendisliği Lab III: Deney 1
## Üç Bileşenli Sistemlerde Faz Dengesi (Asetik Asit - Kloroform - Su)

**Tarih:** 12 Ekim 2026 | **Saat:** 10:15 | **Grup:** B5[cite: 7, 12] 
**Laboratuvar:** MAYMER Laboratuvarı | **Sorumlu:** Arş. Gör. Esma Yeliz KAYA[cite: 6, 11]

---

### 1. Teorik Altyapı ve Fiziksel Konsept
Termodinamik olarak birbiriyle karışmayan veya kısmen karışan iki çözücü (bu sistemde su ve kloroform) bir araya getirildiğinde kimyasal yapıları gereği iki ayrı sıvı faz oluştururlar[cite: 14, 16]. Bu ikili karışıma, her iki çözücüde de çözünebilme afinitesine sahip üçüncü bir bileşen (asetik asit) eklendiğinde, bu bileşen sistemin kimyasal potansiyeli her iki fazda eşitlenene dek su ve kloroform fazları arasında dağılır[cite: 14, 16]. 

### 2. Termodinamik Serbestlik ve Gibbs Faz Kuralı
Kimyasal reaksiyonun söz konusu olmadığı sistemlerde faz ilişkisi Gibbs Faz Kuralı ile ifade edilir[cite: 14]:
$$F = C - P + 2$$
Burada $F$ serbestlik derecesini, $C$ bileşen sayısını, $P$ sistemde bulunan faz sayısını, $2$ ise sıcaklık ve basınç sabitini göstermektedir[cite: 14].

**Sisteme Özel İndirgeme:**
Üç bileşenli faz diyagramları genellikle sabit basınç ve sıcaklıkta (izotermal ve izobarik) çalışılır[cite: 14]. Dış etkilerin sabit tutulduğu bu sistemlerde formül $F = C - P$ şekline indirgenir[cite: 14].
*   Bileşen sayısı ($C$) = 3 (Su, Kloroform, Asetik asit)[cite: 16]. 
*   Faz sayısı ($P$) = 2 (Organik alt faz ve sulu üst faz).
*   **F = 3 - 2 = 1**
Serbestlik derecesinin 1 olması, bu termodinamik denge durumunu tam tanımlayabilmek için yalnızca tek bir bağımsız değişkene (örneğin fazlardan birindeki asetik asit derişimine) ihtiyaç duyulduğunu kanıtlar.

### 3. Kompozisyon Analizi ve Roozeboom Diyagramları
Sabit basınç ve sıcaklıkta üç bileşenli sistemlerin faz diyagramlarını iki boyutlu uzayda çizmek için eşkenar üçgen (Roozeboom diyagramları) kullanılır[cite: 14].
*   **Köşeler:** Saf (%100) bileşenleri temsil eder[cite: 14, 15].
*   **Kenarlar:** İki bileşenli (ikili) sistemleri temsil eder[cite: 14, 15].
*   **İç Bölge:** Üç bileşenli (ternary) karışımları temsil eder[cite: 15]. Bir noktanın kompozisyonu, o noktadan üçgen kenarlarına çizilen paralel doğruların eksenleri kestiği değerler okunarak belirlenir[cite: 15, 16].

### 4. Proses Akım Şeması (PFD - Endüstriyel Standart)
Asetik asit-kloroform-su karışımları toplam 20 ml olarak hazırlanıp ayırma hunisinde faz dengesine ulaşması sağlanır[cite: 16]. Ardından 1 M NaOH ve fenolftalein kullanılarak titrasyon gerçekleştirilir[cite: 16].

```mermaid
graph TD
    classDef stream fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff;
    classDef unit fill:#ecf0f1,stroke:#bdc3c7,stroke-width:2px;
    classDef analysis fill:#f39c12,stroke:#e67e22,stroke-width:2px,color:#fff;

    S1([Akım 1: Su]):::stream --> MIX-101[MIX-101 \n Karıştırma Ünitesi]:::unit
    S2([Akım 2: Kloroform]):::stream --> MIX-101
    S3([Akım 3: Asetik Asit]):::stream --> MIX-101
    
    MIX-101 -- S4 (Toplam 20 mL) --> SEP-101{SEP-101 \n Ayırma Hunisi \n (Sıvı-Sıvı Ekstraksiyon)}:::unit
    
    SEP-101 -- S5: Sulu Faz (Üst) --> T-101[(Hacim ve Kütle \n Ölçüm Tankı)]:::unit
    SEP-101 -- S6: Organik Faz (Alt) --> T-102[(Hacim ve Kütle \n Ölçüm Tankı)]:::unit
    
    T-101 -- S7: 1 mL Numune --> TIT-101[TIT-101 \n 1 M NaOH ile Titrasyon \n (Dönüm: Pembe)]:::analysis
    T-102 -- S8: 1 mL Numune --> TIT-102[TIT-102 \n 1 M NaOH ile Titrasyon \n (Dönüm: Pembe)]:::analysis
```

### 5. Deneysel Veriler ve Hesaplamalar Tablosu
Laboratuvar ortamında elde edilecek değerler aşağıdaki tablolara işlenmelidir[cite: 16, 17].

*   $T=..........................^{\circ}C$[cite: 16]
*   $P=..................atm$[cite: 16]

**Tablo 1: Denge doğruları üzerinde seçilen noktalardaki kompozisyonların oluşturulması**[cite: 17]

| Bileşen | Asetik Asit | Kloroform | Su |
| :--- | :--- | :--- | :--- |
| **Yoğunluk** | | | |
| **Numune** | **Kütle (%) / Hacim (ml)** | **Kütle (%) / Hacim (ml)** | **Kütle (%) / Hacim (ml)** |
| **M1** | | | |
| **M2** | | | |
| **M3** | | | |

*Not: Titrasyonda kullanılan asetik asit-su-kloroform karışımı 1 ml; Titrasyon için kullanılan baz ve konsantrasyonu NaOH, 1 M'dır*[cite: 17].

**Tablo 2: Denge doğrusu üzerinde seçilen noktalardaki alt ve üst bileşimlerin belirlenmesi**[cite: 17]

| Nokta Adı | Üst Faz Hacim (ml) | Üst Faz Kütle (g) | Harcanan Baz (ml) | Alt Faz Hacim (ml) | Alt Faz Kütle (g) | Harcanan Baz (ml) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1** | | | | | | |
| **M2** | | | | | | |
| **M3** | | | | | | |

### 6. Kritik İş Sağlığı, Güvenliği ve Çevre (HSE) Standartları
*   **Kloroform ($CHCl_3$):** Toksik ve kanserojen etkileri bilinen bir solventtir[cite: 16]. Buharlarının solunmaması için deney mutlak suretle **çeker ocakta** çalışılmalıdır[cite: 16].
*   **Asetik Asit ($CH_3COOH$):** Cilt, göz ve solunum yollarına zarar verebilen aşındırıcı ve yanıcı bir organik asittir[cite: 16].
*   **Genel KKD:** Deney sırasında eldiven, laboratuvar önlüğü ve koruyucu gözlük kullanılması zorunludur[cite: 5, 10, 16]. Temas halinde bölge bol suyla yıkanmalı ve MSDS formlarındaki riskler dikkate alınmalıdır[cite: 16, 17].

---

