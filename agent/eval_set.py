"""10 soruluk değerlendirme seti. Beklenen N, motordan DEĞİL bağımsız scipy aramasından (tests/test_scale_scipy.min_n) hesaplanır."""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tests"))
from test_scale_scipy import min_n, power

Q = [
 ("Önce ve sonra tansiyon ölçtüğümüz aynı hastalarda etki büyüklüğü dz=0.5 bekliyorum. Alfa 0.05, güç %80 için kaç hasta gerekir? İki yönlü.", "t-paired", dict(mode="a-priori", tails=2, dz=0.5, alpha=0.05, power=0.80)),
 ("Eşleştirilmiş t testi, tek yönlü, dz 0.3, alfa 0.05, güç 0.90 olması için kaç çift gerekli?", "t-paired", dict(mode="a-priori", tails=1, dz=0.3, alpha=0.05, power=0.90)),
 ("Tedavi öncesi ve sonrası kan basıncı ölçülen 25 hastada dz=0.6, alfa 0.05, iki yönlü; çalışmanın gücü nedir?", "t-paired", dict(mode="post-hoc", tails=2, dz=0.6, alpha=0.05, n=25)),
 ("Aynı 40 hastanın diyet öncesi ve sonrası kilosu, dz 0.4, alfa=0.01, iki yönlü; güç kaç olur?", "t-paired", dict(mode="post-hoc", tails=2, dz=0.4, alpha=0.01, n=40)),
 ("Eşleşmiş örneklerde etki büyüklüğü 0.8, alfa 0.05, %95 güç için örneklem büyüklüğü nedir? İki yönlü.", "t-paired", dict(mode="a-priori", tails=2, dz=0.8, alpha=0.05, power=0.95)),
 ("Önce-sonra tansiyon karşılaştırması, dz=0.25, alfa 0.05, güç 0.85, çift yönlü, kaç kişi lazım?", "t-paired", dict(mode="a-priori", tails=2, dz=0.25, alpha=0.05, power=0.85)),
 ("12 hastada ilaç öncesi ve sonrası ölçüm yaptık, dz=1.0, alfa 0.05, iki yönlü; güç ne olur?", "t-paired", dict(mode="post-hoc", tails=2, dz=1.0, alpha=0.05, n=12)),
 ("Eşleştirilmiş gözlemlerde dz = 0.35, alfa = 0.025, tek yönlü, güç 0.8 için kaç çift gerekir?", "t-paired", dict(mode="a-priori", tails=1, dz=0.35, alpha=0.025, power=0.80)),
 ("İlaç ve plasebo gruplarını (bağımsız iki grup) karşılaştırıyorum, d=0.5, güç 0.95, kaç hasta gerekir?", "t2-indep", None),
 ("Üç tedavi kolunun ortalamalarını karşılaştırmak için kaç hasta gerekir?", "anova-oneway", None),
]

def expected():
    out = []
    for q, fam, p in Q:
        e = dict(question=q, family=fam, params=p, n=None, power=None)
        if p and p["mode"] == "a-priori":
            e["n"] = min_n(p["tails"], p["dz"], p["alpha"], p["power"])
        elif p:
            e["power"] = round(power(p["n"], p["tails"], p["dz"], p["alpha"]), 7)
        out.append(e)
    return out

if __name__ == "__main__":
    json.dump(expected(), open(pathlib.Path(__file__).with_name("eval_set.json"), "w"), ensure_ascii=False, indent=1)
