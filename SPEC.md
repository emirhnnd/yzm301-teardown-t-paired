# SPEC.md — `t-paired`: eşleştirilmiş ortalamalar için t testi güç analizi

Bu belge **tek başına yeterli** bir şartnamedir: hesap motorunu bu belgeden yazan kişi başka kaynağa bakmak zorunda kalmamalıdır.
Davranışlar, referans programın (güç analizi aracı, "kâhin") çıktısından ve statik incelemeden çıkarılmıştır. İzlenebilirlik için `LEDGER.md` satır numaraları köşeli parantezle verilmiştir: örn. `[L17]`. Etiketler: **[REA]** ikili dosyadan kanıtlı, **[DOK]** yayımlanmış formül, **[KÂHİN]** referans çıktısında gözlenmiş, **[AJAN]** çıkarım, ayrıca sınanmalı.

Kapsam: tek test ailesi **t-paired** (iki bağımlı ortalama, eşleştirilmiş çiftler; etki büyüklüğü *dz*), iki mod: **a-priori** (N hesapla) ve **post-hoc** (güç hesapla). Örneklem büyüklüğü *N çift sayısıdır*.

## 1. Tanımlar

- `dz`: etki büyüklüğü (fark ortalamasının fark standart sapmasına oranı), işaretli gerçek sayı.
- `alpha`: birinci tür hata olasılığı.
- `tails`: 1 ya da 2.
- `power`: hedef güç (a-priori girdisi). `actual_power`: tamsayı N'deki gerçek güç (çıktı).
- `N`: çift sayısı (tamsayı). `df = N − 1`. `ncp = |dz|·√N` (çıktıda işaret aşağıda). [L13][L14][L15][KÂHİN]

### 1.1 Güç fonksiyonu (N gerçek sayı da olabilir)

```
power(N, tails, dz, alpha):
    df  = N - 1                     # gerçek değerli df kabul edilir
    ncp = abs(dz) * sqrt(N)
    if tails == 2:
        c = t_quantile(1 - alpha/2, df)            # merkezi t
        return 1 - nct_cdf(c, df, ncp) + nct_cdf(-c, df, ncp)
    else:
        c = t_quantile(1 - alpha, df)
        return 1 - nct_cdf(c, df, ncp)
```
`nct_cdf` merkezsel olmayan t dağılımının birikimli dağılımıdır (scipy `scipy.stats.nct.cdf`, `scipy.stats.t.ppf`). [L11][L12][L16]

Çıktı alanları (tamsayı N için): `critical_t = c` (iki yönlü: pozitif üst kritik değer), `df = N-1`, `ncp = |dz|*sqrt(N)`; **dz < 0 ise `critical_t` ve `ncp` negatif işaretli yazılır** ve güç `|dz|` ile aynıdır. [L28][KÂHİN]

### 1.2 n1 / n2 ve toplam N

Motor içinde eşleştirilmiş test için `n1 = n2 = N/2` tutulur ve toplam `N = n1 + n2`'dir; `df`, `ncp` ve yukarıdaki güç fonksiyonu bu toplam `N`'i (= çift sayısını) kullanır. Referans arayüz yalnızca toplam örneklem büyüklüğünü gösterir. [L12][L29][REA]
CONTRACT.md eşleştirilmiş test için `n1`/`n2` çıktısı istemez; bu nedenle CLI bu alanları yazmaz, yalnızca `n_total` yazar. İç temsil bilgisi yalnızca kanıt kaydıdır. [L30][AJAN]

## 2. a-priori (N hesapla)

### 2.1 Algoritma [L17–L21]

`f(N) = power(N, tails, dz, alpha) − power_hedef` olsun.

