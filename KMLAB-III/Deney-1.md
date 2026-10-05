# KMB405 - Kimya Mühendisliği Lab III: Deney 1
## Üç Bileşenli Sistemlerde Faz Dengesi

**Tarih:** 12 Ekim 2026 | **Grup:** B5 | **Laboratuvar:** MAYMER[cite: 6, 7]

### 1. Teorik Altyapı ve Gibbs Faz Kuralı
Kimyasal reaksiyonun söz konusu olmadığı sistemlerde faz ilişkisi Gibbs Faz Kuralı ile tanımlanır[cite: 14]:
$$F = C - P + 2$$
Burada; $F$ serbestlik derecesini, $C$ bileşen sayısını, $P$ sistemdeki faz sayısını ve $2$ ise sıcaklık ile basınç sabitlerini ifade eder[cite: 14]. 

Üç bileşenli sistemlerin faz diyagramları, çizim zorluklarını aşmak adına genellikle sabit sıcaklık ve basınçta çizilir[cite: 14]. Dış etkilerin sabit tutulduğu bu koşullarda serbestlik derecesinden 2 çıkarılır; dolayısıyla 1, 2 ve 3 fazlı bölgelerde serbestlik derecesi sırasıyla 2, 1 ve 0 değerini alır[cite: 14]. Denge ilişkilerinin yorumlanmasında iki boyutlu uzayda çizilen eşkenar üçgen grafiklerinden (Roozeboom diyagramları) faydalanılır[cite: 14].

### 2. Kompozisyon Analizi (Roozeboom Diyagramı)
Eşkenar üçgen grafiklerinde okuma prensipleri:
* **Köşeler:** Saf bileşenleri (%100) temsil eder[cite: 14, 15].
* **Kenarlar:** Kenar çizgileri üzerindeki her nokta iki bileşenli (ikili) sistemleri gösterir[cite: 14, 15].
* **İç Bölge:** Üçgenin içerisindeki herhangi bir nokta üç bileşenin de bulunduğu ternary (üçlü) karışımları temsil eder[cite: 15].
* Bir noktanın kompozisyonu, o noktadan üçgenin kenarlarına çizilen paralel doğruların kestiği eksen değerleri okunarak belirlenir[cite: 15, 16].

### 3. Kullanılan Kimyasallar ve Kritik Güvenlik (HSE) Önlemleri
Deneyde asetik asit, kloroform ve su sisteminin faz dengesi incelenecektir[cite: 16].
* **Kloroform ($CHCl_3$):** Toksik ve kanserojen etkilere sahip bir solventtir; buharlarına maruziyeti engellemek için kesinlikle çeker ocak altında çalışılmalıdır[cite: 16].
* **Asetik Asit ($CH_3COOH$):** Cilt, göz ve solunum yollarında hasara yol açabilen aşındırıcı ve yanıcı güçlü bir organik asittir[cite: 16].
* **Kişisel Koruyucu Donanım (KKD):** Laboratuvara eldiven, önlük ve koruyucu gözlük olmadan girilmesi yasaktır[cite: 5, 13, 16]. Temas halinde bölge derhal bol su ile yıkanmalıdır[cite: 16].

### 4. Proses Akım Şeması (Deneysel Prosedür)
```mermaid
flowchart TD
    A[Asetik Asit, Kloroform ve Su] -->|Belirlenen Kompozisyonlarda Toplam 20 mL| B(Ayırma Hunisi)
    B --> C{Kuvvetlice Çalkala}
    C -->|Termodinamik Dengeye Ulaşması İçin Bekle| D[Faz Ayrımı]
    D --> E[Üst Faz: Hacim ve Kütle Ölçümü]
    D --> F[Alt Faz: Hacim ve Kütle Ölçümü]
    E --> G[1 mL Numune Al]
    F --> G
    G --> H[1 M NaOH ve Fenolftalein ile Titrasyon]
    H --> I[Fazlardaki Asetik Asit Miktarının Tayini]
