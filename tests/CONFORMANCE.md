# Uyum raporu (diferansiyel test)

Komut: `python -m pytest -q tests` → **113 test geçti, 1 xfail (bilinen sapma)** (tarih 2026-10-22, CONTRACT.md v1.0.0 sonrası).

| Katman | Vektör | Sonuç |
|---|---|---|
| G\*Power arayüz vektörleri (oracle/) — a priori | 28 | N, df tam; güç/kritik/ncp 5e-8 içinde: **28/28** |
| G\*Power arayüz vektörleri — post hoc | 9 | df tam; güç/kritik/ncp 5e-8 içinde: **9/9** |
| G\*Power hata vektörleri | 3 | hata JSON'u (error, code, field) + çıkış kodu 2 + mesaj parçası: **3/3** |
| Ölçek (bağımsız scipy kaba kuvvet "hedefi sağlayan en küçük N") | 560 | N eşleşmesi **560/560 (%100)** |
| CLI ↔ MCP eşliği (gerçek stdio MCP istemcisi) | 40 | çıktılar birebir aynı: **40/40** |
| Sınır testleri | 10 test | geçti |
| Sınır vektörleri (oracle/oracle_boundary.csv, 22 Ekim) | 5 | 4 tam eşleşme, 1 bilinen sapma (dz = 1e-5, xfail) |

## Açıklanan farklar (bulgular)

1. **Kesirli N ve yukarı yuvarlama.** `pwr`/`statsmodels` gibi kütüphaneler kesirli N* verir. G\*Power N* değerini bulur, 10 ondalığa yuvarlar, sonra yukarı yuvarlar (LEDGER 17–21). Aşağıdaki tabloda her satırda `güç(N−1) < hedef ≤ gerçek güç(N)` sağlanır.
2. **N alt sınırı 2.** Güç hedefi N=2'deki güce eşit/altındaysa N* alt sınırın altına düşer ve G\*Power N=2 verir (vektör 19, 20, 21, 26). Post hoc modda N=2 girişi ise hata verir (LEDGER 22, 25).
3. **`scipy.stats.nct.cdf` bazı (df, ncp) çiftlerinde `nan` döndürür** (ör. df=130, ncp≈5,7, α=0,001). Hem testteki referans kodda hem de temiz oda motorunun ilk sürümünde ortaya çıktı (HALLUCINATIONS #5). Motor `sf` ve 0'a düşme yedekleri, test referansı ise bağımsız bir sayısal integral kullanır.
4. **10 ondalık yuvarlaması** yalnızca N*, bir tamsayının ≤ 5e-11 üstündeyse fark yaratır (`tests/test_boundary.py::test_n_star_just_above_integer` birim düzeyinde sınar; GUI'de böyle bir vektör bulunamadı).

## Kesirli N* ile G\*Power N karşılaştırması (a priori vektörleri)

| vektör | dz | α | güç | tails | kesirli N* (kütüphane) | G*Power N | güç(N−1) | gerçek güç(N) |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.5 | 0.05 | 0.95 | 2 | 53.9406 | 54 | 0.946527 | 0.9502120 |
| 2 | 0.5 | 0.05 | 0.8 | 2 | 33.3671 | 34 | 0.795366 | 0.8077775 |
| 3 | 0.5 | 0.05 | 0.8 | 1 | 26.1375 | 27 | 0.798054 | 0.8118316 |
| 4 | 0.5 | 0.05 | 0.95 | 1 | 44.6800 | 45 | 0.947266 | 0.9512400 |
| 5 | 0.2 | 0.05 | 0.8 | 2 | 198.1508 | 199 | 0.799698 | 0.8016910 |
| 6 | 0.8 | 0.05 | 0.8 | 2 | 14.3028 | 15 | 0.790088 | 0.8213105 |
| 7 | 0.3 | 0.05 | 0.9 | 2 | 118.6865 | 119 | 0.898315 | 0.9007612 |
| 8 | 0.5 | 0.01 | 0.8 | 2 | 50.0647 | 51 | 0.799337 | 0.8093892 |
| 9 | 0.5 | 0.01 | 0.95 | 2 | 74.6109 | 75 | 0.948102 | 0.9511756 |
| 10 | 0.5 | 0.01 | 0.8 | 1 | 42.8913 | 43 | 0.789952 | 0.8011974 |
| 11 | 0.5 | 0.1 | 0.8 | 2 | 26.1362 | 27 | 0.798072 | 0.8118463 |
| 12 | 1.0 | 0.05 | 0.8 | 2 | 9.9378 | 10 | 0.748017 | 0.8030969 |
| 13 | 1.0 | 0.05 | 0.99 | 2 | 20.4239 | 21 | 0.988591 | 0.9916492 |
| 14 | 0.1 | 0.05 | 0.8 | 2 | 786.8089 | 787 | 0.799595 | 0.8000954 |
| 15 | 0.05 | 0.05 | 0.8 | 2 | 3141.4655 | 3142 | 0.799942 | 0.8000668 |
| 16 | 2.0 | 0.05 | 0.8 | 2 | 4.2207 | 5 | 0.754984 | 0.9088849 |
| 17 | 3.0 | 0.05 | 0.95 | 2 | 3.8234 | 4 | 0.745268 | 0.9670006 |
| 18 | 5.0 | 0.05 | 0.95 | 2 | 2.8526 | 3 | 0.420961 | 0.9754623 |
| 19 | 0.5 | 0.05 | 0.06 | 2 | (N=2 alt sınır) | 2 | nan | 0.0619486 |
| 20 | 0.5 | 0.05 | 0.051 | 2 | (N=2 alt sınır) | 2 | nan | 0.0619486 |
| 21 | 0.5 | 0.05 | 0.051 | 1 | (N=2 alt sınır) | 2 | nan | 0.1058229 |
| 22 | 0.5 | 0.05 | 0.99 | 2 | 75.4457 | 76 | 0.989648 | 0.9904221 |
| 23 | 0.5 | 0.05 | 0.999 | 2 | 103.9687 | 104 | 0.998916 | 0.9990026 |
| 24 | 0.5 | 0.001 | 0.8 | 2 | 73.7012 | 74 | 0.794002 | 0.8025148 |
| 25 | 0.01 | 0.05 | 0.8 | 2 | 78490.5258 | 78491 | 0.799997 | 0.8000024 |
| 26 | 0.5 | 0.05 | 0.05 | 2 | (N=2 alt sınır) | 2 | nan | 0.0619486 |
| 29 | -0.5 | 0.05 | 0.8 | 1 | 26.1375 | 27 | 0.798054 | 0.8118316 |
| 30 | -0.5 | 0.05 | 0.8 | 2 | 33.3671 | 34 | 0.795366 | 0.8077775 |