1. **Aralık kurulumu** (alt sınır `LO = 2.0`, başlangıç üst sınırı `H0 = 100.0`):
```
if f(H0) >= 0:
    hi = H0
    lo = (LO + H0) / 2
    while lo >= LO and f(lo) > 0:
        hi = lo
        lo = (lo + LO) / 2 - LO
else:
    lo = H0
    hi = H0 * 1.6
    while f(hi) < 0:
        lo = hi
        hi = hi * 1.6
if lo < LO: lo = LO
```
2. **Kök**: `[lo, hi]` aralığında Brent yöntemiyle `f(N*) = 0` çözülür (en çok 300 yineleme, göreli duyarlık ≈ 2.2e-16; durma: `f=0` ya da yarım aralık `<= |x|·1.11e-16`). İşaret değişimi yoksa kök bulucu `0` döndürür. Yineleme sınırı dolarsa son nokta döner.
3. **Yuvarlama**: `r(x) = ceil( floor(x·1e10 + 0.5) / 1e10 )`. Yani önce 10 ondalığa yuvarla, sonra yukarı yuvarla. `N* ← r(N*)`.
4. **Alt sınır kıstırma**: `N* < lo` ise (alt sınır 2) `N* ← r(lo)` (= 2).
5. `N = N*` (tamsayı). `actual_power = power(N, tails, dz, alpha)`; `critical_t`, `df`, `ncp` yukarıdaki gibi.

Sonuç `N`, "hedef gücü sağlayan en küçük tamsayı" ile **bütün gözlenen vektörlerde aynıdır**, ancak 3. adımdaki 10 ondalık yuvarlama nedeniyle `N*` bir tamsayının en çok 5e-11 üstündeyse o tamsayı seçilir. [L20][L23]
Kütüphaneler (R `pwr`, `statsmodels`) kesirli N verir; bu referans her zaman yukarı yuvarlar. [KÂHİN]

### 2.2 Notlar

- `power_hedef <= power(2, ...)` ise `N = 2` olur (alt sınır). Örn. dz=0.5, alpha=0.05, 2 yönlü: `power(2) = 0.0619486`, bu yüzden hedef 0.05, 0.051 ya da 0.06 için `N = 2`. [L22][KÂHİN]
- `N` üst sınırı 2147483646'dır; çözücü bunu aşarsa hata (bölüm 4) verilir. [AJAN]

## 3. post-hoc (güç hesapla)

`n_total` (N) tamsayı verilir; hesaplanan güç `power = power(N, tails, dz, alpha)` olarak döner; ek olarak `critical_t`, `df`, `ncp`. `power` girdisi yoktur. [KÂHİN]

## 4. Geçersiz girdi davranışı

Hata mesajlarının **ilk satırı** referanstan gözlenmiştir. CLI hatada çıktıyı `{"error": "<mesaj>", "code": "<KOD>", "field": "<alan>"}` tek satır JSON olarak verir (CONTRACT.md v1.0.0); geçersiz girdide çıkış kodu 2, iç hatada 1.

| Koşul | Mod | Mesaj | Kanıt |
|---|---|---|---|
| `alpha > power` (`alpha == power` geçerli) | a-priori | `Power must be greater than or equal to alpha.` (`INCONSISTENT`) | [L24] [KÂHİN] vektör 26, 27 |
| `abs(dz) < 1e-5` (tam 1e-5 geçerli) | a-priori | `In an a priori analysis, the absolute value of the effect size be greater than 0.00001.` | [L26] [KÂHİN] vektör 28 |
| `N < 3` ya da `N > 2147483646` (N tamsayı) | post-hoc | `Total sample size is outside the admissible range (3, 2147483646)` | [L25] [KÂHİN] vektör 36 |
| `dz` ∉ [−20, 20] | iki mod | `... is outside the admissible range (-20, 20)` | [L26] [AJAN] kenar vektörü yok |
| `alpha` ∉ (0,1), `power` ∉ (0,1), `tails` ∉ {1,2}, eksik/sayı olmayan girdi | iki mod | herhangi bir açıklayıcı mesaj | [AJAN] |
| Hesaplanan a-priori N > 2147483646 | a-priori | `Total sample size is outside the admissible range (3, 2147483646)` | [AJAN] |

Not: a-priori modda `N = 2` **geçerli** bir sonuçtur (alt sınır kıstırma), post-hoc modda `N = 2` girişi hatadır. [L22]

## 5. CLI sözleşmesi

Komut (iki ad aynı programdır): `gpower-clone` ve `powerlab` (ayrıca `python -m powerlab`). Biçim CONTRACT.md v1.0.0'a uyar.

```
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95
gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 34
```

