## KMB401 Proses Kontrol - Detaylı Çalışma ve Analiz Senaryoları

Bu bölüm, proses kontrol dinamiklerinin matematiksel temellerini ve fiziksel karşılıklarını birleştiren, sınav formatına uygun lisans seviyesi çalışma sorularını içermektedir. Çözümler, ezberden ziyade mühendislik yaklaşımını (modelleme, s-domenine geçiş, analiz) kavramaya yönelik olarak yapılandırılmıştır.

### Soru 1: Birinci Mertebeden Sistemlerin Dinamik Analizi ve Son Değer Teoremi
**Soru:** Kimyasal bir prosesin dinamik davranışı, aşağıdaki birinci mertebeden lineer diferansiyel denklem ile tanımlanmaktadır[cite: 21]:

$$2\frac{dy}{dt}+8y=4$$

Sistemin başlangıç koşulu $y(0)=2$ olarak verilmiştir[cite: 21].
a) Bu sistemi Laplace dönüşümü kullanarak zaman domeninde ($y(t)$) çözünüz[cite: 21].
b) Sistemin ulaşacağı yeni kararlı hal (son) değerini fiziksel anlamıyla açıklayarak bulunuz[cite: 21].

**Sistem Blok Diyagramı (Simulink/Matlab Gösterimi):**
```mermaid
graph LR
    A((Giriş Etkisi)) -->|Uygulanan Sinyal| B[Proses Transfer Fonksiyonu<br>Dinamik Yanıt]
    B -->|Zamana Bağlı Değişim| C((Çıkış:<br>y t))
    
    style B fill:#e6f3ff,stroke:#31708f,stroke-width:2px
```

**Eğitici Mühendislik Çözümü:**

1.  **Diferansiyel Denklemin s-Domenine Aktarılması (Laplace Dönüşümü):**
    Zaman ($t$) domenindeki türevsel değişimleri cebirsel olarak çözebilmek için denklemin her iki tarafının Laplace dönüşümü alınır. Başlangıç koşulunu ($y(0)=2$) doğrudan işleme dahil etmeliyiz.
    $2[sY(s)-y(0)]+8Y(s)=\frac{4}{s}$
    $2[sY(s)-2]+8Y(s)=\frac{4}{s}$

2.  **Cebirsel Düzenleme ve Y(s)'in Yalnız Bırakılması:**
    Sistemin çıkış fonksiyonu $Y(s)$'i bir tarafa toplayarak denklemi çözülebilir kesir formuna getiriyoruz.
    $2sY(s)-4+8Y(s)=\frac{4}{s}$
    $Y(s)(2s+8)=\frac{4}{s}+4=\frac{4s+4}{s}$
    $Y(s)=\frac{4s+4}{s(2s+8)}=\frac{2s+2}{s(s+4)}$

3.  **Kısmi Kesirlere Ayırma (Partial Fractions):**
    Ters Laplace tablosundaki standart formlara ulaşmak için karmaşık kesri basit bileşenlere ayırıyoruz.
    $\frac{2s+2}{s(s+4)}=\frac{A}{s}+\frac{B}{s+4}$
    Payları eşitleyerek: $A(s+4)+Bs=2s+2$
    *   $s=0$ için: $4A=2 \implies A=0.5$
    *   $s=-4$ için: $-4B=-8+2 \implies B=1.5$
    
    Kısmi kesir formu: $Y(s)=\frac{0.5}{s}+\frac{1.5}{s+4}$

4.  **Zaman Domenine Geri Dönüş (Ters Laplace):**
    Bulduğumuz $s$-domeni fonksiyonunu, fiziksel dünyada karşılığı olan zamana bağlı bir fonksiyona ($y(t)$) dönüştürüyoruz.
    $y(t)=0.5+1.5e^{-4t}$
    *(Öğretici Not: Buradaki $e^{-4t}$ terimi, sistemin başlangıçtaki "geçici (transient)" tepkisini gösterir ve zamanla sönümlenir.)*

