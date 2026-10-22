# MCP ve GUI yolu: token, süre, doğruluk

**Dürüst durum:** MCP yolu 10 soruda **ölçüldü**. GUI yolu **1 soruda ölçüldü** (22 Ekim, 19:11): bilgisayar kontrolüyle gerçek G\*Power penceresinde tek bir a-priori analiz çözüldü. 10 soruluk GUI koşusu yapılmadı. Ölçüm n = 1'dir ve genelleme taşımaz. Görüntü tokenları sayaçtan değil, piksel formülünden (genişlik × yükseklik ÷ 750) hesaplandı.

## GUI yolu (ölçülen, n = 1)

Soru: dz = 0,5, alfa = 0,05, güç = 0,80, iki yönlü, a priori. Başlangıç durumu: pencere açık, başka bir analizin sonucu ekranda.

| Ölçüt | Değer |
|---|---|
| Duvar saati süresi (ilk ekran görüntüsünden doğru sonuca) | ≈ 26 sn (model gecikmesi dahil, bu bir alt sınır değil) |
| Model turu / araç çağrısı | 5 (1 ekran görüntüsü, 1 açılır liste, 2 toplu giriş, 1 sonuç okuma) |
| Alınan görüntü | 2 tam ekran (1456×819 ≈ 1.590 token), 1 yarım ölçekli (≈ 400), 1 yakınlaştırma (≈ 150) → ≈ 3.700 görüntü tokenı |
| İlk deneme | **hatalı**: üç kez tıklama alanı seçmedi, değerler `0.50.5`, `0.050.2`, `0.80.95` olarak birleşti; ekrandaki sonuç yine de doğru görünüyordu. Ctrl+A ile ikinci denemede girdiler temiz çıktı |
| Sonuç | N = 34, kritik t = 2,0345153, ncp = 2,9154759, güç = 0,8077775, ekrandan okundu; `oracle` vektör 2 ile aynı |

Yani aynı soruda GUI ≈ **3.700+ token**, MCP ≈ **51 token**: yaklaşık **70 kat**, ve GUI'de bir kere girdi hatası yaşandı (okuma sonucu doğru kalsa da girdiler bozuktu, bu bir ajanın fark etmeyebileceği bir hatadır).

## MCP yolu (ölçülen)

| Ölçüt | Değer | Nasıl ölçüldü |
|---|---|---|
| Araç çağrısı + yanıt boyutu | ≈ 51 token/soru (8 hesaplanan soru için 194–211 karakter, karakter÷4) | `logs/tool_calls_llm.jsonl` |
| MCP sunucu süresi | ≈ 5,6 ms/soru (3–11 ms) | araç çağrısı süresi, aynı günlük |
| Doğruluk | 8/8 hesaplanan soruda N ya da güç G\*Power ile aynı; 10/10 yönlendirme | `agent/eval_report_llm.md` |
| Çıkarıcı alt ajanın toplam kullanımı | 69.236 token, 10 soru, ≈ 10 sn | alt ajanın raporladığı sayaç |

Son satır dikkat ister: 69k token neredeyse tamamen ajanın sabit yüküdür (sistem istemi, araç şemaları, dosyayı okuma/yazma). Sorunun kendisi ve cevabı yaklaşık 50 token. Yalın bir ajan gövdesiyle bu yük çok daha küçük olur, ama biz onu **ölçmedik**; bu satırı "MCP yolu 50 token" diye okumamak gerekir.

## Kalan belirsizlik

- GUI ölçümü tek soru ve tek koşu; süre, model gecikmesi ve ekran boyutuna göre değişir.
- Görüntü tokenı formülden hesaplandı, sayaçtan değil.
- 10 soruluk GUI karşılaştırması ve GUI doğruluk oranı ölçülmedi.
- Aralık tahmini (önceki sürümde 1.500–9.000 token/soru) bu ölçümle uyumlu: 3 görüntülük akışta ≈ 3.700.
