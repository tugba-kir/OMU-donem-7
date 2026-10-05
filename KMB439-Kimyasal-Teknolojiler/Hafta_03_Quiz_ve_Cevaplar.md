# 📝 KMB439 Kimyasal Teknolojiler - Hafta 03: Öz-Değerlendirme ve Sınav Hazırlığı

Bu doküman, 3. hafta konularının mühendislik temellerini pekiştirmek ve sınav senaryolarına hazırlık yapmak amacıyla oluşturulmuştur.

---

### 💧 Soru 1 (Su Sertliği ve Hesaplama)
**Suda kalsiyum ($Ca^{+2}$) ve magnezyum ($Mg^{+2}$) iyonlarının analizi yapılırken neden doğrudan bu elementler yerine referans olarak Kalsiyum Karbonat ($CaCO_3$) baz alınır? Açıklayınız.**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> Kalsiyum karbonatın ($CaCO_3$) mol kütlesi tam olarak **100 g/mol**'dür. Analitik kimya hesaplamalarında (milieşdeğer veya mg/L birimlerine geçerken) bu tam sayı matematiksel olarak çok büyük bir kolaylık sağlar. Ayrıca kalsiyum ve magnezyum iyonlarının sitokiyometrik (değerlik) oranları aynı olduğundan, sistemde sadece tek bir kirletici varmış gibi ortak bir $CaCO_3$ referansı üzerinden "Toplam Sertlik" tek bir denklemde formüle edilebilir.

---

### 🌡️ Soru 2 (Kireç-Soda Kimyası)
**Soğuk kireç-soda işlemi ile Sıcak kireç-soda işlemi arasındaki temel termodinamik ve operasyonel farklar nelerdir? Sıcak işlemin buhar kazanları için zorunlu olmasının nedenini kinetik ve gaz giderimi ($stripping$) açısından açıklayınız.**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> * **Soğuk Proses:** Ortam sıcaklığında yapılır, reaksiyon ve çökelme yavaştır. Çıkış suyunda 30-40 mg/L kalıntı sertlik bırakır (şehir şebeke suları için yeterlidir).
> * **Sıcak Proses:** 95-100 °C bandında çalışır. Isı, termodinamik olarak reaksiyonu ve kinetik olarak çökelmeyi hızlandırır. Yüksek sıcaklık suyun **viskozitesini düşürür**, böylece oluşan çamur (floklar) çok daha hızlı dibe çöker. Ayrıca çözünmüş haldeki oksijen ve karbondioksit gibi korozif gazlar sıcaklıkla uçurulur (stripping).
> * **Zorunluluk:** Buhar kazanlarında yüksek basınç ve sıcaklık altında çok küçük sertlik iyonları bile birikerek "kışır/kabuk" oluşturup boruları patlatabilir veya ısı transferini bozabilir. Sıcak proses kalıntı sertliği 10 mg/L'nin altına düşürdüğü ve korozyon yapan gazları uzaklaştırdığı için kazan besleme sularında zorunludur.

---

### ⚗️ Soru 3 (Azeotrop ve Saflaştırma)
**Etil alkolün su ile oluşturduğu karışım neden basit ayrımsal damıtma ile %100 saflığa ulaştırılamaz? Bu karışımı mutlak alkole dönüştürmek için kullanılan zeolitlerin (moleküler eleklerin) çalışma prensibi nedir?**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> Alkol ve su, %96 alkol - %4 su oranına geldiğinde **azeotropik bir karışım** oluşturur. Bu oranda sıvının kaynama noktası ile buharının kaynama noktası (buhar-sıvı dengesi / VLE) eşitlenir. Yani sıvı kaynadığında çıkan buharın bileşimi yine %96 alkol, %4 su olur. Bu yüzden ayrımsal damıtma (distilasyon) bu noktadan öteye gidemez. 
> **Zeolitler (Moleküler Elekler)** ise gözenek çapları çok hassas ayarlanmış (genellikle 3 Ångström) katı alüminosilikatlardır. Su moleküllerini (çapı daha küçük olduğu için) içlerine hapsederken, büyük etanol moleküllerinin geçmesine izin vererek %100 saf alkol eldesini fiziksel adsorpsiyonla sağlarlar.

---