5.  **Son Değer (Final Value) Analizi:**
    Sistem yeterince uzun süre çalıştırıldığında ($t \to \infty$), geçici rejim biter ve yeni bir kararlı hale (steady-state) ulaşılır[cite: 21].
    $y(\infty)=0.5+1.5e^{-\infty}=0.5+0=0.5$
    *(Sistem 2 birimlik başlangıç durumundan harekete geçmiş, dinamik tepkisini vermiş ve $t=\infty$ anında $0.5$ birimlik yeni dengesine oturmuştur.)*

---

### Soru 2: Sıvı Seviye Kontrol Sistemi ve Basamak (Step) Etki Analizi
**Soru:** Kesit alanı $A=5\text{ m}^2$ olan bir prosese $q_i$ hacimsel debisi ile sıvı beslenmektedir[cite: 21]. Çıkış debisi sıvı seviyesi ($h$) ile vananın direncine ($R$) bağlı olarak $q_o=\frac{h}{R}$ kuralına göre değişmektedir[cite: 21]. Vana direnci $R=2\text{ dk/m}^2$'dir[cite: 21]. Proses başlangıçta $q_{is}=2\text{ m}^3/\text{dk}$ giriş debisi ile kararlı (steady-state) haldedir.
a) Sıvı seviyesinin giriş debisine oranını veren transfer fonksiyonunu ($\frac{H'(s)}{Q_i'(s)}$) çıkarınız[cite: 20, 21].
b) Giriş debisinde aniden meydana gelen $0.5\text{ m}^3/\text{dk}$'lık bir basamak artışı (step change) sonrasında sistemin göstereceği seviye değişim profilini ($h(t)$) bulunuz[cite: 20, 21].

**Proses Akım Şeması (Aspen / ChemCAD PFD Gösterimi):**
```mermaid
flowchart TD
    IN((Besleme Akımı<br>q_i)) -->|Giriş| TANK[Tam Karıştırmalı Tank<br>Kesit Alanı: A = 5 m²<br>Sıvı Seviyesi: h]
    TANK -->|Yerçekimi Akışı| VALVE(Çıkış Vanası<br>Direnç: R = 2 dk/m²)
    VALVE --> OUT((Çıkış Akımı<br>q_o = h/R))
    
    style TANK fill:#d9edf7,stroke:#31708f,stroke-width:2px
    style VALVE fill:#fcf8e3,stroke:#8a6d3b,stroke-width:2px
```

**Eğitici Mühendislik Çözümü:**

1.  **Başlangıç Kararlı Hal (Steady-State) Koşullarının Belirlenmesi:**
    Herhangi bir bozucu etki gelmeden önce, tanka giren sıvı miktarı çıkan sıvı miktarına tam eşittir ve seviye sabittir.
    $q_{is}=q_{os}=\frac{h_s}{R} \implies 2=\frac{h_s}{2} \implies h_s=4\text{ m}$
    *(Tank başlangıçta 4 metre sıvı seviyesinde dengededir.)*

