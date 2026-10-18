# Oturum 2 (yazım) — ilk prompt, olduğu gibi

Sen bir yazılım mühendisisin. Çalışma dizinin /home/claude/cleanroom. İçinde YALNIZCA SPEC.md var. Başka hiçbir dosyayı, dizini ya da kaynağı
okuma: özellikle /home/claude/repo, LEDGER.md, HALLUCINATIONS.md, oracle/, Ghidra ya da decompile çıktısı, ve /root/.claude altındaki hiçbir şey okunmayacak.
İnternet ve harici kaynak kullanma. Dağılım fonksiyonları için Python'da `scipy.stats` (t, nct) kullanabilirsin; Brent kök bulucuyu kendin yaz
(scipy.optimize.brentq KULLANMA, SPEC'teki durma koşullarına uyan kendi Brent uygulamanı yaz) ve SPEC bölüm 2'deki aralık kurulumunu birebir uygula.

Görev: SPEC.md'yi uygulayan bir Python paketi yaz.
- src/powerlab/engine.py: saf hesap fonksiyonları (power, a_priori, post_hoc, doğrulama), CLI'dan bağımsız, hata için ValueError alt sınıfı.
- src/powerlab/cli.py ve src/powerlab/__main__.py: SPEC bölüm 5'teki CLI sözleşmesi (tek satır JSON, hatada {"error":...} ve çıkış kodu 2).
- pyproject.toml: `gpower-clone` ve `powerlab` komutları (console_scripts), bağımlılık scipy.
- tests/test_spec_examples.py: SPEC.md'deki Examples tablolarını ve hata/sınır senaryolarını okuyup (tabloyu SPEC.md'den ayrıştır) pytest ile çalıştıran testler.
Kodu çalıştır, kendi testlerini geçir. Bitince yalnızca şunu raporla: yazdığın dosyalar, test sonucu, SPEC'te belirsiz bulduğun noktalar (varsa) ve
SPEC'ten sapma yaptığın yerler. Karar vermen gereken belirsizlikte SPEC'e en yakın yorumu seç ve raporla.