### 🏭 Soru 4 (Kriyojenik Üretim)
**Endüstride yüksek saflıkta azot gazı elde etmek için uygulanan fraksiyonlu damıtma (havanın sıvılaştırılması) işleminde, azot ve oksijenin birbirinden ayrılmasını sağlayan fiziksel özellik farkı nedir?**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> Fraksiyonlu damıtmada ana ayırma prensibi **kaynama noktası (uçuculuk) farkıdır**. Sıvı azot -196 °C'de, sıvı oksijen ise -183 °C'de kaynar. Sıvılaştırılmış hava fraksiyon kolonunda ısıtılmaya başlandığında, kaynama noktası daha düşük (daha uçucu) olan Azot, kolonun üst kısmında gaz fazına geçerek ayrılır; kaynama noktası daha yüksek (daha az uçucu) olan oksijen ise kolonun alt kısmında sıvı olarak kalır.

---

### ❄️ Soru 5 (Fizikokimyasal Olaylar)
**Sıvı azot ile çalışırken karşılaşılan "Leidenfrost Etkisi" nedir ve bu durum pratik uygulamalarda nasıl bir fiziksel davranışa yol açar?**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> Sıvı azotun kaynama noktası çok düşüktür (-196 °C). Ortam sıcaklığındaki (örneğin 25 °C) bir yüzeye veya canlı dokuya temas ettiğinde, yüzey ile sıcaklık farkı o kadar yüksektir ki, sıvı azot damlasının alt kısmı temas anında aniden buharlaşır. Bu oluşan gaz tabakası, sıvının geri kalanı ile sıcak yüzey arasında **yalıtkan (izolatör) bir buhar yastığı** görevi görür. Buna *Leidenfrost Etkisi* denir. Bu etki sayesinde sıvı anında kaynayıp yok olmak yerine, buhar tabakası üzerinde sürtünmesizce süzülür.

---

### 🚗 Soru 6 (Gaz Yasaları ve Airbag Stokiyometrisi)
**Arabalardaki hava yastıklarında (airbag) azot gazı üretim mekanizmasını sodyum azidin ($NaN_3$) bozunma reaksiyonu üzerinden yazınız. Milisaniyeler içinde ~50 L hacme ulaşması gereken bir hava yastığı tasarımında, tepkime stokiyometrisinin önemi nedir? Neden Oksijen değil de Azot gazı açığa çıkarılmaktadır?**

> **💡 Çözüm ve Mühendislik Yaklaşımı:**
> Hava yastıklarındaki temel reaksiyon, sodyum azidin elektriksel bir kıvılcımla çok hızlı bozunmasıdır:
> $$2NaN_3(k) \rightarrow 2Na(k) + 3N_2(g)$$
> * **Stokiyometri ve Hacim:** Denklemden görüleceği üzere 2 mol katı maddeden aniden 3 mol gaz açığa çıkar. Mühendisler, arabanın kabin hacmine (örneğin 50 Litrelik bir yastık) ve saniyenin onda biri süresinde gereken basınca göre termodinamik denklemlerle kaç mol gaz gerekeceğini hesaplar ve ona uygun miktarda $NaN_3$ yerleştirirler. 
> * **Azotun Tercihi:** Çarpışma anında yüksek sıcaklık ve basınç oluşur. Eğer sistemde Oksijen ($O_2$) kullanılsaydı, reaktif ve yakıcı bir gaz olduğu için patlamalara veya yanıklara sebep olabilirdi. Bunun yerine kimyasal olarak **inert** (tepkimeye girmeyen), üçlü bağ yapısı sayesinde çok kararlı ve güvenli olan Azot ($N_2$) gazı tercih edilir.
# 🎯 KMB439 Kimyasal Teknolojiler - Hafta 03: Kritik Hesaplama ve Sınav Senaryoları

Bu doküman, sınavlarda karşına çıkabilecek yüksek puanlı "Tasarım/Hesaplama" ve "Kavramsal Senaryo" soruları için ideal çözüm şablonlarını içermektedir.

---

## 🧮 Senaryo 1: Kireç-Soda Prosesi Kütle Denkliği (Hesaplama Sorusu)

**Soru Senaryosu:** 
Bir endüstriyel tesisin su kaynağında analiz yapılmış ve suda litre başına **162 mg Kalsiyum Bikarbonat [$Ca(HCO_3)_2$]** (geçici sertlik) ve **136 mg Kalsiyum Sülfat [$CaSO_4$]** (kalıcı sertlik) tespit edilmiştir. 
Bu tesisin **1 metreküp ($1 \ m^3$)** suyunu tamamen yumuşatmak için teorik olarak kaç gram Kireç ($CaO$) ve Soda ($Na_2CO_3$) eklenmesi gerektiğini hesaplayınız.
*(Mol Kütleleri: $Ca(HCO_3)_2$=162 g/mol, $CaSO_4$=136 g/mol, $CaO$=56 g/mol, $Na_2CO_3$=106 g/mol)*

