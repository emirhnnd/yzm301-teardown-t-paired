# Oturum 1 (inceleme): ilk prompt

Aşağıdaki metin, oturuma yapıştırılan ödev duyurusudur (olduğu gibi). Öğrencinin bu metnin altına yazdığı kendi isteği özetle şuydu:
grup 15, konu K2 = t testi, eşleştirilmiş ortalama (`t-paired`); modlar a priori ve post hoc; G*Power 3.1.9.7'yi REA + Ghidra ile incele,
kanıt defteri ve SPEC.md üret; bu oturumda kod yazma.

Not: öğrencinin kendi cümleleri birebir kayıtlı değildir; oturum bağlam sınırına ulaştığı için özetle devam etmiştir. Aşağıdaki duyuru metni birebirdir.

Öğrencinin konu seçimi (kendi ifadesiyle, birebir):

> K2 2) t testi, eşleştirilmiş ortalama (önce ve sonra tansiyon)

Diğer cümleleri kayıtlı değildir.

---

G*Power, klinik araştırmacıların "kaç denek gerekir?" sorusunu yanıtladığı ücretsiz bir araç. Ama yalnızca grafik arayüzü var; ne CLI'si ne API'si var. Bir AI ajanı onu ancak ekran görüntüsü alıp tıklayarak kullanabiliyor ve bu her çağrıda çok token demek.

Bu sprintte G*Power'ın bir hesabını REA ile tersine mühendislikle inceleyecek, kanıtlarıyla belgeleyecek, temiz odada yeniden yazacak ve ajan çağına taşıyacaksınız: önce CLI, isterseniz MCP ve AI ajanı.

Soru: "Ajanın söktüğü şeyin DOĞRU olduğunu nasıl kanıtlarsın?"

TAKIM: En fazla 4 kişi; bireysel çalışma da serbest. Her takım tek bir test ailesi üzerinde çalışır.

PUANLAMA
- Temel (CLI): 85 puan. Kapı: gizli vektörlerde N en az %90 oranında tam eşleşmeli. Tutmazsa bonus açılmaz.
- +15 MCP sunucusu: 100 puan
- +10 AI ajanı (MCP üzerinden, doğal dilde): 110 puan

TEMEL KURALLAR
1. Puan yalnızca [REA] etiketli kanıtlara verilir. Kılavuzda yazanı değil, kılavuzda OLMAYAN davranışı bulun.
2. İki ayrı ajan oturumu: biri inceler, diğeri yalnızca SPEC.md ile yazar.
3. Hesap mantığı tek motordadır. CLI, MCP ve ajan bu motoru çağıran ince katmanlardır.
4. Teslim edilen kodda decompile çıktısı olmaz. GPower.exe repoya konmaz.

TESLİM: GitHub repo linki

Ayrıntılı yönerge, CLI sözleşmesi ve etik kurallar ekteki dosyada. Ders slaytları ders klasöründe.