2.  **Fiziksel Kütle Denkliği ve Sapma Değişkenleri (Deviation Variables):**
    Genel korunum yasasına göre: $Giren - \text{\c{C}}\imath kan = Birikim$[cite: 20]
    $A\frac{dh}{dt}=q_i-\frac{h}{R}$
    Kontrol mühendisliğinde analizleri kolaylaştırmak için mutlak değerler yerine "kararlı halden sapma miktarları" kullanılır. Sapma değişkeni: $h'=h-h_s$ ve $q_i'=q_i-q_{is}$.
    Dinamik denklemden kararlı hal denklemi çıkarıldığında sapma modeli elde edilir:
    $A\frac{dh'}{dt}=q_i'-\frac{h'}{R}$

3.  **Transfer Fonksiyonunun Türetilmesi:**
    Sapma modelinin (başlangıç şartı $h'(0)=0$ kabulüyle) Laplace dönüşümü alınır[cite: 20]. Bu kabul, sistemin tam $t=0$ anında dengede olduğunu belirtir.
    $AsH'(s)=Q_i'(s)-\frac{H'(s)}{R}$
    $H'(s)(As+\frac{1}{R})=Q_i'(s) \implies \frac{H'(s)}{Q_i'(s)}=\frac{R}{ARs+1}$
    Sistem parametreleri ($A=5$, $R=2$) yerine konulduğunda transfer fonksiyonu:
    $G_p(s)=\frac{H'(s)}{Q_i'(s)}=\frac{2}{10s+1}$
    *(Öğretici Not: Bu format $\frac{K_p}{\tau s+1}$ şeklindeki standart 1. mertebe transfer fonksiyonudur. Sistemin kazancı $K_p=2$, zaman sabiti $\tau=10$ dakikadır.)*

4.  **Basamak (Step) Etki Sistem Yanıtının Çözümlenmesi:**
    Giriş debisi $2\text{ m}^3/\text{dk}$'dan $2.5\text{ m}^3/\text{dk}$'ya çıktığı için oluşan sapma (hata):
    $\Delta q_i=2.5-2=0.5\text{ m}^3/\text{dk}$[cite: 20, 21]
    Anlık kalıcı bir değişim olduğu için Laplace karşılığı bir basamak fonksiyonudur[cite: 20, 21]: $Q_i'(s)=\frac{0.5}{s}$
    Bunu transfer fonksiyonunda yerine koyduğumuzda:
    $H'(s)=(\frac{2}{10s+1})(\frac{0.5}{s})=\frac{1}{s(10s+1)}=\frac{0.1}{s(s+0.1)}$

5.  **Kısmi Kesirler ve Ters Laplace:**
    $\frac{0.1}{s(s+0.1)}=\frac{C_1}{s}+\frac{C_2}{s+0.1}$
    *   $s=0$ için $C_1=1$
    *   $s=-0.1$ için $C_2=-1$
    
    $H'(s)=\frac{1}{s}-\frac{1}{s+0.1}$
    Ters Laplace ile sapma fonksiyonu bulunur: $h'(t)=1-e^{-0.1t}$

6.  **Mutlak (Gerçek) Seviye Profili:**
    Gerçek tank seviyesi, başlangıçtaki kararlı hal seviyesi ile sapma miktarının toplamıdır.
    $h(t)=h_s+h'(t)=4+(1-e^{-0.1t})=5-e^{-0.1t}$
    *(Fiziksel Yorum: Vana açılıp tanka daha fazla sıvı girmeye başladığında seviye logaritmik olarak artacak ve $t \to \infty$ anında tank taşmadan tam $5\text{ m}$ seviyesinde yeni bir hidrodinamik dengeye oturacaktır.)*
    # KMB401 Proses Kontrol - Vize (Ara Sınav) Hazırlık Soruları

Bu bölüm, dersin eğitmeninin spesifik soru tiplerine (yüksek mertebeli Laplace dönüşümleri, limit teoremleri ve karışım prosesi modelleme) sadık kalınarak hazırlanmış ileri düzey lisans çalışma sorularını içermektedir.

---
# KMB401 Proses Kontrol - Vize (Ara Sınav) Hazırlık Soruları

Bu bölüm, dersin eğitmeninin spesifik soru tiplerine (yüksek mertebeli Laplace dönüşümleri, limit teoremleri ve karışım prosesi modelleme) sadık kalınarak hazırlanmış ileri düzey lisans çalışma sorularını içermektedir.

---

### Soru 1: Üçüncü Mertebeden Sistem Dinamiği ve Laplace Analizi (35 Puan)
**Soru:** Kimyasal bir reaktörün dinamik davranışı, aşağıdaki 3. mertebeden lineer diferansiyel denklem ile ifade edilmektedir[cite: 26]:

$$ \frac{d^3x}{dt^3}-7\frac{dx}{dt}-6x=5 $$

Sistemin başlangıç koşulları $x(0)=0$, $x'(0)=0$ ve $x''(0)=0$ olarak verilmiştir[cite: 26]. 
Sisteme $t=0$ anında uygulanan $5$ birimlik basamak (step) etki altındaki zaman yanıtını ($x(t)$ fonksiyonunu) Laplace dönüşümü ve kısmi kesirlere ayırma yöntemini kullanarak elde ediniz[cite: 26, 27].

**Mühendislik Çözüm Şablonu:**
1.  **Her İki Tarafın Laplace Dönüşümünün Alınması:**
    Türev kuralları uygulanarak sistem $s$-domenine geçirilir[cite: 27].
    $[s^3X(s)-s^2x(0)-sx'(0)-x''(0)]-7[sX(s)-x(0)]-6X(s)=\frac{5}{s}$
2.  **Başlangıç Koşullarının Uygulanması:**
    Tüm başlangıç koşulları sıfır olduğundan denklem sadeleşir[cite: 26].
    $s^3X(s)-7sX(s)-6X(s)=\frac{5}{s}$
    $X(s)[s^3-7s-6]=\frac{5}{s}$
3.  **Karakteristik Denklemin Çarpanlarına Ayrılması:**
    Polinom bölmesi veya deneme yoluyla $s^3-7s-6=0$ denkleminin kökleri bulunur[cite: 26, 27]. $s=-1$ için denklem sıfırlanır, dolayısıyla $(s+1)$ bir çarpandır.
    $s^3-7s-6=(s+1)(s^2-s-6)=(s+1)(s-3)(s+2)$
    Buna göre transfer fonksiyonu:
    $X(s)=\frac{5}{s(s+1)(s+2)(s-3)}$
4.  **Kısmi Kesirlere Ayırma İşlemi:**
    $\frac{5}{s(s+1)(s+2)(s-3)}=\frac{A}{s}+\frac{B}{s+1}+\frac{C}{s+2}+\frac{D}{s-3}$
    Paylar eşitlenerek sabitler bulunur (Hocanın notlarındaki kök yerine koyma yöntemi ile çözülür)[cite: 26]. Örnek kök bulma adımı:
    *   $s=0$ için: $A(1)(2)(-3)=5 \implies -6A=5 \implies A=-5/6$
5.  **Ters Laplace ile Zaman Domenine Geçiş:**
    Bulunan katsayılarla ters Laplace standart formülü ($e^{at}$) kullanılarak sistemin açık dinamik yanıtı $x(t)$ elde edilir[cite: 26, 27].

---

### Soru 2: Başlangıç ve Son Değer Teoremleri (25 Puan)
**Soru:** Kompleks bir endüstriyel prosesin $s$-domenindeki çıkış fonksiyonu $Y(s)$ aşağıda verilmiştir[cite: 28]:

$$ Y(s)=\frac{s^4-6s^2+9s-8}{s(s-2)(s^3+2s^2-s-2)} $$

Bu sistemin zaman domenindeki karşılığını ($y(t)$) açıkça çözmeye gerek kalmadan, sistemin tam $t=0$ anındaki (başlangıç) ve sonsuz zamandaki ($t \to \infty$, yatışkın hal) değerlerini limit teoremleri yardımıyla bulunuz[cite: 28].

**Mühendislik Çözüm Şablonu:**
1.  **Başlangıç Değer Teoremi (Initial Value Theorem):**
    Kural: $\lim_{t\to0}y(t)=\lim_{s\to\infty}sY(s)$[cite: 28].
    $sY(s)=\frac{s(s^4-6s^2+9s-8)}{s(s-2)(s^3+2s^2-s-2)}=\frac{s^4-6s^2+9s-8}{s^4-5s^2+4}$
    Limit $s \to \infty$ için pay ve payda en yüksek dereceli $s^4$ parantezine alınır[cite: 28].
    $\lim_{s\to\infty}sY(s)=\frac{1-0+0-0}{1-0+0}=1$ (Başlangıç Değeri)[cite: 28].

2.  **Son Değer Teoremi (Final Value Theorem):**
    Kural: $\lim_{t\to\infty}y(t)=\lim_{s\to0}sY(s)$[cite: 28].
    Yine $s$ çarpanları sadeleştirildikten sonra $s=0$ değeri fonksiyonda doğrudan yerine yazılır[cite: 28].
    $\lim_{s\to0}\frac{s^4-6s^2+9s-8}{(s-2)(s^3+2s^2-s-2)}=\frac{-8}{(-2)(-2)}=\frac{-8}{4}=-2$ (Son Değer)[cite: 28].

---

### Soru 3: Proses Modelleme ve Kontrol Tasarımı (40 Puan)
**Soru:** Bir karıştırma prosesinde iki akım bir tankta birleştirilerek istenilen bileşimde bir çıkış akımı elde edilmek istenmektedir[cite: 23]. Akım 1'in kütlesel debisi $w_1$ sabittir ancak kütlesel kesri ($x_1$) zamanla değişen bir bozucu etkendir[cite: 23]. Akım 2 ise "Saf A" bileşeninden oluşmaktadır ($x_2=1$) ve debisi $w_2$ bir kontrol vanası ile ayarlanabilmektedir[cite: 23]. Tanktaki karışımın hacmi ($V$) ve yoğunluğu ($\rho$) sabit kabul edilmektedir[cite: 25].
a) Kararlı halde (steady-state), çıkış akımında istenilen hedef bileşime ($x_R$) ulaşmak için sisteme beslenmesi gereken Akım 2 debisinin ($w_2$) formülünü türetiniz[cite: 23].
b) Sistemin "A" bileşeni için **yatışkın olmayan hal (unsteady-state)** diferansiyel kütle denkliğini çıkarınız[cite: 25].
c) Girdi derişimi ($x_1$) değiştiğinde, çıkış bileşimini $x_R$'de tutabilmek için prosesin Blok Diyagramını / Kontrol Şemasını çizerek mantığını açıklayınız[cite: 24].

**Mühendislik Çözüm Şablonu:**
1.  **Kararlı Hal Kütle Denklikleri (a Şıkkı):**
    Toplam kütle denkliği: $w=w_1+w_2$[cite: 23, 25].
    Bileşen kütle denkliği: $w_1x_{1s}+w_2(1)=wx_R$[cite: 23].
    Birinci denklem ikincide yerine yazılırsa: $w_1x_{1s}+w_2=(w_1+w_2)x_R$[cite: 23].
    Denklem $w_2$ için düzenlendiğinde:
    $w_2=w_1\frac{x_R-x_{1s}}{1-x_R}$[cite: 23].

2.  **Yatışkın Olmayan Hal Dinamik Modeli (b Şıkkı):**
    Genel Prensip: *Giren - Çıkan = Birikim*[cite: 25].
    Toplam Kütle Birikimi: $\frac{d(V\rho)}{dt}=w_1+w_2-w$[cite: 25].
    A Bileşeni Kütle Birikimi: $\frac{d(V\rho x)}{dt}=w_1x_1+w_2x_2-wx$[cite: 25].
    Türev açılımı yapılır: $\rho V\frac{dx}{dt}+x\frac{d(V\rho)}{dt}=w_1x_1+w_2(1)-wx$[cite: 25].
    Toplam kütle birikimi terimi yerine yazıldığında dinamik model elde edilir:
    $\rho V\frac{dx}{dt}+x(w_1+w_2-w)=w_1x_1+w_2-wx \implies \rho V\frac{dx}{dt}=w_1(x_1-x)+w_2(1-x)$[cite: 25].

3.  **Proses Kontrol Stratejisi ve Şeması (c Şıkkı):**
    Bozucu etken $x_1$'in sisteme girmeden önce ölçülüp, hata oluşmadan önce müdahale edilmesini sağlayan **İleri Beslemeli (Feedforward)** benzeri bir strateji uygulanmalıdır[cite: 24]. $x_1$ çok yüksek olduğunda kontrolcü $w_2$'yi azaltmalı, $x_1$ düştüğünde ise $w_2$'yi artırmalıdır[cite: 24].

```mermaid
graph TD
    W1((Giriş Akımı 1<br>w1 sabit, x1 bozucu)) --> TANK[Tam Karıştırmalı<br>Sistem Tankı]
    W2((Giriş Akımı 2<br>Saf A, w2 ayar)) --> VALVE[Kontrol Vanası] --> TANK
    TANK --> W((Çıkış Akımı<br>w, hedef x_R))
    
    W1 -.->|x1 ölçümü| AT((AT<br>Analizör))
    AT -.-> AC((AC<br>Kontrolör))
    AC -.->|Hesaplanmış Sinyal| VALVE
    
    style TANK fill:#e8f4f8,stroke:#31708f,stroke-width:2px
    style AC fill:#fcf8e3,stroke:#8a6d3b,stroke-width:2px
```