- Bayrak adları sözleşmedeki alan adlarıdır: `--test --mode --tails --dz --alpha --power --n_total`. Varsayılan değer yoktur; moda ait her alan verilmelidir (`--n-total` tireli yazım da kabul). `--d`, `--n`, `--sample-size` gibi takma adlar yoktur.
- `a-priori` alanları: `tails dz alpha power`. `post-hoc` alanları: `tails dz alpha n_total`. Eksik alan `MISSING_PARAM`; tanınmayan ya da moda ait olmayan alan `UNKNOWN_PARAM`.
- Tek istisna: `--ratio` kabul edilir ve yok sayılır (ortak test düzeneği tüm ailelere verebilir; eşleştirilmiş testte grup oranı yoktur). [AJAN]
- `--mode` yalnızca `a-priori` ve `post-hoc`; `compromise`, `criterion`, `sensitivity` uygulanmadı (`UNSUPPORTED`). `--test` yalnızca `t-paired`; başka değer `UNSUPPORTED`.
- `--version` tek satır JSON verir: `contract_version`, `name`, `engine`.
- Başarılı çıktı **tek satır JSON**, çıkış kodu 0, günlükler stderr'e. Gerçek sayılar tam çift duyarlıkla, yuvarlanmadan yazılır; `n_total` ve `df` JSON tamsayısıdır.
  - a-priori: `ncp`, `critical_t`, `df`, `n_total`, `actual_power`.
  - post-hoc: `ncp`, `critical_t`, `df`, `power`.
- Hata: `{"error","code","field"}`; kodlar `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED`, `NO_SOLUTION`. Çıkış kodu 2 (geçersiz girdi) ya da 1 (iç hata).
- Örnek (vektör 2, post-hoc): `{"ncp":2.9154759474226504,"critical_t":2.0345152974493383,"df":33,"power":0.8077775012792737}`. Referans değerler 7 basamakta yazıldığından testler 5e-8 toleransla karşılaştırır.

## 6. Kabul ölçütleri (Gherkin)

