# AGENT_COST.md — ajan, maliyet ve süreç günlüğü

| Oturum | Ajan / model | Rol | Yaklaşık girdi+çıktı token | Yaklaşık maliyet | Yineleme |
|---|---|---|---|---|---|
| 1 (inceleme) | Claude (Sonnet 5.5) + REA 6.5.0 + Ghidra 12.1.4 | İkili inceleme, LEDGER/HALLUCINATIONS/SPEC üretimi | ≈ 1,5–2 M (bağlam sıkıştırması dahil; ölçülen sayaç yok, tahmin) | tahmini ≈ 6–10 USD | 3 bağlam penceresi, ≈ 120 araç çağrısı |
| 2 (yazım) | Claude alt ajanı, yalnızca SPEC.md ile | Temiz oda yeniden yazım | tahmin: 0,1–0,3 M | tahmini ≈ 0,5–1,5 USD | 1 tur + düzeltmeler |
| Ajan ölçümleri | 4 Claude haiku alt ajanı (TR/EN sınıflandırma ×2 set, 10 soru çıkarımı) | LLM çıkarıcı, kalibrasyon | alt ajan sayaçları: ≈ 70.000 token/ajan (çoğu sabit yük), toplam ≈ 0,5 M | ≈ 0,3–0,5 USD (tahmin) | 1 tur |
| Test ve MCP | Claude (aynı oturum 1 bağlamı) | Diferansiyel test, MCP adaptörü, ajan | tahmin: 0,3 M | tahmini ≈ 1–2 USD | birkaç tur |

Not: Kesin token/maliyet sayacı bu ortamda ajana açık değildi; yukarıdaki değerler **tahmindir** (en dürüst ifade budur) ve oturum günlüklerinden doğrulanmamıştır.

## Süreç özeti

1. REA kurulumu: `GHIDRA_INSTALL_DIR` ortam değişkeni Claude masaüstü yapılandırmasına yazılana kadar Ghidra sağlayıcısı kullanılamadı (≈ 3 tur kayıp).
2. Kâhin vektörleri insan eliyle (GUI) toplandı: 40 vektör, ekran görüntüleri `oracle/screenshots/`. İlk ekran görüntüleri yalnızca grafiği gösteriyordu; tam pencere istemek 1 tur kaybettirdi.
3. İnceleme sırası: sınıf adı → sanal tablo → güç fonksiyonu → df/ncp → çözücü (yuva 18) → yuvarlama → doğrulama dizeleri.
4. Hata ayıklama döngüsü: iki yanlış çıkarım (HALLUCINATIONS #1, #2), sonra çözücü yuva karışıklığı (#3).

## Neyi farklı yapardım

- Ghidra ortamını (env) ilk dakikada doğrulamak; "araç var mı" kontrolünü ekran görüntüsüyle README'ye koymak.
- Kâhin vektör listesini inceleme başlamadan önce hazırlayıp hata mesajlarını baştan toplatmak.
- Tek bağlamda uzun inceleme yerine, her bulguyu hemen LEDGER'a yazmak (bağlam sıkıştırması sırasında ayrıntı kaybı olmadı, ama risk vardı).
- 500+ vektörlük ölçek testini SPEC'ten önce çalıştırıp sınır vektörlerini oradan seçmek.
