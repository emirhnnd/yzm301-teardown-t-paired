<div align="center">

# powerlab

### Bir istatistik programının "beynini" tersine mühendislikle çıkarıp sıfırdan yeniden yazdık

**Eşleştirilmiş t testi (`t-paired`) için örneklem büyüklüğü ve güç hesabı · CLI + MCP + Türkçe yapay zekâ ajanı**

![python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)
![tests](https://img.shields.io/badge/tests-113%20passed%20%C2%B7%201%20xfail-2ea44f)
![oracle](https://img.shields.io/badge/G%2APower%20uyumu-40%2F40-2ea44f)
![scale](https://img.shields.io/badge/%C3%B6l%C3%A7ek%20testi-560%2F560-2ea44f)
![MCP](https://img.shields.io/badge/MCP-tool-8A2BE2)

YZM301 Teardown Sprint · Grup 15 · Konu K2

[▶ Demo videosu](demo/demo.mp4) · [Şartname](SPEC.md) · [Kanıt defteri](LEDGER.md) · [Halüsinasyon günlüğü](HALLUCINATIONS.md) · [Uyum raporu](tests/CONFORMANCE.md)

</div>

---

## İçindekiler

1. [30 saniyede bu repo ne?](#1-30-saniyede-bu-repo-ne)
2. [Önce şu kavramlar (sözlük)](#2-önce-şu-kavramlar-sözlük)
3. [2 dakikada dene](#3-2-dakikada-dene)
4. [Çıktıyı nasıl okurum?](#4-çıktıyı-nasıl-okurum)
5. [Bu iş nasıl yapıldı?](#5-bu-iş-nasıl-yapıldı)
6. [Doğru olduğunu nereden biliyoruz?](#6-doğru-olduğunu-nereden-biliyoruz)
7. [MCP sunucusu ve AI ajanı](#7-mcp-sunucusu-ve-ai-ajanı)
8. [Repoda nereye bakmalıyım?](#8-repoda-nereye-bakmalıyım)
9. [Dürüstlük: neyi yapmadık / bilmiyoruz](#9-dürüstlük-neyi-yapmadık--bilmiyoruz)
10. [Atıf ve kullanılan araçlar](#10-atıf-ve-kullanılan-araçlar)

---

## 1. 30 saniyede bu repo ne?

**Sorun.** Bir araştırmacı "aynı hastalara ilaçtan önce ve sonra tansiyon ölçeceğim; **kaç hasta** lazım?" diye sorar. Bu hesabı genelde **G\*Power** adlı ücretsiz, penceresi olan bir Windows programı yapar. Ama o program kaynak koduyla gelmez, komut satırından kullanılamaz, bir yapay zekâ ajanı da onu tıklayamaz.

**Ne yaptık.**

1. Programı **kaynak koduna bakmadan**, yalnızca derlenmiş `.exe` dosyasını inceleyerek (tersine mühendislik) çözdük: hesabı nasıl yapıyor, hangi girdilere hata veriyor, sayıyı nasıl yuvarlıyor?
2. Bulduklarımızı bir **şartnameye** ([SPEC.md](SPEC.md)) yazdık.
3. Başka bir oturumda, **yalnızca o şartnameyi** okuyarak sıfırdan yeniden yazdık (temiz oda yöntemi).
4. Sonucu, G\*Power penceresinden elle aldığımız **40 gerçek sonuçla** karşılaştırdık.

**Sonuç.** Aşağıdaki gibi tek komutla çalışan, makinece okunur çıktı veren, bir yapay zekânın çağırabileceği bir araç:

```bash
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
# → {"n_total":34, ...}      yani 34 çift (hasta) gerekir
```

> **Önemli:** Bu proje G\*Power değildir ve öyle sunulmaz. Onun davranışını gözlemleyip yeniden uygulayan bağımsız bir eğitim çalışmasıdır. Kaynaklar için bkz. [Atıf](#10-atıf-ve-kullanılan-araçlar).

### Ödev katmanları

| Katman | Puan | Durum |
|---|---|---|
| Temel: CLI, SPEC, LEDGER, HALLUCINATIONS, AGENT_COST, oracle, testler | 85 | ✅ |
| MCP sunucusu | +15 | ✅ |
| AI ajanı | +10 | ✅ LLM çıkarıcı + kalibrasyon + TR/EN ölçüldü; GUI token karşılaştırması yalnızca hesap (bkz. §9) |

---

## 2. Önce şu kavramlar (sözlük)

İstatistik bilmiyorsanız bu tablo yeter; çıktıdaki her sayı burada açıklanıyor.

| Terim | Gündelik anlamı | Bu repoda |
|---|---|---|
| **Eşleştirilmiş (paired) t testi** | Aynı kişilerde iki ölçümü kıyaslama (önce/sonra) | `--test t-paired` |
| **Etki büyüklüğü `dz`** | Farkın "ne kadar büyük" olduğu. Önce-sonra farklarının ortalaması ÷ bu farkların standart sapması. 0,2 küçük, 0,5 orta, 0,8 büyük sayılır | `--dz 0.5` |
| **Alfa (α)** | "Gerçekte fark yokken yanlışlıkla fark var deme" olasılığı. Genelde 0,05 | `--alpha 0.05` |
| **Güç (power)** | "Gerçekten fark varsa onu yakalama" olasılığı. Genelde 0,80 istenir | `--power 0.80` |
| **N (çift sayısı)** | Kaç kişi/çift ölçüm | `n_total`, `--n` |
| **Tek / çift yönlü (`tails`)** | Fark tek yönde mi aranıyor (1), iki yönde mi (2) | `--tails 2` |
| **a priori** | *Çalışmadan önce*: "Bu güce ulaşmak için kaç kişi lazım?" | `--mode a-priori` → N bulur |
| **post hoc** | *Çalışmadan sonra*: "Bu N ile gücüm ne kadardı?" | `--mode post-hoc` → güç bulur |
| **Oracle (kahin)** | Doğru cevabı bildiğimiz kaynak. Burada G\*Power penceresinin gösterdiği sayılar | `oracle/` |
| **Temiz oda (clean-room)** | Yeniden yazan kişi orijinali görmez, yalnızca şartnameyi görür | §5 |

---

## 3. 2 dakikada dene

```bash
git clone https://github.com/emirhnnd/yzm301-teardown-t-paired.git
cd yzm301-teardown-t-paired
pip install -e ".[test,mcp]"       # Python 3.9+; scipy gerekir, MCP için ek paket
```

**a priori, "kaç kişi lazım?"**

```bash
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80
```
```json
{"ncp":2.9154759474226504,"critical_t":2.0345152974493383,"df":33,"n_total":34,"actual_power":0.8077775012792737}
```

**post hoc, "34 kişiyle gücüm ne?"**

```bash
gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 34
```
```json
{"ncp":2.9154759474226504,"critical_t":2.0345152974493383,"df":33,"power":0.8077775012792737}
```

**Hatalı girdi.** dz = 0 ise "fark yok" demektir, kaç kişi gerekeceği tanımsızdır:

```bash
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0 --alpha 0.05 --power 0.8
```
```json
{"error": "In an a priori analysis, the absolute value of the effect size be greater than 0.00001.", "code": "OUT_OF_RANGE", "field": "dz"}
```
Geçersiz girdide çıkış kodu **2**, iç hatada **1**'dir. Bu mesaj G\*Power'ın kendi mesajıdır (kasıtlı olarak aynı).

`powerlab` ve `python -m powerlab` aynı programdır. Bayraklar [CONTRACT.md](https://gist.github.com/seyyah/08d3e031781d853b17366be8ba264211) v1.0.0'a göredir: `--test --mode --tails --dz --alpha --power --n_total`; varsayılan yoktur, moda ait olmayan ya da bilinmeyen bayrak hatadır (`UNKNOWN_PARAM`), eksik olan `MISSING_PARAM` verir. Tek istisna `--ratio`'dur: kabul edilir ve yok sayılır (ortak test düzeneği tüm ailelere verebilir). Ayrıntı için [SPEC.md](SPEC.md) §5.

---

## 4. Çıktıyı nasıl okurum?

Çıktı tek satır JSON'dur (hem insan hem program okuyabilsin diye).

| Alan | Hangi modda | Anlamı | Örnekteki değer |
|---|---|---|---|
| `n_total` | a priori | Gereken çift sayısı | 34 |
| `actual_power` | a priori | N tam sayı olduğundan gerçekte ulaşılan güç (hedeften biraz yüksek olabilir) | 0,8077775 (hedef 0,80) |
| `power` | post hoc | Verilen N ile gücün kendisi | 0,8077775 |
| `critical_t` | ikisi de | Kritik t değeri: gözlenen t bunu aşarsa "fark var" denir | 2,0345 |
| `df` | ikisi de | Serbestlik derecesi = N − 1 | 33 |
| `ncp` | ikisi de | Merkezsel olmayan parametre = \|dz\|·√N; gücün hesabında kullanılır | 2,9155 |

Sayılar yuvarlanmadan, tam çift duyarlıkla yazılır; `n_total` ve `df` JSON tamsayısıdır. Hata durumunda `{"error": "...", "code": "...", "field": "..."}` gelir; kodlar `MISSING_PARAM`, `UNKNOWN_PARAM`, `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED`, `NO_SOLUTION`.

---

## 5. Bu iş nasıl yapıldı?

```
 ┌────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────────┐
 │ G*Power (kaynak yok)   │   │ OTURUM 1: İnceleme           │   │ OTURUM 2: Temiz oda      │
 │  • .exe dosyası        │──►│ REA + Ghidra ile ikili dosya │──►│ Yalnızca SPEC.md okunur  │
 │  • pencereden 40 sonuç │   │ çözülür                      │   │ src/ buradan yazılır     │
 └───────────┬────────────┘   │ çıktı: LEDGER.md, SPEC.md    │   └────────────┬─────────────┘
             │                └──────────────────────────────┘                │
             │      oracle/ (40 vektör + ekran görüntüleri)                    │
             └──────────────────────► DİFERANSİYEL TEST ◄─────────────────────┘
                                      "iki program aynı sayıyı veriyor mu?"
```

**Neden iki ayrı oturum?** Yeniden yazan taraf orijinal koda/çözümlemeye bakarsa şartnamenin eksiğini fark edemeyiz. Şartname yeterli değilse yeni program yanlış çıkar ve test bunu yakalar.

**Her iddia etiketli.** [LEDGER.md](LEDGER.md) her bulgunun kanıtını gösterir:

| Etiket | Anlamı |
|---|---|
| `[REA]` | İkili dosyadan, adres göstererek kanıtlandı |
| `[DOK]` | Kılavuzda yazıyor |
| `[AJAN]` | Yapay zekâ çıkarımı; testle doğrulanana dek şüpheli |
| `[KÂHİN]` | G\*Power penceresinde gözlendi |

**Yapay zekâ nerede yanıldı?** [HALLUCINATIONS.md](HALLUCINATIONS.md) 5 yanlış çıkarımı kaydeder. Örneğin ajan, arayüzde bir pencere sınıfı olan `CEff_T_PairedMeans`'i hesap motoru sandı; gerçek motor `PowerTPairedMean` çıktı.

### Kılavuzda yazmayan, ikili dosyadan çıkardığımız davranışlar

| Konu | Bulgu |
|---|---|
| Güç nasıl hesaplanır? | Merkezsel olmayan t dağılımı; df = N − 1, ncp = \|dz\|·√N, kritik değer çift yönlüde α/2'den |
| N nasıl bulunur? | Sayısal kök bulma (Brent). Aralık [2, 100] ile başlar, gerekirse ×1,6 ile genişler (adresler LEDGER'da) |
| Yuvarlama | Kesirli N önce 10 ondalığa yuvarlanır, sonra **yukarı** yuvarlanır |
| N alt sınırı | a priori'de 2 olabilir; post hoc'ta N ≥ 3 olmalı |
| Güç = alfa | Geçerli. Güç < alfa hata |
| dz = 0 | a priori'de hata (\|dz\| < 1e-5) |
| Negatif dz | N aynı çıkar; kritik t ve ncp negatif yazılır |

---

## 6. Doğru olduğunu nereden biliyoruz?

Test yöntemi **diferansiyel test**: aynı girdiyi hem G\*Power'a hem bizim programa verip çıktıları karşılaştırıyoruz.

```bash
python -m pytest -q tests      # 113 test geçer, 1 bilinen sapma xfail (≈ 2 dakika sürer)
```

| Katman | Vektör | Sonuç |
|---|---|---|
| G\*Power penceresinden elle alınan, a priori | 28 | ✅ 28/28 |
| G\*Power penceresinden elle alınan, post hoc | 9 | ✅ 9/9 |
| G\*Power hata mesajları | 3 | ✅ 3/3 |
| Ölçek testi: bağımsız scipy aramasıyla "hedefi sağlayan en küçük N" | 560 | ✅ 560/560 |
| CLI ile MCP çıktısı birebir aynı mı (gerçek MCP istemcisiyle) | 40 | ✅ 40/40 |
| Sınır değer testleri | 10 test | ✅ |

Sayılar 5e-8 hassasiyetle eşleşir (G\*Power 7 hane gösterir). Kaynak veriler [oracle/oracle_vectors.csv](oracle/oracle_vectors.csv), her satırın ekran görüntüsü `oracle/screenshots/` altında. Tam rapor: [tests/CONFORMANCE.md](tests/CONFORMANCE.md).

<details>
<summary><b>Bir test neden "kendi kendini kandırmaz"?</b></summary>

Ölçek testi, motorun kullandığı arama yöntemini kullanmaz. N = 2, 3, 4, … diye tek tek deneyip hedef gücü ilk sağlayan N'yi bulur ve motorun bulduğuyla karşılaştırır. `scipy`'nin `nct.cdf` fonksiyonu bazı (df, ncp) değerlerinde `nan` döndürdüğünden, testte bu durumda sayısal integralle hesap yapılır. Bu hata [HALLUCINATIONS.md](HALLUCINATIONS.md)'de kayıtlıdır.
</details>

---

## 7. MCP sunucusu ve AI ajanı

### MCP sunucusu (+15)

MCP, bir yapay zekânın dış araçları çağırma standardıdır. `powerlab-mcp` (stdio) tek bir araç sunar. İçinde hesap mantığı **yoktur**; yalnızca CLI'daki `powerlab.cli.compute` fonksiyonunu çağırır (bu yüzden iki yol aynı sonucu verir).

**Araç: `power_analysis_t_paired`**

| Girdi | Tür | Açıklama |
|---|---|---|
| `mode` | string | `a-priori` veya `post-hoc` |
| `tails` | int | 1 veya 2 |
| `dz` | number | etki büyüklüğü (−20 … 20) |
| `alpha` | number | (0, 1) |
| `power` | number, isteğe bağlı | a priori için hedef güç (alfa ≤ güç < 1) |
| `n_total` | int, isteğe bağlı | post hoc için çift sayısı (3 … 2147483646) |

Çıktı CLI ile aynıdır (a priori: `ncp, critical_t, df, n_total, actual_power`; post hoc: `ncp, critical_t, df, power`) ya da `{"error", "code", "field"}`.

### Türkçe AI ajanı (+10)

Araştırmacı Türkçe sorar; ajan hangi teste ait olduğunu belirler, parametreleri çıkarır ve aracı çağırır. **Rakamları ajan hesaplamaz, yalnızca MCP aracı üretir.** Emin değilse (güven < 0,75) ya da test desteklenmiyorsa **sorar**.

İki çıkarıcı var: kural tabanlı (çevrimdışı) ve LLM. Ödevin örnek verdiği hızlı karar veren Sistem 1 modeli **Jev'e erişimimiz yoktu**; ödevin izin verdiği şekilde aynı etiket kümesine kısıtlı bir LLM kullandık: **Claude haiku, alt ajan olarak ("Sistem 1" rolü)**. Model yalnızca etiket, güven ve sorudaki sayıları üretir, hesap yapmaz.

```bash
python agent/run_eval.py        # kural tabanlı → agent/eval_report.md
python agent/run_eval_llm.py    # LLM çıkarımı (agent/calibration/out_10.json) + MCP → agent/eval_report_llm.md
python agent/calibration/analyze.py easy|hard   # kalibrasyon ve TR/EN raporları
```

| Ölçüt | Kural tabanlı | LLM (haiku) |
|---|---|---|
| 10 soruluk değerlendirme seti: aile / yönlendirme | 10/10 (kurallar bu sorulara bakılarak yazıldı) | 10/10 |
| Parametreler / N ya da güç doğru | 8/8 · 8/8 | 8/8 · 8/8 |
| Yeni, kolay 40 soru (TR) etiket doğruluğu | **24/40** | 40/40 |
| Yeni, zor 30 soru (TR) etiket doğruluğu | **9/30** | 29/30 |
| Yanlış aileyle t-paired aracını çağırma | 4 vakada | 0 |

**Kalibrasyon** ("%90 güven" dediğinde gerçekte yüzde kaç doğru?), 70 soru × TR/EN = 140 tahmin, tümü LLM:

| Söylenen güven | n | ortalama söylenen | gerçek doğruluk |
|---|---|---|---|
| < 0,75 | 7 | 0,61 | 0,86 |
| 0,75–0,90 | 20 | 0,82 | 1,00 |
| 0,90–0,96 | 86 | 0,93 | 1,00 |
| ≥ 0,96 | 27 | 0,97 | 1,00 |

Genel doğruluk 139/140, ECE 0,087. Model **temkinli** (söylediğinden daha sık doğru), güven arttıkça doğruluk düşmüyor.
**Türkçe ve İngilizce:** Türkçe 69/70, İngilizce 70/70; iki dil 69/70 soruda aynı etiketi verdi. Fark bu örneklemle anlamlı değildir (tek yanlış).

Ayrıntı: `agent/calibration/`, `agent/eval_report_llm.md`, `agent/TOKEN_COMPARISON.md`.

**Token karşılaştırması:** MCP yolu **ölçüldü**: araç çağrısı+yanıt ≈ 51 token/soru, sunucu süresi ≈ 5,6 ms, 8/8 doğru. GUI yolu **ölçülemedi**: G\*Power taşınabilir `.exe` olduğundan bilgisayar kontrolü onu açamadı. GUI için gerçek ekran görüntülerinden *hesap*: pencere görüntüsü ≈ 486 token, soru başına ≥ 3 görüntü → ≈ 1.500–9.000 token, yani **tahminen 30–180 kat** (`agent/TOKEN_COMPARISON.md`).

Etiket kümesi: `t2-indep`, `t-paired`, `anova-oneway`, `chi2-contingency`, `multireg-r2`, `ambiguous`, `unsupported`.

---

## 8. Repoda nereye bakmalıyım?

**Okuma sırası önerisi:** bu README → [SPEC.md](SPEC.md) (ne yapıyor) → [LEDGER.md](LEDGER.md) (nasıl bulduk) → `src/powerlab/engine.py` (kod) → [tests/CONFORMANCE.md](tests/CONFORMANCE.md) (kanıt).

| Yol | İçerik |
|---|---|
| [`SPEC.md`](SPEC.md) | Kendi kendine yeten şartname: algoritma, doğrulama kuralları, CLI sözleşmesi, G\*Power'dan alınmış örnek tablolar |
| [`LEDGER.md`](LEDGER.md) | Kanıt defteri: her bulgu, etiketi ve ikili dosyadaki adresiyle |
| [`HALLUCINATIONS.md`](HALLUCINATIONS.md) | Yapay zekânın yanlış çıkarımları ve nasıl yakalandıkları |
| [`AGENT_COST.md`](AGENT_COST.md) | Ajan kullanımı, maliyet (tahmin olarak işaretli) ve süreç günlüğü |
| `prompts/` | İki oturumun başlangıç istemleri (neyin kime gösterildiği) |
| `oracle/` | 40 referans vektör (CSV) ve her birinin ekran görüntüsü |
| `src/powerlab/engine.py` | Hesap motoru: güç, Brent, yuvarlama, `a_priori`, `post_hoc` |
| `src/powerlab/cli.py` | Komut satırı arayüzü (`compute()` fonksiyonu ortak çekirdek) |
| `src/powerlab_mcp/server.py` | MCP adaptörü (ince katman) |
| `agent/` | Türkçe ajan, değerlendirme setleri, kalibrasyon (`calibration/`), token karşılaştırması |
| `tests/` | Diferansiyel, ölçek, sınır ve CLI↔MCP eşlik testleri |
| `demo/` | Demo videosu ve onu üreten betikler |
| `docs/` | Ekran görüntüleri (G\*Power penceresi, REA kontrolü) |

---

## 9. Dürüstlük: neyi yapmadık / bilmiyoruz

- **Kalibrasyon seti benim yazdığım sorulardır.** Sorular ve beklenen etiketler Claude tarafından yazıldı, etiketleyen model de Claude; yanlılık ortak olabilir. Kolay sette tavan etkisi var (%100) ve 140 tahminde yalnızca 1 yanlış var, bu yüzden kalibrasyon eğrisi istatistiksel olarak zayıf.
- **Kural tabanlı çıkarıcı genelleştirmiyor.** 10 soruya bakılarak yazıldığı için orada 10/10, yeni sorularda 24/40 ve 9/30; yanlış aileyle araç çağırdığı vakalar var. LLM çıkarıcı bunu düzeltiyor, güvenilecek olan odur.
- **Jev erişimi yoktu; Claude haiku kullanıldı** ve bu, alt ajan olarak çalıştı (`ANTHROPIC_API_KEY` ile programdan doğrudan çağıran `extract_llm` yolu hâlâ ölçülmedi).
- **GUI token karşılaştırması ölçüm değil, hesaptır.** G\*Power Başlat menüsünde kayıtlı olmadığı için gerçek bir GUI ajanı koşturulamadı; GUI süresi ve GUI doğruluğu ölçülmedi. MCP tarafı ölçüldü (bkz. `agent/TOKEN_COMPARISON.md`).
- **Demo videosu ekran kaydı değildir.** `demo/make_video.py` gerçek motoru ve gerçek komutları çalıştırıp sonuçlarını sahnelere çizer (40 vektörün yan yana tablosu dahil); çıktılar uydurma değildir, betik yeniden üretir. Videoda ses yoktur; sahne etiketleri ve altyazı satırları vardır.
- **Kenar vektörleri (22 Ekim, `oracle/oracle_boundary.csv`, hepsi tek yönlü):** dz = 0.001 (N = 6182559), dz = 20 (güç 1), dz = 21 (hata `Effect size d is outside the admissible range (-20, 20).`) ve alfa = 0.2 G\*Power ile birebir eşleşti. **Bir bilinen sapma:** dz = 0.00001 için G\*Power N = 61823520102 verir (gerçek güç 0.7999842, hedefin altında; çok büyük df'de kendi sayısal sınırı), klon matematiksel kökü 61825572322 verir. Test xfail olarak işaretli; nedeni REA ile incelenmedi. Alfa/güç için kesin geçerlilik aralıkları yine denenmedi (`[AJAN]`, SPEC §8).
- **n1 / n2.** İç temsil `[REA]` ile kanıtlandı: motor eşleştirilmiş testte `n1 = n2 = N/2` tutar, toplam `N = n1 + n2` (LEDGER 12, 29; adresler 0x4bdee0, 0x4d38b0, 0x5cac90, 0x5cac94). Sözleşme eşleştirilmiş test için `n1`/`n2` istemediğinden CLI bunları yazmaz; bilgi yalnızca kanıt kaydıdır (LEDGER 30).
- **Sözleşme (CONTRACT.md v1.0.0) uygulandı.** Bonus modlar `compromise`, `criterion`, `sensitivity` yok (`UNSUPPORTED` döner). Çok büyük N yalnızca yukarıdaki dz = 1e-5 noktasında G\*Power'dan ayrışıyor.
- **SPEC'te olmayan iki ekleme var.** Motordaki `scipy.stats.nct.cdf` nan yedeği (HALLUCINATIONS #5) ve CLI'daki `--ratio` argümanı SPEC'te yazmıyor. İkisi de oracle sonuçlarını değiştirmez, ama motor bu iki noktada saf SPEC çıktısı değildir.
- **Popülasyon düzeltmesi** (ikili dosyada bir alan var) arayüzden erişilebilir mi bilinmiyor; uygulanmadı.

---

## 10. Atıf ve kullanılan araçlar

Bu yazılım, güç analizi aracının davranışını **gözlem ve statik inceleme** ile yeniden uygulayan bağımsız bir eğitim çalışmasıdır. O yazılım değildir ve onun gibi sunulmaz. İkili dosya ve decompile çıktıları repoda **yoktur** (`.gitignore`).

| | |
|---|---|
| İncelenen ikili | `GPowerNT.exe`, sürüm 3.1.9.7 (Windows, x86) |
| SHA-256 | `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812` |
| Araçlar | REA 6.5.0 (`rea-agents`), Ghidra 12.1.4, JDK 21 |

REA ve Ghidra sağlayıcısının kullanılabilirlik kontrolü:

![REA ve Ghidra kontrolü](docs/rea_kontrol.png)

Kaynaklar:

- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G\*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G\*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.
