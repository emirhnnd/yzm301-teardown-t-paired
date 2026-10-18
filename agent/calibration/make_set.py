"""40 soruluk sınıflandırma seti (TR + İngilizce çeviri). Etiketler ayrı dosyada tutulur; ajanlara etiketsiz kopya verilir."""
import json, pathlib
here = pathlib.Path(__file__).resolve().parent
S = [
# t-paired (8)
("t-paired","Aynı 30 hastanın ilaç başlamadan önceki ve üç ay sonraki kolesterol değerlerini karşılaştıracağız; dz=0.5, alfa 0.05, güç 0.80 için kaç hasta gerekir?","We will compare the cholesterol values of the same 30 patients before starting the drug and three months later; how many patients are needed for dz=0.5, alpha 0.05, power 0.80?"),
("t-paired","Her katılımcıyı hem sağ hem sol elinde ölçtük, eşleştirilmiş t testi için güç nedir? dz=0.4, 20 çift, alfa 0.05.","We measured each participant on both the right and left hand; what is the power for a paired t-test? dz=0.4, 20 pairs, alpha 0.05."),
("t-paired","Egzersiz programı öncesi ve sonrası istirahat nabzı ölçülen kişiler için tek yönlü, dz=0.6, alfa 0.05, güç 0.90 örneklem büyüklüğü?","Sample size for people whose resting pulse was measured before and after an exercise program, one-tailed, dz=0.6, alpha 0.05, power 0.90?"),
("t-paired","İkiz kardeşlerde (her çiftte bir kardeşe tedavi, diğerine plasebo) fark için dz=0.35 beklenirse kaç ikiz çifti lazım, güç 0.80, alfa 0.05?","If dz=0.35 is expected for the difference in twins (one twin of each pair gets treatment, the other placebo), how many twin pairs are needed, power 0.80, alpha 0.05?"),
("t-paired","Ameliyat öncesi ve sonrası ağrı skoru, 45 hasta, dz=0.3, alfa 0.01; gücümüz ne kadar?","Pain score before and after surgery, 45 patients, dz=0.3, alpha 0.01; what is our power?"),
("t-paired","Aynı öğrencilerin ön test ve son test notları arasındaki farkı yakalamak için dz=0.45, alfa 0.05, %85 güçle kaç öğrenci gerekir?","How many students are needed to detect the difference between pre-test and post-test scores of the same students, dz=0.45, alpha 0.05, 85% power?"),
("t-paired","Tek göz ameliyatlı hastalarda ameliyatlı ve ameliyatsız göz arasındaki basınç farkı (eşleşmiş gözler), dz=0.7, güç 0.80, kaç hasta?","Pressure difference between the operated and non-operated eye in patients with single-eye surgery (matched eyes), dz=0.7, power 0.80, how many patients?"),
("t-paired","Kilo kaybı programının başında ve sonunda tartılan 60 kişi için dz=0.2, alfa 0.05, iki yönlü güç kaçtır?","For 60 people weighed at the start and end of a weight-loss program, dz=0.2, alpha 0.05, what is the two-tailed power?"),
# t2-indep (8)
("t2-indep","Tedavi grubu ile kontrol grubunun (farklı hastalar) ortalama tansiyonunu karşılaştıracağız; d=0.5, alfa 0.05, güç 0.80, grup başına kaç hasta?","We will compare mean blood pressure between a treatment group and a control group (different patients); d=0.5, alpha 0.05, power 0.80, how many patients per group?"),
("t2-indep","Erkek ve kadınlarda boy ortalaması farkı için iki bağımsız grup t testi, d=0.8, eşit gruplar, güç 0.90 kaç kişi?","Independent two-group t-test for the difference in mean height between men and women, d=0.8, equal groups, power 0.90, how many people?"),
("t2-indep","İlaç grubu 40, plasebo grubu 40 kişi; d=0.4, alfa 0.05 ile gücümüz nedir?","Drug group 40, placebo group 40 people; with d=0.4 and alpha 0.05, what is our power?"),
("t2-indep","Sigara içenlerle içmeyenlerin akciğer kapasitesi ortalamasını kıyaslıyoruz, d=0.6, tek yönlü, alfa 0.05, güç 0.80.","We compare mean lung capacity of smokers and non-smokers, d=0.6, one-tailed, alpha 0.05, power 0.80."),
("t2-indep","Randomize iki kollu çalışmada A kolu ile B kolu arasındaki HbA1c farkı için d=0.3, güç 0.85, kaç denek?","In a randomized two-arm trial, for the HbA1c difference between arm A and arm B, d=0.3, power 0.85, how many subjects?"),
("t2-indep","Cerrahi ile konservatif tedavi gören iki ayrı hasta grubunun iyileşme süresi, d=0.55, alfa 0.05, güç 0.80.","Recovery time of two separate patient groups receiving surgery versus conservative treatment, d=0.55, alpha 0.05, power 0.80."),
("t2-indep","Yeni ve eski eğitim yöntemiyle öğrenen iki farklı sınıfın sınav ortalamaları arasındaki fark, d=0.35, kaç öğrenci gerekir?","Difference between exam means of two different classes taught with the new and old method, d=0.35, how many students are needed?"),
("t2-indep","Hastane A ve hastane B'deki hastaların bekleme süresi ortalamaları farklı mı? d=0.5, 50'şer hasta, güç nedir?","Are mean waiting times different for patients at hospital A and hospital B? d=0.5, 50 patients each, what is the power?"),
# anova-oneway (6)
("anova-oneway","Üç farklı doz grubunun (düşük, orta, yüksek) ortalama ağrı skorlarını karşılaştırmak için f=0.25, alfa 0.05, güç 0.80 ile kaç hasta gerekir?","To compare mean pain scores of three dose groups (low, medium, high), how many patients are needed with f=0.25, alpha 0.05, power 0.80?"),
("anova-oneway","Dört tedavi kolunda tek yönlü varyans analizi, etki büyüklüğü f=0.4, güç 0.90.","One-way analysis of variance across four treatment arms, effect size f=0.4, power 0.90."),
("anova-oneway","Beş farklı gübre türünün verime etkisi, tek faktörlü ANOVA, f=0.3, alfa 0.05, güç 0.80.","Effect of five different fertilizer types on yield, one-way ANOVA, f=0.3, alpha 0.05, power 0.80."),
("anova-oneway","Üç kol, kol başına 25 kişi, f=0.35, alfa 0.05; ANOVA gücü nedir?","Three arms, 25 people per arm, f=0.35, alpha 0.05; what is the ANOVA power?"),
("anova-oneway","Üç ayrı hastanenin ortalama yatış süresini aynı anda karşılaştırmak istiyoruz, f=0.2, güç 0.80.","We want to compare mean length of stay in three separate hospitals at once, f=0.2, power 0.80."),
("anova-oneway","Altı egzersiz protokolünün ortalama VO2 değerlerini karşılaştıran tek yönlü ANOVA için f=0.25, kaç denek?","How many subjects for a one-way ANOVA comparing mean VO2 across six exercise protocols, f=0.25?"),
# chi2-contingency (6)
("chi2-contingency","Sigara içme durumu (içen/içmeyen) ile akciğer hastalığı (var/yok) arasındaki ilişkiyi 2x2 olumsallık tablosunda ki-kare ile sınayacağız, w=0.3, güç 0.80.","We will test the association between smoking (yes/no) and lung disease (yes/no) with chi-square in a 2x2 contingency table, w=0.3, power 0.80."),
("chi2-contingency","Üç kan grubu ile hastalık durumu arasında ki-kare bağımsızlık testi, w=0.2, alfa 0.05, kaç kişi?","Chi-square test of independence between three blood groups and disease status, w=0.2, alpha 0.05, how many people?"),
("chi2-contingency","Cinsiyet ve parti tercihi (4 parti) tablosunda ki-kare, w=0.15, güç 0.90.","Chi-square on the table of gender and party preference (4 parties), w=0.15, power 0.90."),
("chi2-contingency","Aşı olan ve olmayanlarda hastalanma oranlarının olumsallık tablosu, w=0.25, alfa 0.05, güç 0.80.","Contingency table of illness rates in vaccinated and unvaccinated people, w=0.25, alpha 0.05, power 0.80."),
("chi2-contingency","Anket cevabı (evet/hayır/kararsız) ile yaş grubu (3 grup) ilişkisi için ki-kare, w=0.3, 200 kişi, güç?","Chi-square for the association between survey answer (yes/no/undecided) and age group (3 groups), w=0.3, 200 people, power?"),
("chi2-contingency","Kategorik iki değişken arasında bağımsızlık sınaması, 3x3 tablo, w=0.2, alfa 0.01, güç 0.80.","Test of independence between two categorical variables, 3x3 table, w=0.2, alpha 0.01, power 0.80."),
# multireg-r2 (6)
("multireg-r2","Yaş, kilo ve kan şekeri değişkenleriyle tansiyonu tahmin eden çoklu doğrusal regresyonda R² testi, f²=0.15, güç 0.80, kaç kişi?","R² test in a multiple linear regression predicting blood pressure from age, weight and blood sugar, f²=0.15, power 0.80, how many people?"),
("multireg-r2","Beş yordayıcılı bir regresyon modelinde R² anlamlı mı, f²=0.1, alfa 0.05, güç 0.90.","Is R² significant in a regression model with five predictors, f²=0.1, alpha 0.05, power 0.90."),
("multireg-r2","Çoklu regresyonda toplam varyansın açıklanma oranı (R²) için örneklem büyüklüğü, 4 yordayıcı, f²=0.2.","Sample size for R² (proportion of variance explained) in multiple regression, 4 predictors, f²=0.2."),
("multireg-r2","Risk faktörleri (yaş, BMI, sigara, kolesterol, aile öyküsü) ile hastalık skoru arasındaki regresyon; f²=0.12, 150 kişi, güç nedir?","Regression between risk factors (age, BMI, smoking, cholesterol, family history) and disease score; f²=0.12, 150 people, what is the power?"),
("multireg-r2","Üç bağımsız değişkenli regresyon modelinde R² sıfırdan farklı mı testi için n, f²=0.35, alfa 0.05, güç 0.80.","Sample size n for testing whether R² differs from zero in a regression model with three independent variables, f²=0.35, alpha 0.05, power 0.80."),
("multireg-r2","Gelir, eğitim ve yaşla mutluluk puanını yordayan çoklu regresyon, R² testi, f²=0.08, güç 0.85.","Multiple regression predicting happiness score from income, education and age, R² test, f²=0.08, power 0.85."),
# ambiguous (3)
("ambiguous","İki ölçüm arasındaki farkı karşılaştıracağız, etki 0.5, güç 0.80, kaç kişi gerekir?","We will compare the difference between two measurements, effect 0.5, power 0.80, how many people are needed?"),
("ambiguous","İki grubun ortalamalarını karşılaştırmak istiyorum, d=0.5, ama gruplar aynı kişilerden mi farklı kişilerden mi henüz bilmiyorum.","I want to compare the means of two groups, d=0.5, but I do not yet know whether the groups are the same people or different people."),
("ambiguous","Tedavinin etkisini görmek için bir çalışma planlıyorum, güç 0.80 olsun, kaç hasta gerekir?","I am planning a study to see the effect of the treatment; let power be 0.80, how many patients are needed?"),
# unsupported (3)
("unsupported","Hayatta kalma süresini iki tedavi arasında log-rank testiyle karşılaştıracağım, kaç olay gerekir?","I will compare survival time between two treatments with a log-rank test; how many events are needed?"),
("unsupported","İki sürekli değişken arasındaki Pearson korelasyonu r=0.3'ü saptamak için kaç kişi lazım?","How many people are needed to detect a Pearson correlation of r=0.3 between two continuous variables?"),
("unsupported","Verim normal dağılmıyor, Mann-Whitney U testi için örneklem büyüklüğü hesaplar mısın?","The data are not normally distributed; can you compute the sample size for the Mann-Whitney U test?"),
]
assert len(S) == 40
truth = [dict(id=i+1, family=f) for i, (f, tr, en) in enumerate(S)]
json.dump(truth, open(here/"truth.json","w"), ensure_ascii=False, indent=1)
json.dump([dict(id=i+1, question=tr) for i,(f,tr,en) in enumerate(S)], open(here/"questions_tr.json","w"), ensure_ascii=False, indent=1)
json.dump([dict(id=i+1, question=en) for i,(f,tr,en) in enumerate(S)], open(here/"questions_en.json","w"), ensure_ascii=False, indent=1)
print(len(S), "ok")
