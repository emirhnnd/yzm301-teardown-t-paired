# Ajan değerlendirmesi, LLM çıkarıcı (10 soru)

Çıkarıcı: Claude haiku alt ajanı (Jev yerine etiket kümesine kısıtlı LLM). Hesap: yalnızca MCP aracı. Sayıları LLM üretmedi, sorudaki sayıları çıkardı.

Aile/yönlendirme doğru: 10/10 | Parametreler doğru: 8/8 | N ya da güç doğru: 8/8

| Soru | Beklenen | Bulunan | Güven | Karar | Parametre | N/güç | MCP süresi (s) |
|---|---|---|---|---|---|---|---|
| Önce ve sonra tansiyon ölçtüğümüz aynı hastalarda etki büyüklüğü dz=0.… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.02 |
| Eşleştirilmiş t testi, tek yönlü, dz 0.3, alfa 0.05, güç 0.90 olması i… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.006 |
| Tedavi öncesi ve sonrası kan basıncı ölçülen 25 hastada dz=0.6, alfa 0… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.004 |
| Aynı 40 hastanın diyet öncesi ve sonrası kilosu, dz 0.4, alfa=0.01, ik… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.003 |
| Eşleşmiş örneklerde etki büyüklüğü 0.8, alfa 0.05, %95 güç için örnekl… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.006 |
| Önce-sonra tansiyon karşılaştırması, dz=0.25, alfa 0.05, güç 0.85, çif… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.006 |
| 12 hastada ilaç öncesi ve sonrası ölçüm yaptık, dz=1.0, alfa 0.05, iki… | t-paired | t-paired | 0.95 | tool_call | True | True | 0.003 |
| Eşleştirilmiş gözlemlerde dz = 0.35, alfa = 0.025, tek yönlü, güç 0.8 … | t-paired | t-paired | 0.95 | tool_call | True | True | 0.006 |
| İlaç ve plasebo gruplarını (bağımsız iki grup) karşılaştırıyorum, d=0.… | t2-indep | t2-indep | 0.95 | ask_researcher | None | None | None |
| Üç tedavi kolunun ortalamalarını karşılaştırmak için kaç hasta gerekir… | anova-oneway | anova-oneway | 0.9 | ask_researcher | None | None | None |