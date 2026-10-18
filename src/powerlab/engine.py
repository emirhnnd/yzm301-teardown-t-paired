"""Pure computation for t-paired (dz) power analysis. See SPEC.md."""
import math

from scipy import stats

N_MAX = 2147483646
N_MIN_POSTHOC = 3
RANGE_MSG = "Total sample size is outside the admissible range (3, 2147483646)"
LO = 2.0
H0 = 100.0
EPS = 2.220446049250313e-16
REL_TOL = 1.11e-16
MAX_ITER = 300


class PowerError(ValueError):
    """Invalid input or unsolvable problem."""


def _upper(c, df, ncp):
    v = 1 - stats.nct.cdf(c, df, ncp)
    if math.isnan(v):
        v = stats.nct.sf(c, df, ncp)
    return float(v)


def _lower(c, df, ncp):
    """nct_cdf(-c, df, ncp); scipy returns nan for large ncp, where the true
    value is negligible, so fall back to the reflected survival function."""
    v = stats.nct.cdf(-c, df, ncp)
    if math.isnan(v):
        v = stats.nct.sf(c, df, -ncp)
    if math.isnan(v):
        v = 0.0
    return float(v)


def power(N, tails, dz, alpha):
    df = N - 1
    ncp = abs(dz) * math.sqrt(N)
    if tails == 2:
        c = stats.t.ppf(1 - alpha / 2, df)
        return _upper(c, df, ncp) + _lower(c, df, ncp)
    c = stats.t.ppf(1 - alpha, df)
    return _upper(c, df, ncp)


def brent(f, a, b, max_iter=MAX_ITER):
    """Brent's root finder (zeroin). Returns 0.0 without a sign change."""
    fa, fb = f(a), f(b)
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if (fa > 0) == (fb > 0):
        return 0.0
    c, fc = a, fa
    d = e = b - a
    for _ in range(max_iter):
        if (fb > 0) == (fc > 0):
            c, fc = a, fa
            d = e = b - a
        if abs(fc) < abs(fb):
            a, b, c = b, c, b
            fa, fb, fc = fb, fc, fb
        tol = REL_TOL * abs(b)
        m = 0.5 * (c - b)
        if abs(m) <= tol or fb == 0.0:
            return b
        if abs(e) >= tol and abs(fa) > abs(fb):
            s = fb / fa
            if a == c:
                p = 2.0 * m * s
                q = 1.0 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * (2.0 * m * q * (q - r) - (b - a) * (r - 1.0))
                q = (q - 1.0) * (r - 1.0) * (s - 1.0)
            if p > 0:
                q = -q
            else:
                p = -p
            if 2.0 * p < min(3.0 * m * q - abs(tol * q), abs(e * q)):
                e = d
                d = p / q
            else:
                d = m
                e = m
        else:
            d = m
            e = m
        a, fa = b, fb
        if abs(d) > tol:
            b += d
        else:
            b += math.copysign(tol, m)
        fb = f(b)
    return b


def round_up_n(x):
    """r(x) = ceil(floor(x*1e10 + 0.5) / 1e10)."""
    return math.ceil(math.floor(x * 1e10 + 0.5) / 1e10)


def _num(name, v):
    if isinstance(v, bool) or v is None:
        raise PowerError(f"{name} is missing or not a number")
    try:
        v = float(v)
    except (TypeError, ValueError):
        raise PowerError(f"{name} is missing or not a number")
    if not math.isfinite(v):
        raise PowerError(f"{name} is missing or not a number")
    return v


def _common(tails, dz, alpha):
    t = _num("tails", tails)
    if t not in (1.0, 2.0):
        raise PowerError("tails must be 1 or 2")
    dz = _num("dz", dz)
    alpha = _num("alpha", alpha)
    if not (0.0 < alpha < 1.0):
        raise PowerError("alpha must be in the open interval (0, 1)")
    if not (-20.0 <= dz <= 20.0):
        raise PowerError("Effect size dz is outside the admissible range (-20, 20)")
    return int(t), dz, alpha


def _outputs(N, tails, dz, alpha):
    p = power(N, tails, dz, alpha)
    df = N - 1
    q = 1 - alpha / 2 if tails == 2 else 1 - alpha
    c = float(stats.t.ppf(q, df))
    ncp = abs(dz) * math.sqrt(N)
    if dz < 0:
        c, ncp = -c, -ncp
    return {"n_total": N, "n1": N, "n2": N, "actual_power": p, "power": p,
            "critical": c, "df": df, "ncp": ncp}


def post_hoc(tails, dz, alpha, n):
    tails, dz, alpha = _common(tails, dz, alpha)
    nv = _num("n", n)
    if nv != math.floor(nv):
        raise PowerError("n must be an integer")
    if nv < N_MIN_POSTHOC or nv > N_MAX:
        raise PowerError(RANGE_MSG)
    return _outputs(int(nv), tails, dz, alpha)


def _f_factory(tails, dz, alpha, target):
    def f(N):
        v = power(N, tails, dz, alpha) - target
        if math.isnan(v):
            raise PowerError("numerical failure while solving for N")
        return v
    return f


def a_priori(tails, dz, alpha, power_target):
    tails, dz, alpha = _common(tails, dz, alpha)
    pw = _num("power", power_target)
    if not (0.0 < pw < 1.0):
        raise PowerError("power must be in the open interval (0, 1)")
    if alpha > pw:
        raise PowerError("Power must be greater than or equal to alpha.")
    if abs(dz) < 1e-5:
        raise PowerError("In an a priori analysis, the absolute value of the "
                         "effect size be greater than 0.00001.")
    f = _f_factory(tails, dz, alpha, pw)
    if f(H0) >= 0:
        hi = H0
        lo = (LO + H0) / 2
        while lo >= LO and f(lo) > 0:
            hi = lo
            lo = (lo + LO) / 2 - LO
    else:
        lo = H0
        hi = H0 * 1.6
        while f(hi) < 0:
            lo = hi
            hi = hi * 1.6
            if lo > N_MAX:
                raise PowerError(RANGE_MSG)
    if lo < LO:
        lo = LO
    root = brent(f, lo, hi)
    n = round_up_n(root)
    if n < lo:
        n = round_up_n(lo)
    if n > N_MAX:
        raise PowerError(RANGE_MSG)
    return _outputs(int(n), tails, dz, alpha)
