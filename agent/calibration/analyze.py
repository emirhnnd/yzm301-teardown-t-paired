"""Kalibrasyon ve TR/EN karşılaştırması. Girdi: truth.json, out_tr.json, out_en.json"""
import json, pathlib
here = pathlib.Path(__file__).resolve().parent
import sys
SET = sys.argv[1] if len(sys.argv) > 1 else "easy"
SUF = "" if SET == "easy" else "_hard"
N = 40 if SET == "easy" else 30
T = {r["id"]: r["family"] for r in json.load(open(here/f"truth{SUF}.json"))}
THR = 0.75
def load(f): return {r["id"]: r for r in json.load(open(here/f))}
def stats(out):
    rows = [(i, out[i]["family"], float(out[i]["confidence"]), out[i]["family"] == T[i]) for i in sorted(T)]
    acc = sum(r[3] for r in rows) / len(rows)
    bins = [(0.0, 0.75), (0.75, 0.9), (0.9, 1.01)]
    cal = []
    for lo, hi in bins:
        b = [r for r in rows if lo <= r[2] < hi]
        if b: cal.append((lo, hi, len(b), sum(r[2] for r in b)/len(b), sum(r[3] for r in b)/len(b)))
    # yönlendirme: model güven>=0.75 ve etiket desteklenen -> otomatik; aksi halde araştırmacıya sorulur
    auto = [r for r in rows if r[2] >= THR and r[1] not in ("ambiguous", "unsupported")]
    auto_ok = [r for r in auto if r[3]]
    # tehlikeli hata: aracı yanlış çağırmak (t-paired sanıp çağırmak ama gerçek t-paired değil)
    wrong_call = [r for r in auto if r[1] == "t-paired" and T[r[0]] != "t-paired"]
    ece = sum(n/len(rows)*abs(c-a) for _,_,n,c,a in cal)
    return rows, acc, cal, auto, auto_ok, wrong_call, ece
tr, en = load(f"out{SUF}_tr.json"), load(f"out{SUF}_en.json")
lines = [f"# Sınıflandırma kalibrasyonu ve TR/EN karşılaştırması ({N} soru, {'kolay' if SET=='easy' else 'zor'} set)", "",
 "Model: hızlı bir LLM (Claude haiku) etiket kümesine kısıtlı, yalnızca etiket+güven üretir, sayı üretmez. Jev erişimi yoktu; bu yüzden Jev yerine kısıtlı LLM kullanıldı.", ""]
res = {}
for name, out in (("Türkçe", tr), ("İngilizce", en)):
    rows, acc, cal, auto, auto_ok, wrong_call, ece = stats(out)
    res[name] = rows
    lines += [f"## {name}", "", f"- Etiket doğruluğu: **{sum(r[3] for r in rows)}/{N} = %{acc*100:.1f}**",
      f"- Otomatik karar (güven ≥ {THR} ve desteklenen etiket): {len(auto)} soru, bunların {len(auto_ok)} tanesi doğru",
      f"- Yanlış aileyle t-paired aracını çağırma (tehlikeli hata): **{len(wrong_call)}**",
      f"- Beklenen kalibrasyon hatası (ECE, 3 kutu): {ece:.3f}", "",
      "| Güven kutusu | n | ortalama söylenen güven | gerçek doğruluk |", "|---|---|---|---|"]
    lines += [f"| [{lo:.2f}, {min(hi,1):.2f}] | {n} | {c:.3f} | {a:.3f} |" for lo,hi,n,c,a in cal]
    wrong = [r for r in rows if not r[3]]
    lines += ["", "Yanlışlar: " + (", ".join(f"#{r[0]} (gerçek {T[r[0]]}, tahmin {r[1]}, güven {r[2]:.2f})" for r in wrong) or "yok"), ""]
agree = sum(tr[i]["family"] == en[i]["family"] for i in T)
lines += [f"## Dil karşılaştırması", "", f"- TR ve EN aynı etiketi verdi: {agree}/{N}", ""]
json.dump({k: v for k, v in res.items()}, open(here/f"results{SUF}.json", "w"), ensure_ascii=False)
(here/f"calibration_report{SUF}.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
