# MCP ve GUI yolu: token, süre, doğruluk

**Dürüst durum:** MCP yolu **ölçüldü**. GUI yolu **ölçülemedi, hesaplandı.** G\*Power taşınabilir bir `.exe`; bilgisayar kontrolü (computer use) yalnızca Başlat menüsünde kayıtlı uygulamaları açabiliyor ve G\*Power orada yoktu (`notInstalled`). Bu yüzden 10 soruyu gerçekten ekran görüntüsüyle çözen bir GUI ajanı koşturamadım. Aşağıdaki GUI sayıları gerçek ekran görüntülerinden türetilmiş tahmindir.

## MCP yolu (ölçülen)

| Ölçüt | Değer | Nasıl ölçüldü |
|---|---|---|
| Araç çağrısı + yanıt boyutu | ≈ 51 token/soru (8 hesaplanan soru için 194–211 karakter, karakter÷4) | `logs/tool_calls_llm.jsonl` |
| MCP sunucu süresi | ≈ 5,6 ms/soru (3–11 ms) | araç çağrısı süresi, aynı günlük |
| Doğruluk | 8/8 hesaplanan soruda N ya da güç G\*Power ile aynı; 10/10 yönlendirme | `agent/eval_report_llm.md` |
| Çıkarıcı alt ajanın toplam kullanımı | 69.236 token, 10 soru, ≈ 10 sn | alt ajanın raporladığı sayaç |

Son satır dikkat ister: 69k token neredeyse tamamen ajanın sabit yüküdür (sistem istemi, araç şemaları, dosyayı okuma/yazma). Sorunun kendisi ve cevabı yaklaşık 50 token. Yalın bir ajan gövdesiyle bu yük çok daha küçük olur, ama biz onu **ölçmedik**; bu satırı "MCP yolu 50 token" diye okumamak gerekir.

## GUI yolu (hesaplanan, ölçülmedi)

| Ölçüt | Değer | Dayanak |
|---|---|---|
| Bir ekran görüntüsünün token maliyeti | ortalama ≈ 486 (445–738) | senin 40 gerçek G\*Power pencere görüntün (`oracle/screenshots/`), görüntü tokenı ≈ genişlik × yükseklik ÷ 750 |
| Tam ekran görüntüsü | ≈ 1.500 civarı (tahmin) | 1920×1080'in tipik sınırı |
| Bir soru için gereken ekran görüntüsü | en az 3 (durum, alanlar dolu, sonuç) | test ailesi seçimi + 4 alan + Calculate + sonucu okuma |
| Soru başına GUI görüntü tokenı | ≈ 1.500 (3 pencere görüntüsü) ile ≈ 9.000 (6 tam ekran) arası | yukarıdaki çarpım |
| Süre | ölçülmedi | her ekran görüntüsü bir model turu; G\*Power'ın kendisi anında hesaplar |
| Doğruluk | ölçülmedi | okuma hatası ekran görüntüsü okumaktan gelir (7 hane) |

## Sonuç

Soru başına: MCP ≈ 50 token (ölçüldü), GUI ≈ 1.500–9.000 token (hesap). Yani aralık **30–180 kat**. Bu oran ödevin "bir ekran görüntüsü yüzlerce, binlerce token" varsayımıyla uyumludur ama bu **bir tahmin**, adım sayısı ve ekran boyutu varsayımına bağlıdır. Gerçek ölçüm için: G\*Power'ı Başlat menüsüne kısayolla ekleyip bilgisayar kontrolüyle 10 soruyu koşturmak ve her turun token sayacını kaydetmek gerekir.
