# Kalibrasyon ve dil karşılaştırması

- `make_set.py`, `make_hard.py`: 40 kolay + 30 zor soru (TR) ve İngilizce çevirileri; `truth*.json` beklenen etiketler.
- Ajanlara yalnızca soru dosyaları (etiketsiz) verildi; her dil için ayrı alt ajan (Claude haiku), hızlı karar veren Sistem 1 modeli olarak (Jev erişimi yok).
- `out*_tr.json`, `out*_en.json`: ham model çıktıları. `analyze.py [easy|hard]` raporları üretir: `calibration_report*.md`, `calibration_report_combined.md`.
- `out_10.json`: 10 soruluk değerlendirme setinde LLM çıkarımı (aile + parametre); `agent/run_eval_llm.py` bunu MCP üzerinden koşturur.

**Sınırlar:** Sorular ve beklenen etiketler Claude tarafından yazıldı, etiketleyen model de Claude; yanlılık ortak olabilir. Kolay sette tavan etkisi var (%100). Tek bir yanlış (zor set, TR #13) olduğundan kalibrasyon eğrisi istatistiksel olarak zayıftır.
