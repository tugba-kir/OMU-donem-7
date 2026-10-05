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