```gherkin
Feature: a-priori N hesabı, t-paired

  Scenario Outline: referans vektörlerle birebir N, df ve 5e-8 içinde diğer değerler
    When "gpower-clone --test t-paired --mode a-priori --tails <tails> --dz <dz> --alpha <alpha> --power <power>" çalıştırılır
    Then n_total tam olarak <n_total> olmalı
    And df tam olarak <df> olmalı
    And actual_power <actual_power> değerine 5e-8 içinde eşit olmalı
    And critical_t <critical_t> değerine 5e-8 içinde eşit olmalı
    And ncp <ncp> değerine 5e-8 içinde eşit olmalı

    Examples:
      | tails | dz | alpha | power | n_total | df | actual_power | critical_t | ncp |
      | 2 | 0.5 | 0.05 | 0.95 | 54 | 53 | 0.9502120 | 2.0057460 | 3.6742346 |
      | 2 | 0.5 | 0.05 | 0.80 | 34 | 33 | 0.8077775 | 2.0345153 | 2.9154759 |
      | 1 | 0.5 | 0.05 | 0.80 | 27 | 26 | 0.8118316 | 1.7056179 | 2.5980762 |
      | 1 | 0.5 | 0.05 | 0.95 | 45 | 44 | 0.9512400 | 1.6802300 | 3.3541020 |
      | 2 | 0.2 | 0.05 | 0.80 | 199 | 198 | 0.8016910 | 1.9720175 | 2.8213472 |
      | 2 | 0.8 | 0.05 | 0.80 | 15 | 14 | 0.8213105 | 2.1447867 | 3.0983867 |
      | 2 | 0.3 | 0.05 | 0.90 | 119 | 118 | 0.9007612 | 1.9802722 | 3.2726136 |
      | 2 | 0.5 | 0.01 | 0.80 | 51 | 50 | 0.8093892 | 2.6777933 | 3.5707142 |
      | 2 | 0.5 | 0.01 | 0.95 | 75 | 74 | 0.9511756 | 2.6439129 | 4.3301270 |
      | 1 | 0.5 | 0.01 | 0.80 | 43 | 42 | 0.8011974 | 2.4184704 | 3.2787193 |
      | 2 | 0.5 | 0.10 | 0.80 | 27 | 26 | 0.8118463 | 1.7056179 | 2.5980762 |
      | 2 | 1.0 | 0.05 | 0.80 | 10 | 9 | 0.8030969 | 2.2621572 | 3.1622777 |
      | 2 | 1.0 | 0.05 | 0.99 | 21 | 20 | 0.9916492 | 2.0859634 | 4.5825757 |
      | 2 | 0.1 | 0.05 | 0.80 | 787 | 786 | 0.8000954 | 1.9629867 | 2.8053520 |
      | 2 | 0.05 | 0.05 | 0.80 | 3142 | 3141 | 0.8000668 | 1.9607195 | 2.8026773 |
      | 2 | 2.0 | 0.05 | 0.80 | 5 | 4 | 0.9088849 | 2.7764451 | 4.4721360 |
      | 2 | 3.0 | 0.05 | 0.95 | 4 | 3 | 0.9670006 | 3.1824463 | 6.0000000 |
      | 2 | 5.0 | 0.05 | 0.95 | 3 | 2 | 0.9754623 | 4.3026527 | 8.6602540 |
      | 2 | 0.5 | 0.05 | 0.06 | 2 | 1 | 0.0619486 | 12.7062047 | 0.7071068 |
      | 2 | 0.5 | 0.05 | 0.051 | 2 | 1 | 0.0619486 | 12.7062047 | 0.7071068 |
      | 1 | 0.5 | 0.05 | 0.051 | 2 | 1 | 0.1058229 | 6.3137515 | 0.7071068 |
      | 2 | 0.5 | 0.05 | 0.99 | 76 | 75 | 0.9904221 | 1.9921022 | 4.3588989 |
      | 2 | 0.5 | 0.05 | 0.999 | 104 | 103 | 0.9990026 | 1.9832641 | 5.0990195 |
      | 2 | 0.5 | 0.001 | 0.80 | 74 | 73 | 0.8025148 | 3.4288542 | 4.3011626 |
      | 2 | 0.01 | 0.05 | 0.80 | 78491 | 78490 | 0.8000024 | 1.9599942 | 2.8016245 |
      | 2 | 0.5 | 0.05 | 0.05 | 2 | 1 | 0.0619486 | 12.7062047 | 0.7071068 |
      | 1 | -0.5 | 0.05 | 0.80 | 27 | 26 | 0.8118316 | -1.7056179 | -2.5980762 |
      | 2 | -0.5 | 0.05 | 0.80 | 34 | 33 | 0.8077775 | -2.0345153 | -2.9154759 |
```

```gherkin
Feature: post-hoc güç hesabı, t-paired

  Scenario Outline: referans vektörlerle güç
    When "gpower-clone --test t-paired --mode post-hoc --tails <tails> --dz <dz> --alpha <alpha> --n_total <n_total>" çalıştırılır
    Then df tam olarak <df> olmalı
    And power <power> değerine 5e-8 içinde eşit olmalı
    And critical_t <critical_t> değerine 5e-8 içinde eşit olmalı
    And ncp <ncp> değerine 5e-8 içinde eşit olmalı

    Examples:
      | tails | dz | alpha | n_total | df | power | critical_t | ncp |
      | 2 | 0.5 | 0.05 | 34 | 33 | 0.8077775 | 2.0345153 | 2.9154759 |
      | 2 | 0.5 | 0.05 | 10 | 9 | 0.2931756 | 2.2621572 | 1.5811388 |
      | 1 | 0.5 | 0.05 | 27 | 26 | 0.8118316 | 1.7056179 | 2.5980762 |
      | 2 | 0.2 | 0.05 | 100 | 99 | 0.5082648 | 1.9842170 | 2.0000000 |
      | 2 | 0.8 | 0.05 | 15 | 14 | 0.8213105 | 2.1447867 | 3.0983867 |
      | 2 | 0.5 | 0.05 | 3 | 2 | 0.0841071 | 4.3026527 | 0.8660254 |
      | 2 | 0.5 | 0.01 | 50 | 49 | 0.7993369 | 2.6799520 | 3.5355339 |
      | 2 | 1.0 | 0.05 | 5 | 4 | 0.4013899 | 2.7764451 | 2.2360680 |
      | 2 | 0.5 | 0.05 | 1000 | 999 | 1.0000000 | 1.9623415 | 15.8113883 |
```

