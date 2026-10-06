# BÖLÜM 0: SIFIRDAN PROSES KONTROL MANTIĞI VE 4 TEMEL ADIM

Diferansiyel denklemler, integraller ve karmaşık Laplace dönüşümleri ilk bakışta korkutucu görünebilir. Ancak proses kontrol, fiziksel dünyadaki bir mekanizmanın (örneğin bir 3D yazıcının sıcaklık kontrolü veya bir hidrolik valfin sıvı akışı) matematiksel bir dil ile ifade edilmesinden ibarettir. Sınavlarda karşımıza çıkan tüm o uzun denklemler, sistemin "dengesini" sağlamak için birbirini izleyen **4 sabit mantık adımına** dayanır.

---

## Proses Kontrol Aslında Nedir? (Büyük Resim)

Sistemi kontrol etmek demek, bir "Hedef" belirleyip, "Mevcut Durum" ile aradaki "Hatayı" sıfıra indirmeye çalışmak demektir.

*   **Set Point (İstenen Değer / SP):** Bizim mekanik veya termal hedefimiz (Örn: 60 °C sıcaklık).
*   **Process Variable (Ölçülen Değer / PV):** Sistemin o anki gerçek durumu (Örn: 50 °C).
*   **Hata (Error):** İstenen - Ölçülen. (Örn: Sistem 10 derece geride). 

```mermaid
graph LR
    A(Set Point<br>Hedef) --> C{Hata <br> SP - PV}
    C -->|Hesaplanan Hata| D[Kontrolcü<br>Beyin]
    D -->|Müdahale Sinyali| E(Ayar Vanası<br>Mekanik Eylem)
    E --> F[Proses<br>Tank/Isıtıcı]
    F -->|Anlık Durum| B(Sensör<br>Ölçüm)
    B -. Geri Besleme .-> C
    
    style C fill:#f9d0c4,stroke:#d9534f,stroke-width:2px
    style D fill:#d9edf7,stroke:#31708f,stroke-width:2px
    style E fill:#fcf8e3,stroke:#8a6d3b,stroke-width:2px
```

---

## Adım Adım Sınav Reçetesi (Mantıksal İnşa)

### Adım 1: Korunum Prensibini Yaz (Fiziksel Mantık)
Her şey şu basit fizik kuralına dayanır: **Giren - Çıkan = Birikim**

> **Örnek Soru:** Sabit hacimli bir su tankına dakikada 10 litre su giriyor ve altındaki vanadan 10 litre su çıkıyor. Giriş vanasını açıp dakikada 12 litre su sokmaya başlarsak ne olur?
> 
> **Mantık:** 
> *   İlk Durum: $10 - 10 = 0$ (Birikim yok, sistem Kararlı Halde).
> *   İkinci Durum: $12 - 10 = 2$ (Dakikada 2 litre su içeride birikmeye ve seviye yükselmeye başlar).

Matematiksel olarak "Birikim", seviyenin zamanla değişmesidir ( $\frac{dh}{dt}$ ). Tankın kesit alanı $A$ ise, denklemimiz:
$$ A \frac{dh}{dt} = q_{giren} - q_{cikan} $$

### Adım 2: Sapma Değişkeni (Deviation) Oluştur
Mühendislikte tonlarca suyun mutlak hacmiyle uğraşmak yerine, sadece **"Sistem dengeden ne kadar şaştı?"** (Sapma) sorusuyla ilgileniriz. 

> **Mantık:**
> Giriş debisindeki şaşma (sapma) miktarı: $q_{giren}' = 12 - 10 = 2$ litre/dakika.
> Değişkenlerin üzerine kesme işareti ($'$) koyarak, sadece o artan "2 litrelik fazlalık" üzerinden yepyeni ve hafif bir denklem yazarız:
$$ A \frac{dh'}{dt} = q_{giren}' - q_{cikan}' $$

### Adım 3: Laplace Dönüşümü (Türevden Kurtulmak)
Çıkış debisini vana direncine ($R$) bağlı olarak yazarsak denklemimiz şu hali alır: $A \frac{dh'}{dt} = q_{giren}' - \frac{h'}{R}$. Bu denklemdeki o korkunç türevden ($\frac{dh'}{dt}$) kurtulmak için devreye Laplace girer.

> **Laplace Kuralı:** Zaman ($t$) dünyasındaki türevi alır, sanal ($s$) dünyasına basit bir çarpım ($s$) olarak atar. 
> Türev ($\frac{d}{dt}$) gördüğün yere $s$ yaz:
$$ A \cdot s \cdot H'(s) = Q_{giren}'(s) - \frac{H'(s)}{R} $$

Artık elimizde sadece harflerin çarpılıp bölündüğü, lise matematiğiyle çözülebilen cebirsel bir denklem var. $H'(s)$ yalnız bırakıldığında sınavların vazgeçilmezi olan **Transfer Fonksiyonu** elde edilir:
$$ \frac{H'(s)}{Q_{giren}'(s)} = \frac{1}{As + 1/R} $$

### Adım 4: Kısmi Kesirlere Ayırma ve Fiziksel Dünyaya Dönüş (Ters Laplace)
Diyelim ki işlemleri yaptık ve Laplace dünyasında şu sonuca ulaştık: $H'(s) = \frac{2}{s(s+1)}$
Bu birleşik kesri, Ters Laplace tablolarında bulabilmek için küçük parçalara (Kısmi Kesirlere) ayırmalıyız.

> **Pratik Kapatma Yöntemi:**
> $$ \frac{2}{s(s+1)} = \frac{A}{s} + \frac{B}{s+1} $$
> *   **A'yı bulmak için:** $s$'yi sıfır yapan değer $0$'dır. Ana kesirde $s$'yi kapatıp geri kalanda $0$ yaz: $\frac{2}{0+1} = 2 \implies A = 2$.
> *   **B'yi bulmak için:** $(s+1)$'i sıfır yapan değer $-1$'dir. Ana kesirde $(s+1)$'i kapatıp geri kalanda $-1$ yaz: $\frac{2}{-1} = -2 \implies B = -2$.

Parçalanmış halimiz:
$$ H'(s) = \frac{2}{s} - \frac{2}{s+1} $$

**Tablo Kuralları:**
1. $\frac{Sayi}{s}$ daima sabit bir sayıya dönüşür. $\implies 2$
2. $\frac{Sayi}{s+a}$ daima $e^{-at}$ fonksiyonuna dönüşür. $\implies 2e^{-1t}$

**Zaman Domeni (Nihai Sonuç):**
$$ h'(t) = 2 - 2e^{-t} $$

*Fiziksel Yorum: Kronometreye bastığında ($t=0$) hata sıfırdır. Saatler geçtiğinde ($t \to \infty$ iken $e^{-\infty} = 0$) hata $2 - 0 = 2$ birimde sabitlenir. Yani vanayı açtığımızda tankın seviyesi zamanla logaritmik olarak 2 metre yükselecek ve o noktada yeni bir dengeye oturacaktır.*
