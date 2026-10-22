"""LLM çıkarıcı değerlendirmesi: alt ajan (Claude haiku) soruları etiketler ve parametre çıkarır (agent/calibration/out_10.json),
hesap yine MCP aracında yapılır. Rapor: agent/eval_report_llm.md, günlük: logs/tool_calls_llm.jsonl"""
import json, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(here), str(here.parent / "src"), str(here.parent / "tests")]
import agent
from eval_set import expected

exp = expected()
out = {r["id"]: r for r in json.load(open(here / "calibration" / "out_10.json"))}
by_q = {e["question"]: out[i + 1] for i, e in enumerate(exp)}
def ext(q):
    r = by_q[q]; return r["family"], float(r["confidence"]), r["params"]
recs = agent.run([e["question"] for e in exp], ext, str(here.parent / "logs" / "tool_calls_llm.jsonl"))
fam_ok = par_ok = n_ok = 0; rows = []; k = sum(1 for e in exp if e["params"]); tok = 0
for e, r in zip(exp, recs):
    f_ok = r["family"] == e["family"] and (e["family"] == "t-paired") == (r["decision"] == "tool_call")
    p_ok = n = None
    if e["params"]:
        a = r.get("args", {})
        p_ok = a.get("mode") == e["params"]["mode"] and all(abs(float(a.get(x, -1)) - float(v)) < 1e-9 for x, v in e["params"].items() if x != "mode")
        res = r.get("result", {})
        n = (res.get("n_total") == e["n"]) if e["n"] is not None else abs(res.get("power", -1) - e["power"]) < 5e-8
        tok += (len(json.dumps(r["args"])) + len(json.dumps(r["result"]))) // 4
    fam_ok += bool(f_ok); par_ok += bool(p_ok); n_ok += bool(n)
    rows.append((e["question"][:70], e["family"], r["family"], r["confidence"], r["decision"], p_ok, n, r.get("seconds")))
rep = ["# Ajan değerlendirmesi, LLM çıkarıcı (10 soru)", "",
       "Çıkarıcı: Claude haiku alt ajanı (Jev yerine etiket kümesine kısıtlı LLM). Hesap: yalnızca MCP aracı. Sayıları LLM üretmedi, sorudaki sayıları çıkardı.", "",
       f"Aile/yönlendirme doğru: {fam_ok}/10 | Parametreler doğru: {par_ok}/{k} | N ya da güç doğru: {n_ok}/{k}", "",
       "| Soru | Beklenen | Bulunan | Güven | Karar | Parametre | N/güç | MCP süresi (s) |", "|---|---|---|---|---|---|---|---|"]
rep += [f"| {q}… | {a} | {b} | {c} | {d} | {p} | {n} | {s} |" for q, a, b, c, d, p, n, s in rows]
(here / "eval_report_llm.md").write_text("\n".join(rep), encoding="utf-8"); print("\n".join(rep))
