# HALLUCINATIONS.md — ajanın yanlış çıkardıkları

## 1. Arayüz sınıfını hesap motoru sanmak
- **Ajanın çıkarımı:** `CEff_T_PairedMeans` eşleştirilmiş t testinin hesap motorudur.
- **Dayanak:** Ad dizesi aramasında "PairedMeans" geçen tek sınıf buydu.
- **Nasıl fark edildi:** Üretici fonksiyon (0x52e5f0) decompile edilince 7 `CEdit` alt denetimi ve pencere kurucuları çıktı: bu bir iletişim kutusu.
- **Yakalayan:** Fonksiyon gövdesinin doğrudan incelenmesi. Doğrusu `PowerTPairedMean` (sanal tablo 0x5cac60).

## 2. RTTI adresinden sanal tablo adresi tahmin etmek
- **Ajanın çıkarımı:** Tür tanımlayıcısına başvuran yapıdan sanal tabloya `0x5ef6d0` üzerinden gidilir.
- **Dayanak:** MSVC RTTI düzeninin hatırlanan ofsetleri.
- **Nasıl fark edildi:** `0x5ef6d0` için xref sorgusu boş döndü.
- **Yakalayan:** Boş xref sonucu. Doğru adres ada göre sorguyla bulundu (0x5cac60).

## 3. "Çözücü giriş yuvası N'yi çözer" varsayımı
- **Ajanın çıkarımı:** Sanal tablodaki Brent'i çağıran ilk işlev (0x4960b0, yuva 14) N çözücüdür (kısa, 300 yinelemeli, mod 3).
- **Dayanak:** Brent çağrısı ve "300" sabiti, N aramasına benziyordu.
- **Nasıl fark edildi:** İşlev sonucunu [+0xb0] alanına (alfa) yazıyor ve mod 3 amaç fonksiyonu (0x4d37f0) ikinci argümanı (alfa) değiştiriyor. Bu **alfa çözücü**. Gerçek N çözücü yuva 18 (0x496aa0), mod 0, sonucu [+0xe8]'e yazıyor.
- **Yakalayan:** Alan ofseti ve mod numarası eşleşmesi; ayrıca oracle vektörlerinde N'nin tamsayıya yuvarlandığı (alfa çözücüde böyle bir yuvarlama yok) gözlemi.

## 4. Eşit güçte ceil'in "gerçek güç ≥ hedef" garantisini vermesi beklentisi
- **Ajanın çıkarımı:** G\*Power N'yi doğrudan ⌈N\*⌉ ile bulur, bu nedenle scipy'daki "hedefi sağlayan en küçük N" ile aynıdır.
- **Dayanak:** Satır 23'teki ilk 9 vektör.
- **Nasıl fark edildi:** Binary'de yuvarlamanın ham ⌈N\*⌉ değil, önce 10 ondalığa yuvarlama (0x496a20) olduğu görüldü. N\* tam bir tamsayının 5e-11 üstündeyse G\*Power o tamsayıyı seçer, saf "en küçük N" ise bir sonrakini seçerdi.
- **Yakalayan:** Rounding işlevinin incelenmesi; sınır testi `tests/test_boundary.py::test_n_star_just_above_integer`.

## 5. "scipy.stats.nct.cdf güvenilir bir referanstır"
- **Çıkarım (iki yerde):** Testlerdeki bağımsız referans ve temiz oda motoru `1 − nct.cdf(c) + nct.cdf(−c)` formülünü doğrudan kullanır.
- **Nasıl fark edildi:** 560 vektörlük ölçek testi ilk koşuda %94,8 uyum verdi; uyuşmayanlar hep α=0,001 satırlarıydı. `nct.cdf(c, 130, 5.7)` `nan` döndürüyordu.
- **Yakalayan:** Ölçek testi (`tests/test_scale_scipy.py`). Doğru değer, ki-kare üzerinden bağımsız sayısal integralle ayrıca doğrulandı (1e-13 içinde); motor `nan` durumunda `sf` yedeğini kullanıyor. Temiz oda ajanı sorunu kendi testlerinde de yakalayıp raporladı.