> **💡 Mühendislik Çözüm Şablonu (Adım Adım):**
> 
> **1. Adım: Verileri Mole Çevirme (1 Litre için)**
> * Geçici Sertlik: $162 \ mg/L = 0.162 \ g/L \rightarrow \frac{0.162 \ g}{162 \ g/mol} = 0.001 \ mol/L$
> * Kalıcı Sertlik: $136 \ mg/L = 0.136 \ g/L \rightarrow \frac{0.136 \ g}{136 \ g/mol} = 0.001 \ mol/L$
>
> **2. Adım: Toplam Hacme Geçiş ($1 \ m^3 = 1000 \ L$)**
> * $1 \ m^3$ sudaki $Ca(HCO_3)_2$ miktarı $= 0.001 \ mol/L \times 1000 \ L = \mathbf{1 \ mol}$
> * $1 \ m^3$ sudaki $CaSO_4$ miktarı $= 0.001 \ mol/L \times 1000 \ L = \mathbf{1 \ mol}$
>
> **3. Adım: Geçici Sertliğin Giderilmesi (Kireç İhtiyacı)**
> Reaksiyon: $$Ca(HCO_3)_2 + CaO \rightarrow 2CaCO_3\downarrow + H_2O$$
> * Stokiyometriye göre 1 mol $Ca(HCO_3)_2$ için 1 mol $CaO$ gereklidir.
> * İhtiyaç: $1 \ mol \ CaO \times 56 \ g/mol = \mathbf{56 \ gram \ Kireç}$
>
> **4. Adım: Kalıcı Sertliğin Giderilmesi (Soda İhtiyacı)**
> Reaksiyon: $$CaSO_4 + Na_2CO_3 \rightarrow CaCO_3\downarrow + Na_2SO_4$$
> * Stokiyometriye göre 1 mol $CaSO_4$ için 1 mol $Na_2CO_3$ gereklidir.
> * İhtiyaç: $1 \ mol \ Na_2CO_3 \times 106 \ g/mol = \mathbf{106 \ gram \ Soda}$
>
> **Sonuç:** $1 \ m^3$ suyun yumuşatılması için sisteme **56 gram CaO** ve **106 gram $Na_2CO_3$** dozlanmalıdır.

---

## 🧪 Senaryo 2: Azeotropik Karışımlar ve İleri Saflaştırma (Kavramsal)

**Soru Senaryosu:** 
İlaç sanayisinde solvent olarak kullanılmak üzere %100 saflıkta (mutlak) etil alkole ihtiyaç duyulmaktadır. Tesis mühendisi, su-alkol karışımını standart bir fraksiyonlu damıtma kolonuna yönlendirmiş ancak saflığın %96'yı geçemediğini raporlamıştır. 
Bu durumun termodinamik sebebini açıklayınız. Tesisteki bu sorunu çözmek ve %100 saflığa ulaşmak için hangi spesifik ayırma teknolojisi kullanılmalıdır? Moleküler seviyedeki mekanizmasını anlatınız.

> **💡 İdeal Sınav Cevabı:**
> * **Termodinamik Sebep:** Etil alkol ve su, ağırlıkça %96 alkol oranına ulaştığında **Azeotropik Karışım** oluşturur. Bu noktada buhar-sıvı dengesi (VLE) eğrileri kesişir; yani sıvının kaynamasıyla oluşan buharın bileşimi de tam olarak %96 alkol ve %4 su olur. Uçuculuk farkı ortadan kalktığı için fraksiyonlu damıtma işlemi bu noktadan öteye fiziksel olarak geçemez.
> * **Çözüm Teknolojisi:** %96'lık karışım damıtma kolonundan alındıktan sonra **Zeolit yataklarına (Moleküler Elek / Molecular Sieve)** yönlendirilmelidir.
> * **Mekanizma:** Zeolitler gözenek çapları Ångström (Å) seviyesinde hassas ayarlanmış kristal yapılı alüminosilikatlardır. Karışım bu yataklardan geçirildiğinde, molekül çapı küçük olan su molekülleri (yaklaşık 2.8 Å) zeolitin gözeneklerine girerek fiziksel olarak hapsolur (adsorpsiyon). Çapı daha büyük olan etanol molekülleri (yaklaşık 4.4 Å) ise gözeneklere sığmaz ve yatağı pas geçerek %100 saf (mutlak) alkol olarak sistemi terk eder.