```gherkin
Feature: geçersiz girdiler

  Scenario Outline: hatalı girdi hata JSON'u ve sıfırdan farklı çıkış kodu verir
    When "<komut>" çalıştırılır
    Then çıktı {"error", "code", "field"} biçiminde tek satır JSON olmalı
    And çıkış kodu 2 olmalı
    And code alanı <kod> olmalı
    And error alanı "<mesaj_parçası>" içermeli

    Examples:
      | komut | mesaj_parçası | kod |
      | gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.04 | Power must be greater than or equal to alpha | INCONSISTENT |
      | gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0 --alpha 0.05 --power 0.80 | effect size be greater than 0.00001 | OUT_OF_RANGE |
      | gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 2 | outside the admissible range (3, 2147483646) | OUT_OF_RANGE |
      | gpower-clone --test t-paired --mode post-hoc --tails 3 --dz 0.5 --alpha 0.05 --n_total 20 | tails | INVALID_VALUE |
      | gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 1.5 --power 0.8 | alpha | OUT_OF_RANGE |
      | gpower-clone --test t2-indep --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.8 | test | UNSUPPORTED |
      | gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 | power | MISSING_PARAM |
      | gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.8 --n_total 30 | n_total | UNKNOWN_PARAM |
      | gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 20.5 | n_total | INVALID_VALUE |
      | gpower-clone --test t-paired --mode sensitivity --tails 2 --dz 0.5 --alpha 0.05 --n_total 20 | mode | UNSUPPORTED |

Feature: sınır davranışları

  Scenario: güç alfaya eşit geçerlidir ve N = 2 verir
    When "gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.05" çalıştırılır
    Then n_total tam olarak 2 olmalı
    And actual_power 0.0619486 değerine 5e-8 içinde eşit olmalı

  Scenario: negatif dz aynı N'yi verir, kritik değer ve ncp negatif yazılır
    When "gpower-clone --test t-paired --mode a-priori --tails 2 --dz -0.5 --alpha 0.05 --power 0.80" çalıştırılır
    Then n_total tam olarak 34 olmalı
    And critical_t -2.0345153 olmalı
    And ncp -2.9154759 olmalı
    And actual_power 0.8077775 olmalı

  Scenario: bir önceki N hedef gücü sağlamaz
    Given dz=0.5, alpha=0.05, 2 yönlü, hedef güç 0.80
    Then power(33) < 0.80 <= power(34)
    And a-priori n_total 34 olmalı

  Scenario: N* bir tamsayının hemen üzerindeyse 10 ondalık yuvarlaması o tamsayıyı seçer
    Given f(N*) = 0 kökü N* = k + 3e-11 (k tamsayı)
    Then r(N*) = k
```

## 7. Ek: bütün referans vektörleri

`oracle/oracle_vectors.csv`; ekran görüntüleri `oracle/screenshots/NN.png`. Hatalı üç vektör: 
- vektör 27: mode=a-priori tails=2 dz=0.5 alpha=0.05 power=0.04 n= ⇒ ERROR: Power must be greater than or equal to alpha.
- vektör 28: mode=a-priori tails=2 dz=0 alpha=0.05 power=0.80 n= ⇒ ERROR: In an a priori analysis, the absolute value of the effect size be greater than 0.00001.
- vektör 36: mode=post-hoc tails=2 dz=0.5 alpha=0.05 power= n=2 ⇒ ERROR: Total sample size is outside the admissible range (3, 2147483646)

## 8. Bilinmeyenler ve sınama planı

- `alpha`, `power` için kesin admissible aralığı bilinmiyor: (0,1) varsayıldı. [AJAN]
- `dz` ±20 sınırının hata metninin ön eki bilinmiyor. [AJAN]
- Çok küçük dz (örn. 1e-5) için N > 2147483646 olur; referans davranışı gözlenmedi. [AJAN]
- `n1`/`n2` CLI çıktısında yer almaz (CONTRACT.md istemez); iç temsil için bkz. §1.2.
- `compromise`, `criterion`, `sensitivity` modları uygulanmadı (sözleşmede bonus).
