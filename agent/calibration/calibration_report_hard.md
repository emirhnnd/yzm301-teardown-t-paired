# Sınıflandırma kalibrasyonu ve TR/EN karşılaştırması (30 soru, zor set)

Model: hızlı bir LLM (Claude haiku) etiket kümesine kısıtlı, yalnızca etiket+güven üretir, sayı üretmez. Jev erişimi yoktu; bu yüzden Jev yerine kısıtlı LLM kullanıldı.

## Türkçe

- Etiket doğruluğu: **29/30 = %96.7**
- Otomatik karar (güven ≥ 0.75 ve desteklenen etiket): 20 soru, bunların 20 tanesi doğru
- Yanlış aileyle t-paired aracını çağırma (tehlikeli hata): **0**
- Beklenen kalibrasyon hatası (ECE, 3 kutu): 0.133

| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |
|---|---|---|---|
| [0.00, 0.75] | 3 | 0.567 | 0.667 |
| [0.75, 0.90] | 11 | 0.809 | 1.000 |
| [0.90, 1.00] | 16 | 0.900 | 1.000 |

Yanlışlar: #13 (gerçek ambiguous, tahmin unsupported, güven 0.55)

## İngilizce

- Etiket doğruluğu: **30/30 = %100.0**
- Otomatik karar (güven ≥ 0.75 ve desteklenen etiket): 20 soru, bunların 20 tanesi doğru
- Yanlış aileyle t-paired aracını çağırma (tehlikeli hata): **0**
- Beklenen kalibrasyon hatası (ECE, 3 kutu): 0.125

| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |
|---|---|---|---|
| [0.00, 0.75] | 4 | 0.637 | 1.000 |
| [0.75, 0.90] | 5 | 0.830 | 1.000 |
| [0.90, 1.00] | 21 | 0.930 | 1.000 |

Yanlışlar: yok

## Dil karşılaştırması

- TR ve EN aynı etiketi verdi: 29/30
