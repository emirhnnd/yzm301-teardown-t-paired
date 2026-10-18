# LEDGER.md — K2: t testi, eşleştirilmiş ortalama (`t-paired`)

Hedef: `GPowerNT.exe` 3.1.9.7, x86, SHA-256 `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
Araç: REA 6.5.0 + Ghidra 12.1.4 (salt okunur). Tarih: 2026-10-18. Oturum 1 (inceleme).

Etiketler: **[REA]** binary'den kanıtlandı (adres), **[DOK]** yayımlanmış kaynakta var, **[AJAN]** ajan çıkarımı (diferansiyel testle sınanır),
**[KÂHİN]** G\*Power arayüz çıktısıyla gözlendi (oracle/ içindeki ekran görüntüsü). Alan adları (`[+0xNN]`) nesne ofsetidir; anlamları [AJAN] çıkarımıdır.
Adresler Ghidra'nın verdiği `FUN_xxxxxxxx` adresleridir. Alıntılar kısadır, decompile çıktısı repoda yoktur.

## A. Motor sınıfı ve genel yapı

| # | Etiket | İddia | Kanıt |
|---|--------|-------|-------|
| 1 | [REA] | `CEff_T_PairedMeans` bir arayüz penceresidir (etki büyüklüğü hesaplayıcı), hesap motoru değildir. Nesne boyutu 0x4a8, 7 adet `CEdit` alt denetimi | `CRuntimeClass` 0x5d6794, ad dizesi 0x5d698c, üretici 0x52e5f0 |
| 2 | [REA] | Motor sınıfı `PowerTPairedMean`; sanal tablosu 0x5cac60 | RTTI dizesi 0x60ce90, sanal tablo başvuruları 0x4d2f38, 0x4dca39 |
| 3 | [REA] | `PowerTPairedMean`, `PowerTOneMean` sınıfından türetilmiş. Önce OneMean kurulur, sonra sanal tablo işaretçisi PairedMean ile değiştirilir. Boyut 0x368, ortak başlatıcı 0x4dc230 | 0x4d2bc0 |
| 4 | [REA] | 0x4d2bc0 bütün güç analizi motorlarını yaratıp listeye ekler (PowerTCorr, PowerTMeans, PowerTOneMean, PowerTPairedMean, PowerTWilcoxPair ...) | 0x4d2bc0 |
| 5 | [REA] | Varsayılanlar: [+0xb0]=0.05, [+0xb8]=0.95, [+0xd8]=0.5, [+0xe8]=100.0, [+0x80]=1.0, [+0x35c]=0, [+0x360]=-1 (int), [+0xa8]=0x3ff0000000000004 | 0x4dc230 |
| 6 | [AJAN] | Bu alanlar sırasıyla alfa, hedef güç, dz, N, df çarpan indeksi, popülasyon büyüklüğüdür | Değerlerden ve aşağıdaki kullanımlardan çıkarım; 7-9. satırlar kullanımı doğrular |
| 7 | [REA] | Sanal tablo 3. yuva (0x4dc9d0) nesnenin kopyasını (Clone) yaratır | 0x4dc9d0 |
| 8 | [REA] | Sanal tablo 1. yuva 0x496830, "amaç fonksiyonu" dağıtıcısıdır: mod alanı [+0x2ac] 0, 1, 3, 4 değerlerine göre sırasıyla 0x4968d0, 0x4bde30, 0x4d37f0, 0x4d3830 | 0x496830, tablo 0x5cad70 |

## B. Güç fonksiyonu ve df/ncp

| # | Etiket | İddia | Kanıt |
|---|--------|-------|-------|
| 9 | [REA] | Mod 0 amaç fonksiyonu f(N) = güç(dz, alfa, N) − hedef güç ([+0xb8]). N çözülürken kök aranan fonksiyon budur | 0x4968d0 |
| 10 | [REA] | Mod 3 amaç fonksiyonu alfayı çözer: f(alfa)=güç(dz, alfa, N) − hedef. (Bu yuva N'yi DEĞİL alfayı çözer; bkz. HALLUCINATIONS #3) | 0x4d37f0, çözücü giriş 0x4960b0 |
| 11 | [REA] | Genel güç hesabı: n1, n2 ve toplam N (= n1+n2, [+0xe8]) saklanır, df için sanal yuva 73 çağrılır; bayt [+0x2a9]==0 ise alfa ikiye bölünür (iki yönlü); kritik değer merkezi, güç merkezsel olmayan dağılımdan | 0x4d38b0 |
| 12 | [REA] | Güç(dz, alfa, N) sanal yuva 12 (0x4bdee0): n1 = N/2, n2 = N/2 ile genel güç hesabını çağırır | 0x4bdee0 |
| 13 | [REA] | df = k[idx]·N − (1, bayt [+0x358]==0 ise). k tablosu 0x6096a8: k[0]=1.0, k[1]=1.0, k[2]=1.5; varsayılan idx 0 ⇒ df = N − 1 | 0x4db950, 0x6096a8, 0x4dc230 |
| 14 | [REA] | ncp δ = dz·√(k[idx]·N); [+0x360] > 0 ise k, (1 − N/[+0x360]) ile bölünür (varsayılan −1 ⇒ düzeltme yok) | 0x4dc1b0 (aynı yapı 0x4dbdc0, 0x4dc0b0, 0x4dc130) |
| 15 | [DOK] | Eşleşmiş t testi: merkezsel olmayan t, df = N−1, δ = dz√N (Faul ve ark. 2007, 2009) | yayın |
| 16 | [KÂHİN] | 37 sayısal vektörde δ = |dz|√N ve df = N − 1; kritik t = t_{1−α/2,df} (iki yönlü) / t_{1−α,df} (tek yönlü); güç = merkezsel olmayan t kuyruk olasılığı (scipy ile 1e-7 içinde) | oracle/ |

## C. N çözücüsü (kılavuzda olmayan davranışlar)

| # | Etiket | İddia | Kanıt |
|---|--------|-------|-------|
| 17 | [REA] | N çözücü sanal yuva 18 (0x496aa0): mod=0 yapar; aralık kurucuyu (yuva 25) çağırır; Brent kök bulucu (0x4f9bb0) ile **en çok 300 yineleme**, tolerans parametresi 1e-10; sonuç N* ([+0xe8]) | 0x496aa0 |
| 18 | [REA] | Kök bulucu 0x4f9bb0 Brent yöntemidir: işaret değişimi yoksa durum=1 ve 0 döner; yineleme bitince durum=2 ve son nokta döner; durma: f=0 ya da yarı aralık ≤ \|x\|·1.11e-16 | 0x4f9bb0 |
| 19 | [REA] | Brent'e giren aralığı kuran işlev (0x49a210 → 0x4962d0) alt sınır **2,0**, başlangıç üst sınırı **100,0** verir. f(100) ≥ 0 ise üst=100, alt=(2+100)/2 ve f(alt)>0 olduğu sürece üst=alt, alt=(alt+2)/2−2 ile daralır; f(100)<0 ise alt=100, üst=160 ve f(üst)<0 olduğu sürece alt=üst, üst=üst·1,6 ile büyür; sonunda alt<2 ise alt=2 | 0x49a210, 0x4962d0 |
| 20 | [REA] | Yuvarlama (yuva 29, 0x496a20): x ← ⌊N*·10¹⁰ + 0,5⌋/10¹⁰, sonra ⌈x⌉. Yani 10 ondalığa yuvarla, sonra yukarı yuvarla | 0x496a20 |
| 21 | [REA] | Çözücü, sonuç ≤ alt sınır (2,0) ise N'yi alt sınıra (2) kıstırır ve yeniden yuvarlar; sonra gerçek gücü tamsayı N'de hesaplar ([+0x108]) | 0x496aa0 |
| 22 | [KÂHİN] | a priori modda N = 2 mümkündür (güç ≥ alfa olan hedefler için: vektör 19, 20, 21, 26); post hoc modda N=2 hata verir (aşağıdaki 25) | oracle 19-21, 26, 36 |
| 23 | [KÂHİN] | Scipy ile "hedefi sağlayan en küçük tamsayı N" 37 vektörün hepsinde G\*Power N'sine eşit | tests/ |

## D. Geçersiz girdi davranışı

| # | Etiket | İddia | Kanıt |
|---|--------|-------|-------|
| 24 | [REA] | Güç ve alfa kontrolü: `alfa <= güç` değilse "Power must be greater than or equal to alpha." (eşitlik geçerli) | 0x4880e0, dize 0x5c6220 |
| 25 | [REA] | Toplam örneklem büyüklüğü kontrolü: min ≤ N ≤ max değilse "Total sample size is outside the admissible range (min, max)". Çağıran 0x4da690: min = [+0xf8] + 2,0, max = 0x7ffffffe (2147483646). Arayüzde gözlenen: (3, 2147483646) | 0x488a10, 0x4da690, dize 0x5c6524 |
| 26 | [REA] | Etki büyüklüğü kontrolü (PairedMean tablosu +0x104, 0x4db990): a priori modda \|dz\| < 1e-5 ise "In an a priori analysis, the absolute value of the\neffect size be greater than 0.00001." Ardından dz ∈ [−20, 20] aralığı denetlenir ("... is outside the admissible range (−20, 20)") | 0x4db990 (ikizi 0x4da5d0), 0x487b70, dize 0x5cb510 |
| 27 | [KÂHİN] | Güç = alfa geçerli (vektör 26). Güç 0,04 < alfa=0,05 hatalı (vektör 27). dz = 0 hatalı (vektör 28). Post hoc N = 2 hatalı (vektör 36) | oracle ekran görüntüleri |
| 28 | [KÂHİN] | Negatif dz: N, \|dz\| ile aynı; ekranda kritik t ve δ negatif işaretli (vektör 29, 30) | oracle 29, 30 |

## Bilinmeyenler (çözülmedi; [AJAN] olarak SPEC'te işaretli)

- Güç ≥ alfa kontrolünün a priori dışında (post hoc) uygulanıp uygulanmadığı: post hoc güç girilmez, uygulanmaz.
- dz üst sınırının ([−20, 20]) PairedMean için kesin değeri: sabitler okundu, ancak sınıra yakın GUI vektörü alınmadı.
- Alfa ve güç için "admissible range" kenar değerleri (örn. alfa=0, alfa=1): GUI vektörü alınmadı.
- Çok büyük N'de (> ~10⁷) Brent'in 300 yineleme sınırı: 78491'e kadar gözlendi.
