# Sınıflandırma kalibrasyonu ve TR/EN karşılaştırması (40 soru, kolay set)

Model: hızlı bir LLM (Claude haiku) etiket kümesine kısıtlı, yalnızca etiket+güven üretir, sayı üretmez. Jev erişimi yoktu; bu yüzden Jev yerine kısıtlı LLM kullanıldı.

## Türkçe

- Etiket doğruluğu: **40/40 = %100.0**
- Otomatik karar (güven ≥ 0.75 ve desteklenen etiket): 34 soru, bunların 34 tanesi doğru
- Yanlış aileyle t-paired aracını çağırma (tehlikeli hata): **0**
- Beklenen kalibrasyon hatası (ECE, 3 kutu): 0.063

| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |
|---|---|---|---|
| [0.75, 0.90] | 2 | 0.800 | 1.000 |
| [0.90, 1.00] | 38 | 0.944 | 1.000 |

Yanlışlar: yok

## İngilizce

- Etiket doğruluğu: **40/40 = %100.0**
- Otomatik karar (güven ≥ 0.75 ve desteklenen etiket): 34 soru, bunların 34 tanesi doğru
- Yanlış aileyle t-paired aracını çağırma (tehlikeli hata): **0**
- Beklenen kalibrasyon hatası (ECE, 3 kutu): 0.047

| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |
|---|---|---|---|
| [0.75, 0.90] | 2 | 0.825 | 1.000 |
| [0.90, 1.00] | 38 | 0.960 | 1.000 |

Yanlışlar: yok

## Dil karşılaştırması

- TR ve EN aynı etiketi verdi: 40/40
