# MCP ve GUI yolu: token, süre, doğruluk

**Dürüst durum:** MCP yolu 10 soruda **ölçüldü**. GUI yolu gerçek G\*Power'da, bilgisayar kontrolüyle **iki koşuda ölçüldü** (22 Ekim): bir tek soruluk saf koşu ve 7 soruluk toplu koşu. 10 sorunun 8'i t-paired'dır (2'si başka test ailesi, GUI'ye girilmedi). Görüntü tokenları sayaçtan değil, piksel formülünden (genişlik × yükseklik ÷ 750) hesaplandı.

## GUI yolu (ölçülen, n = 1)

Soru: dz = 0,5, alfa = 0,05, güç = 0,80, iki yönlü, a priori. Başlangıç durumu: pencere açık, başka bir analizin sonucu ekranda.

| Ölçüt | Değer |
|---|---|
| Duvar saati süresi (ilk ekran görüntüsünden doğru sonuca) | ≈ 26 sn (model gecikmesi dahil, bu bir alt sınır değil) |
| Model turu / araç çağrısı | 5 (1 ekran görüntüsü, 1 açılır liste, 2 toplu giriş, 1 sonuç okuma) |
| Alınan görüntü | 2 tam ekran (1456×819 ≈ 1.590 token), 1 yarım ölçekli (≈ 400), 1 yakınlaştırma (≈ 150) → ≈ 3.700 görüntü tokenı |
| İlk deneme | **hatalı**: üç kez tıklama alanı seçmedi, değerler `0.50.5`, `0.050.2`, `0.80.95` olarak birleşti; ekrandaki sonuç yine de doğru görünüyordu. Ctrl+A ile ikinci denemede girdiler temiz çıktı |
| Sonuç | N = 34, kritik t = 2,0345153, ncp = 2,9154759, güç = 0,8077775, ekrandan okundu; `oracle` vektör 2 ile aynı |

Yani aynı soruda GUI ≈ **3.700+ token**, MCP ≈ **51 token**: yaklaşık **70 kat**; GUI'de bir kere girdi hatası yaşandı.

## GUI yolu, toplu koşu (ölçülen, 7 soru)

Pencerenin yeri ve alan konumları ilk koşudan bilindiği için girdiler tek `batch` çağrısında gönderildi. Bu, bir GUI ajanının alabileceği **en iyi durumdur**; tanımadığı bir arayüzde bu kadar ucuz olmaz.

| Ölçüt | Değer |
|---|---|
| Soru | 7 (a-priori 4, post-hoc 3; a-priori N ve post-hoc güç) |
| Duvar saati süresi | ≈ 54 sn toplam, ≈ 7,7 sn/soru (model gecikmesi dahil) |
| Araç çağrısı | 6 (4 toplu giriş, 2 ekran görüntüsü) |
| Alınan görüntü | 2 × 0,6 ölçekli ekran (≈ 570 token) + 8 yakınlaştırma (≈ 55 token) ≈ 1.600 token → ≈ **230 token/soru** |
| Doğruluk | **7/7 doğru**, ekrandan okunan N ya da güç `agent/eval_set.py`'deki bağımsız beklentiyle aynı (1. koşudaki soruyla birlikte 8/8) |
| Aksama | Bir yakınlaştırma karanlık geldi (uygulama gizlenirken), yeniden ekran görüntüsü gerekti |

Soru başına: MCP ≈ 51 token; GUI ≈ 230 (en iyi durum, toplu) ile ≈ 3.700 (ilk, adım adım) arası. Oran **≈ 4,5× ile ≈ 70×**. Süre: MCP ≈ 5,6 ms (sunucu), GUI ≈ 8–26 sn.

## MCP yolu (ölçülen)

| Ölçüt | Değer | Nasıl ölçüldü |
|---|---|---|
| Araç çağrısı + yanıt boyutu | ≈ 51 token/soru (8 hesaplanan soru için 194–211 karakter, karakter÷4) | `logs/tool_calls_llm.jsonl` |
| MCP sunucu süresi | ≈ 5,6 ms/soru (3–11 ms) | araç çağrısı süresi, aynı günlük |
| Doğruluk | 8/8 hesaplanan soruda N ya da güç G\*Power ile aynı; 10/10 yönlendirme | `agent/eval_report_llm.md` |
| Çıkarıcı alt ajanın toplam kullanımı | 69.236 token, 10 soru, ≈ 10 sn | alt ajanın raporladığı sayaç |

Son satır dikkat ister: 69k token neredeyse tamamen ajanın sabit yüküdür (sistem istemi, araç şemaları, dosyayı okuma/yazma). Sorunun kendisi ve cevabı yaklaşık 50 token. Yalın bir ajan gövdesiyle bu yük çok daha küçük olur, ama biz onu **ölçmedik**; bu satırı "MCP yolu 50 token" diye okumamak gerekir.

## Sonuç ve kalan belirsizlik

- Ödevin "ekran görüntüsü yüzlerce, binlerce token" varsayımı **yalnızca adım adım GUI için** doğru çıktı; sabit bir düzeni önceden bilen ve toplu giren bir GUI ajanı çok daha ucuza çözer. Yine de MCP'den ≈ 4,5 kat pahalıdır ve ekran düzeni değişirse bozulur.
- Görüntü tokenı formülden hesaplandı, sayaç yok. Süreler model gecikmesini içerir.
- GUI doğruluğu 8/8; ama örnek küçük ve tek bir kullanıcı ekranı.
- Tek koşu, tek makine; 10 soruluk eşit koşullu karşılaştırma yapılmadı (2 soru GUI'ye girilmedi).
