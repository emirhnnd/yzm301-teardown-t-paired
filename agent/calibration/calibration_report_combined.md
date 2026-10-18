# Birleşik kalibrasyon (140 tahmin: 70 soru × TR/EN)

| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |
|---|---|---|---|
| [0.00, 0.75] | 7 | 0.607 | 0.857 |
| [0.75, 0.90] | 20 | 0.815 | 1.000 |
| [0.90, 0.96] | 86 | 0.930 | 1.000 |
| [0.96, 1.00] | 27 | 0.973 | 1.000 |

Genel doğruluk: 139/140 = %99.3; ECE = 0.087.
Dil: TR 69/70, EN 70/70.

Okuma: söylenen güven, doğruluğun biraz **altında** (model temkinli); güven yükseldikçe doğruluk düşmüyor. Ama setteki yanlış sayısı çok az (aşağıdaki not), bu yüzden "%90 güven → gerçekte %90" eşleşmesi istatistiksel olarak ince ayarlanamaz.
Yanlış sayısı: 1.