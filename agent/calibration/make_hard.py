"""Zor set (30 soru, TR+EN): yanıltıcı anahtar kelimeler, günlük dil, eksik bilgi. Aynı dosya biçimi, ayrı dosyalar."""
import json, pathlib
here = pathlib.Path(__file__).resolve().parent
S = [
("t-paired","Hastaları iki gruba ayırmadık; herkesi tedaviden önce ve sonra ölçtük, farka bakacağız. dz=0.5, güç 0.8, kaç kişi?","We did not split patients into two groups; we measured everyone before and after treatment and will look at the difference. dz=0.5, power 0.8, how many people?"),
("t2-indep","Eşleştirme yapmadan, rastgele atanmış iki kolun (tedavi / kontrol) önce-sonra fark skorlarını karşılaştıracağız, d=0.5, güç 0.8.","Without matching, we will compare the pre-post change scores of two randomly assigned arms (treatment / control), d=0.5, power 0.8."),
("t-paired","Çiftler halinde eşlenmiş 25 hasta-sağlıklı kardeş ikilisinde enzim düzeyi farkı, dz=0.6, güç nedir?","Enzyme level difference in 25 matched patient-healthy sibling pairs, dz=0.6, what is the power?"),
("t2-indep","Hasta grubu ve sağlıklı gönüllüler (ayrı kişiler) arasında kan düzeyi farkı, d=0.7, kaç kişi?","Blood level difference between a patient group and healthy volunteers (separate people), d=0.7, how many people?"),
("anova-oneway","Plasebo, düşük doz ve yüksek doz kolları arasında ortalama farkı var mı? f=0.3, güç 0.8.","Is there a mean difference among the placebo, low-dose and high-dose arms? f=0.3, power 0.8."),
("anova-oneway","Dört farklı kliniğin hasta memnuniyet ortalamalarını kıyaslamak istiyoruz, f=0.25.","We want to compare mean patient satisfaction across four different clinics, f=0.25."),
("t-paired","Aynı hastalara iki farklı ilacı sırayla verdiğimiz çapraz (crossover) bir çalışmada ilaçlar arasındaki ortalama fark, dz=0.4, kaç hasta?","In a crossover study where the same patients receive two different drugs in sequence, the mean difference between drugs, dz=0.4, how many patients?"),
("chi2-contingency","Hastalık var/yok ile genotip (AA, Aa, aa) arasında ilişki var mı, w=0.25, güç 0.8?","Is there an association between disease present/absent and genotype (AA, Aa, aa), w=0.25, power 0.8?"),
("multireg-r2","Sekiz değişkenle depresyon skorunu açıklayan modelin toplam açıklama gücü (R²) için kaç kişi toplamalıyım, f²=0.1?","How many people must I collect for the overall explanatory power (R²) of a model explaining depression score with eight variables, f²=0.1?"),
("unsupported","İki tedavi arasında hayatta kalma eğrilerini kıyaslayan Cox regresyonu için güç hesabı lazım.","I need a power calculation for a Cox regression comparing survival curves between two treatments."),
("unsupported","Ağrı skorları ordinal, Wilcoxon işaretli sıra testi için kaç hasta gerekir?","Pain scores are ordinal; how many patients are needed for the Wilcoxon signed-rank test?"),
("unsupported","Bir tanı testinin duyarlılığını %90'dan %95'e çıkarıp çıkarmadığını sınamak için örneklem büyüklüğü?","Sample size for testing whether a diagnostic test's sensitivity improved from 90% to 95%?"),
("ambiguous","Önce ve sonra ölçtük ama bir kontrol grubumuz da var; hangi testi seçmeliyim, güç 0.8, kaç kişi?","We measured before and after but we also have a control group; which test should I choose, power 0.8, how many people?"),
("ambiguous","Gruplar arasında fark var mı bakmak istiyorum, etki orta büyüklükte, güç 0.8.","I want to see whether there is a difference between groups, medium effect size, power 0.8."),
("ambiguous","Bu ilacın etkisi var mı? Hasta sayısını bilmiyorum, bana ne gerektiğini söyle.","Does this drug have an effect? I do not know the number of patients, tell me what is needed."),
("t2-indep","Ameliyat olan ve olmayan hastaların ağrı skoru ortalaması arasındaki fark, 30'ar kişi, d=0.6; güç ne?","Difference in mean pain score between patients who had surgery and those who did not, 30 each, d=0.6; what is the power?"),
("t-paired","Her hastanın iki koldaki tansiyonunu ölçtük (sol-sağ), farkın sıfırdan farklı olup olmadığı, dz=0.3, kaç hasta?","We measured each patient's blood pressure in both arms (left-right); whether the difference is non-zero, dz=0.3, how many patients?"),
("anova-oneway","Üç kol arasında önce-sonra değil, yalnızca son ölçümlerin ortalaması karşılaştırılacak, f=0.4, kol başına kaç kişi?","Across three arms, only final measurement means (not pre-post) will be compared, f=0.4, how many per arm?"),
("chi2-contingency","Doğum yöntemi (normal/sezaryen) ile bebek sarılığı (var/yok) bağımlılığı, w=0.2, 300 kişi, güç?","Dependence between delivery method (vaginal/cesarean) and neonatal jaundice (yes/no), w=0.2, 300 people, power?"),
("multireg-r2","Yaş ve cinsiyet kontrol edildikten sonra stresin eklenmesiyle R²'nin artıp artmadığı, f²=0.05 (sıralı regresyon).","Whether R² increases when stress is added after controlling for age and sex, f²=0.05 (hierarchical regression)."),
("unsupported","Ortalama ile standart sapmanın kendisinin bir tahminini hesaplamak istiyorum, güven aralığı genişliği 2 olsun.","I want an estimate with a confidence interval width of 2 for a mean; how large a sample?"),
("t2-indep","Aynı gün iki ayrı hastanede doğan bebeklerin doğum ağırlığı ortalaması farklı mı, d=0.3, kaç bebek?","Is mean birth weight different for babies born the same day in two separate hospitals, d=0.3, how many babies?"),
("t-paired","Kocalar ve eşlerinin (evli çiftler) memnuniyet puanları arasındaki fark, 50 çift, dz=0.25, alfa 0.05 güç?","Difference in satisfaction scores between husbands and their wives (married couples), 50 couples, dz=0.25, alpha 0.05, power?"),
("anova-oneway","Dört farklı ilaç markasının etken madde miktarı ortalamaları aynı mı, f=0.35, her marka için kaç örnek?","Are the active ingredient means of four different drug brands the same, f=0.35, how many samples per brand?"),
("ambiguous","Karşılaştırma yapacağız. Etki büyüklüğünü 0.5 varsayalım.","We will make a comparison. Let us assume an effect size of 0.5."),
("unsupported","Doz-yanıt eğrisinin eğimini (lojistik regresyon, ikili sonuç) test etmek için kaç hasta?","How many patients to test the slope of a dose-response curve (logistic regression, binary outcome)?"),
("chi2-contingency","İki oran karşılaştırması: tedavide iyileşme %60, plasebo %40; bunu ki-kare olumsallık tablosuyla sınayacağız, w=0.2, güç 0.8.","Comparison of two proportions: improvement 60% on treatment vs 40% on placebo; we will test with a chi-square contingency table, w=0.2, power 0.8."),
("t-paired","Şampuan uygulanan saçın bir yarısı ile uygulanmayan diğer yarısı arasındaki kırılma farkı (aynı kişi), dz=0.5.","Breakage difference between the half of the hair treated with shampoo and the untreated other half (same person), dz=0.5."),
("multireg-r2","Dört yordayıcılı regresyon modelinin gücü: 80 kişi, f²=0.15, alfa 0.05.","Power of a four-predictor regression model: 80 people, f²=0.15, alpha 0.05."),
("ambiguous","İki ölçüm yapıldı. Aynı kişilerde mi yoksa farklı kişilerde mi olduğunu veriyi toplayan arkadaşım bilir, ona sormam lazım. dz=0.4.","Two measurements were made. Whether it was on the same or different people only my colleague who collected the data knows. dz=0.4."),
]
assert len(S)==30
json.dump([dict(id=i+1,family=f) for i,(f,a,b) in enumerate(S)], open(here/"truth_hard.json","w"), ensure_ascii=False, indent=1)
json.dump([dict(id=i+1,question=a) for i,(f,a,b) in enumerate(S)], open(here/"questions_hard_tr.json","w"), ensure_ascii=False, indent=1)
json.dump([dict(id=i+1,question=b) for i,(f,a,b) in enumerate(S)], open(here/"questions_hard_en.json","w"), ensure_ascii=False, indent=1)