---

## ⚙️ Senaryo 3: Proses Seçimi ve Optimizasyon (Vaka Analizi)

**Soru Senaryosu:** 
Yeni kurulan büyük bir endüstriyel tesisin su arıtma departmanında iki farklı hat planlanmaktadır:
1. Hat: Tesis personelinin kullanımı ve genel temizlik için şehir şebeke suyu.
2. Hat: Tesisteki reaktörleri ısıtacak olan 40 bar basınçlı buhar kazanının besleme suyu.
Kireç-Soda prosesi kullanılacağı bilinmektedir. Hangi hat için "Sıcak", hangi hat için "Soğuk" kireç-soda prosesi tercih edilmelidir? Mühendislik gerekçeleriyle karşılaştırarak açıklayınız.

> **💡 İdeal Sınav Cevabı:**
> * **1. Hat (Genel Kullanım):** **Soğuk Kireç-Soda Prosesi** tercih edilmelidir. Ortam sıcaklığında gerçekleştiği için enerji maliyeti düşüktür. Çıkış suyunda bıraktığı 30-40 mg/L kalıntı sertlik, genel kullanım ve temizlik (sabun sarfiyatını azaltmak) için tamamen yeterli ve kabul edilebilir bir standarttır.
> * **2. Hat (Buhar Kazanı):** **Sıcak Kireç-Soda Prosesi** zorunludur.
>   * *Kinetik Gerekçe:* Yüksek sıcaklık (95-100 °C) reaksiyonu hızlandırır, suyun viskozitesini düşürerek oluşan çökeleklerin (flokların) durultucuda çok daha hızlı ve kompakt şekilde çökmesini sağlar.
>   * *Termodinamik Gerekçe:* Sıcaklık artışı gazların sudaki çözünürlüğünü azaltır. Kazanda korozyona sebep olacak çözünmüş Oksijen ($O_2$) ve Karbondioksit ($CO_2$) sistemden "stripping" ile uzaklaştırılır.
>   * *Güvenlik Gerekçesi:* Yüksek basınçlı kazanlarda en ufak bir sertlik iyonu bile buharlaşma sonucu ısıtıcı borularda taşlaşarak (kışır/kabuk) patlamalara yol açar. Sıcak proses kalıntı sertliği 10 mg/L'nin altına düşürerek kazan güvenliğini sağlar.

---

## 🌬️ Senaryo 4: Gaz Ayrıştırma ve Endüstriyel Dizayn (Kavramsal)

**Soru Senaryosu:** 
Gıda ambalajlamasında cips paketlerinin içinin hava yerine saf Azot ($N_2$) gazı ile doldurulduğu bilinmektedir. Ambalajlama için oksijenin neden uygun olmadığını kimyasal reaktiflik açısından açıklayınız. Endüstride bu işlem için gereken binlerce ton saf azot gazı, hangi hammadde ve hangi proses kullanılarak elde edilir?

> **💡 İdeal Sınav Cevabı:**
> * **Kimyasal Reaktiflik:** Oksijen ($O_2$) oldukça reaktif ve yükseltgeyici (okside edici) bir gazdır. Gıdalardaki yağlarla reaksiyona girerek acılaşmaya (oksidasyon) ve bakteriyel/mantar büyümesine zemin hazırlar. Azot ($N_2$) ise içerdiği üçlü bağ ($N \equiv N$) nedeniyle son derece kararlı, **inert (tepkimeye girmeyen)** bir gazdır. Gıdanın raf ömrünü uzatır ve pakete mekanik destek sağlar.
> * **Hammadde ve Proses:** Bu çapta devasa bir azot ihtiyacı için tek ekonomik hammadde **Atmosferik Hava**'dır (%78 $N_2$, %21 $O_2$). Kullanılan proses ise **Havanın Sıvılaştırılarak Fraksiyonlu Damıtılmasıdır (Kriyojenik Ayrıştırma)**.
> * **Proses Adımları:** Hava yüksek basınçta sıkıştırılır, nemi ve $CO_2$'si alınır, ardından aniden genleştirilerek (Joule-Thomson etkisi) sıvılaştırılır. Sıvı hava fraksiyon kolonuna gönderilir. Sıvı azot -196 °C'de, sıvı oksijen -183 °C'de kaynar. Kaynama noktası düşük (daha uçucu) olan azot gaz fazına geçerek kolonun tepesinden yüksek saflıkta çekilir.
