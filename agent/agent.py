"""Türkçe klinik soruyu anlayıp MCP aracını çağıran ajan. AJAN HESAP YAPMAZ: sayılar yalnızca MCP aracından gelir.

İki çıkarıcı vardır:
  - rules: çevrimdışı, kural tabanlı (Anthropic API anahtarı gerekmez). Varsayılan.
  - llm:   ANTHROPIC_API_KEY varsa, etiket kümesiyle kısıtlı bir LLM (Claude) aile ve parametre çıkarır.
Her iki durumda test ailesi etiketi {t2-indep,t-paired,anova-oneway,chi2-contingency,multireg-r2,ambiguous,unsupported}
ve güven değeri üretilir; güven < 0.75 ya da etiket ambiguous/unsupported ise araştırmacıya sorulur."""
import asyncio, json, os, re, sys, time, pathlib

LABELS = ["t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2", "ambiguous", "unsupported"]
THRESH = 0.75
NUM = r"(\d+(?:[.,]\d+)?)"

def _f(s): return float(s.replace(",", "."))

def classify(q: str):
    t = q.lower()
    sc = {l: 0.0 for l in LABELS}
    if re.search(r"önce.{0,12}sonra|eşleş|aynı (hasta|kişi)|tedavi öncesi|öncesi ve sonrası|\\bçift\\b(?! yönlü)", t): sc["t-paired"] += 0.9
    if re.search(r"bağımsız (iki )?grup|plasebo|iki grup", t): sc["t2-indep"] += 0.9
    if re.search(r"\büç\b|3 tedavi|anova|tedavi kol", t): sc["anova-oneway"] += 0.9
    if re.search(r"olumsallık|ki-?kare|χ|oran.*tablo", t): sc["chi2-contingency"] += 0.9
    if re.search(r"regresyon|r²|r2|risk faktör", t): sc["multireg-r2"] += 0.9
    top = sorted(sc.items(), key=lambda kv: -kv[1])
    if top[0][1] == 0: return "unsupported", 0.5
    if top[1][1] >= 0.9 and top[0][1] >= 0.9: return "ambiguous", 0.5
    return top[0][0], top[0][1]

def extract_rules(q: str):
    t = q.lower().replace("α", "alfa")
    p = {}
    m = re.search(r"d[zZ]?\s*[=:]?\s*" + NUM, t) or re.search(r"etki büyüklüğü\s*(?:dz)?\s*[=:]?\s*" + NUM, t)
    m2 = re.search(r"\bdz\s*[=:]?\s*" + NUM, t) or re.search(r"etki büyüklüğü\s*[=:]?\s*" + NUM, t) or re.search(r"\bd\s*=\s*" + NUM, t)
    if m2: p["dz"] = _f(m2.group(1))
    m = re.search(r"alfa\s*[=:]?\s*" + NUM, t)
    if m: p["alpha"] = _f(m.group(1))
    m = re.search(r"%\s*(\d+)\s*güç|güç\s*[=:]?\s*%\s*(\d+)", t)
    if m: p["power"] = int(m.group(1) or m.group(2)) / 100
    else:
        m = re.search(r"güç\s*[=:]?\s*" + NUM, t)
        if m and _f(m.group(1)) < 1: p["power"] = _f(m.group(1))
    p["tails"] = 1 if re.search(r"tek yönlü|tek kuyruk", t) else 2
    m = re.search(NUM + r"\s*(hasta|kişi|çift)", t)
    posthoc = bool(re.search(r"gücü nedir|güç (kaç|ne)|çalışmanın gücü", t)) and "power" not in p
    if posthoc and m:
        p["mode"] = "post-hoc"; p["n"] = int(_f(m.group(1)))
    else:
        p["mode"] = "a-priori"
    return p

def extract_llm(q: str):  # pragma: no cover  (API anahtarı gerektirir)
    import anthropic
    c = anthropic.Anthropic()
    sys_p = ("Yalnızca JSON döndür: {family, confidence, params:{mode,tails,dz,alpha,power,n}}. family etiketleri: " + ",".join(LABELS) +
             ". ASLA hesap yapma, N ya da güç üretme; yalnızca soruda yazan sayıları çıkar.")
    r = c.messages.create(model=os.environ.get("AGENT_MODEL", "claude-sonnet-5-5"), max_tokens=300, system=sys_p,
                          messages=[{"role": "user", "content": q}])
    j = json.loads(r.content[0].text)
    return j["family"], j["confidence"], j["params"]

async def call_tool(session, params):
    args = {k: v for k, v in params.items() if v is not None}
    t0 = time.perf_counter()
    res = await session.call_tool("power_analysis_t_paired", args)
    dt = time.perf_counter() - t0
    out = json.loads(res.content[0].text) if res.content else res.structuredContent
    return out, dt, args

async def answer(session, q, log, extractor="rules"):
    if callable(extractor):  # önceden üretilmiş LLM çıkarımı (alt ajan) ya da başka bir çıkarıcı
        fam, conf, params = extractor(q)
    elif extractor == "llm" and os.environ.get("ANTHROPIC_API_KEY"):
        fam, conf, params = extract_llm(q)
    else:
        fam, conf = classify(q); params = extract_rules(q) if fam == "t-paired" else None
    rec = dict(question=q, family=fam, confidence=conf)
    if fam != "t-paired" or conf < THRESH:
        rec["decision"] = "ask_researcher"
        rec["reply"] = f"Bu soru '{fam}' ailesine benziyor (güven {conf:.2f}). Bu araç yalnızca eşleştirilmiş t testini (t-paired) hesaplar; lütfen test ailesini ve parametreleri doğrulayın."
    else:
        out, dt, args = await call_tool(session, params)
        rec.update(decision="tool_call", tool="power_analysis_t_paired", args=args, result=out, seconds=round(dt, 3))
        if "error" in out:
            rec["reply"] = "Hesap motoru hata verdi: " + out["error"]
        elif params["mode"] == "a-priori":
            rec["reply"] = f"Gerekli örneklem: {out['n_total']} çift (gerçek güç {out['actual_power']:.4f}, kritik t {out['critical']}, df {out['df']})."
        else:
            rec["reply"] = f"Güç: {out['actual_power']:.4f} (N={out['n_total']}, df {out['df']})."
    log.write(json.dumps(rec, ensure_ascii=False) + "\n"); log.flush()
    return rec

async def with_server():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    root = pathlib.Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    sp = StdioServerParameters(command=sys.executable, args=["-m", "powerlab_mcp.server"], env=env)
    return sp, stdio_client, ClientSession

def run(questions, extractor="rules", log_path="logs/tool_calls.jsonl"):
    async def _go():
        sp, stdio_client, ClientSession = await with_server()
        recs = []
        with open(log_path, "w") as log:
            async with stdio_client(sp) as (r, w):
                async with ClientSession(r, w) as s:
                    await s.initialize()
                    for q in questions:
                        recs.append(await answer(s, q, log, extractor))
        return recs
    return asyncio.run(_go())

if __name__ == "__main__":
    for r in run([" ".join(sys.argv[1:])]):
        print(r["reply"])
