"""Ölçek testi: 500+ vektörde motorun N'si, bağımsız (scipy) kaba kuvvet aramasıyla bulunan
"hedefi sağlayan en küçük tamsayı N" ile karşılaştırılır. Kesirli N veren kütüphanelerle farkın kaynağı
yukarı yuvarlamadır; G*Power'ın 10 ondalık yuvarlaması yalnızca N* tam tamsayı komşuluğunda fark yaratır."""
import itertools, math, random
import pytest
from scipy import stats
from conftest import run_cli

def _integral(n, tails, dz, a):
    """Bağımsız referans: merkezsel olmayan t kuyruğunu ki-kare üzerinden sayısal integralle hesaplar.
    (scipy nct.cdf bazı (df, ncp) için nan döndürür; o zaman bu yola düşülür.)"""
    from scipy import integrate
    df = n - 1; d = abs(dz) * math.sqrt(n)
    c = stats.t.ppf(1 - (a / 2 if tails == 2 else a), df)
    def g(v):
        s = c * math.sqrt(v / df)
        up = stats.norm.sf(s - d)
        lo = stats.norm.cdf(-s - d) if tails == 2 else 0.0
        return stats.chi2.pdf(v, df) * (up + lo)
    return integrate.quad(g, 0, df * 20 + 200, limit=400, epsabs=1e-13, epsrel=1e-12)[0]

def power(n, tails, dz, a):
    df = n - 1; ncp = abs(dz) * math.sqrt(n)
    c = stats.t.ppf(1 - (a / 2 if tails == 2 else a), df)
    p = 1 - stats.nct.cdf(c, df, ncp)
    if tails == 2:
        p += stats.nct.cdf(-c, df, ncp)
    if math.isnan(p):
        return _integral(n, tails, dz, a)
    return p

def min_n(tails, dz, a, target):
    lo, hi = 2, 4
    if power(2, tails, dz, a) >= target:
        return 2
    while power(hi, tails, dz, a) < target:
        lo, hi = hi, hi * 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if power(mid, tails, dz, a) >= target:
            hi = mid
        else:
            lo = mid
    return hi

def vectors():
    rnd = random.Random(20261018)
    out = []
    for tails, dz, a, p in itertools.product([1, 2], [0.1, 0.2, 0.35, 0.5, 0.8, 1.2, 2.0, 3.5],
                                              [0.001, 0.01, 0.05, 0.1], [0.5, 0.8, 0.9, 0.95, 0.99]):
        out.append((tails, dz, a, p))
    while len(out) < 560:
        out.append((rnd.choice([1, 2]), round(rnd.uniform(0.05, 4), 3), rnd.choice([0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.2]),
                    round(rnd.uniform(0.3, 0.995), 3)))
    return out

VEC = vectors()

def test_vector_count():
    assert len(VEC) >= 500

def test_scale_n_matches_minimal_integer():
    from powerlab import engine  # motor doğrudan (süreç başlatmadan)
    bad = []
    for tails, dz, a, p in VEC:
        got = engine.a_priori(tails, dz, a, p)["n_total"]
        exp = min_n(tails, dz, a, p)
        if got != exp:
            bad.append((tails, dz, a, p, got, exp))
    rate = 1 - len(bad) / len(VEC)
    print("uyum oranı", rate, "uyuşmayan:", bad[:10])
    assert rate >= 0.99, bad[:10]
