# Ajan değerlendirmesi (10 soru)

Çıkarıcı: `rules`  |  Aile/yönlendirme doğru: 10/10  |  Parametreler doğru: 8/8  |  N ya da güç doğru (motor çıktısı bağımsız scipy ile): 8/8

| Soru | Beklenen aile | Bulunan aile | Karar | Parametre | N/güç |
|---|---|---|---|---|---|
| Önce ve sonra tansiyon ölçtüğümüz aynı hastalarda etki büyüklüğü dz=0.… | t-paired | t-paired | tool_call | True | True |
| Eşleştirilmiş t testi, tek yönlü, dz 0.3, alfa 0.05, güç 0.90 olması i… | t-paired | t-paired | tool_call | True | True |
| Tedavi öncesi ve sonrası kan basıncı ölçülen 25 hastada dz=0.6, alfa 0… | t-paired | t-paired | tool_call | True | True |
| Aynı 40 hastanın diyet öncesi ve sonrası kilosu, dz 0.4, alfa=0.01, ik… | t-paired | t-paired | tool_call | True | True |
| Eşleşmiş örneklerde etki büyüklüğü 0.8, alfa 0.05, %95 güç için örnekl… | t-paired | t-paired | tool_call | True | True |
| Önce-sonra tansiyon karşılaştırması, dz=0.25, alfa 0.05, güç 0.85, çif… | t-paired | t-paired | tool_call | True | True |
| 12 hastada ilaç öncesi ve sonrası ölçüm yaptık, dz=1.0, alfa 0.05, iki… | t-paired | t-paired | tool_call | True | True |
| Eşleştirilmiş gözlemlerde dz = 0.35, alfa = 0.025, tek yönlü, güç 0.8 … | t-paired | t-paired | tool_call | True | True |
| İlaç ve plasebo gruplarını (bağımsız iki grup) karşılaştırıyorum, d=0.… | t2-indep | t2-indep | ask_researcher | None | None |
| Üç tedavi kolunun ortalamalarını karşılaştırmak için kaç hasta gerekir… | anova-oneway | anova-oneway | ask_researcher | None | None |

MCP yolu araç çağrısı+yanıt boyutu (tahmini token ≈ karakter/4): toplam ≈ 365 token, soru başına ≈ 45.