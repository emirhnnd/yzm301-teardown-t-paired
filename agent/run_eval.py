"""Değerlendirme: 10 soru, MCP üzerinden. Rapor: agent/eval_report.md, günlük: logs/tool_calls.jsonl"""
import json, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(here), str(here.parent / "src"), str(here.parent / "tests")]
import agent
from eval_set import expected

def main(extractor="rules"):
    exp = expected()
    recs = agent.run([e["question"] for e in exp], extractor, str(here.parent / "logs" / "tool_calls.jsonl"))
    rows, fam_ok, par_ok, n_ok = [], 0, 0, 0
    tok_mcp = 0
    for e, r in zip(exp, recs):
        f_ok = r["family"] == e["family"] or (e["family"] != "t-paired" and r["decision"] == "ask_researcher")
        p_ok = n = None
        if e["params"]:
            a = r.get("args", {})
            p_ok = all(abs(float(a.get(k, -1)) - float(v)) < 1e-9 for k, v in e["params"].items() if k != "mode") and a.get("mode") == e["params"]["mode"]
            res = r.get("result", {})
            if e["n"] is not None: n = res.get("n_total") == e["n"]
            else: n = abs(res.get("power", -1) - e["power"]) < 5e-8
            tok_mcp += (len(json.dumps(r["args"])) + len(json.dumps(r["result"]))) // 4
        fam_ok += bool(f_ok); par_ok += bool(p_ok); n_ok += bool(n)
        rows.append((e["question"][:70], e["family"], r["family"], r["decision"], p_ok, n))
    k = sum(1 for e in exp if e["params"])
    rep = ["# Ajan değerlendirmesi (10 soru)", "",
           f"Çıkarıcı: `{extractor}`  |  Aile/yönlendirme doğru: {fam_ok}/10  |  Parametreler doğru: {par_ok}/{k}  |  N ya da güç doğru (motor çıktısı bağımsız scipy ile): {n_ok}/{k}", "",
           "| Soru | Beklenen aile | Bulunan aile | Karar | Parametre | N/güç |", "|---|---|---|---|---|---|"]
    rep += [f"| {q}… | {a} | {b} | {c} | {d} | {e} |" for q, a, b, c, d, e in rows]
    rep += ["", f"MCP yolu araç çağrısı+yanıt boyutu (tahmini token ≈ karakter/4): toplam ≈ {tok_mcp} token, soru başına ≈ {tok_mcp // max(k,1)}."]
    (here / "eval_report.md").write_text("\n".join(rep), encoding="utf-8")
    print("\n".join(rep))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rules")
