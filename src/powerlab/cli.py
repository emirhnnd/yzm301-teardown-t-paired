"""gpower-clone komut satırı. CONTRACT.md v1.0.0: katı bayraklar, tek satır JSON, hata kodları, çıkış kodu 0/2/1."""
import argparse
import json
import sys

from .engine import PowerError, a_priori, post_hoc

VERSION = {"contract_version": "1.0.0", "name": "gpower-clone-t-paired", "engine": "powerlab"}
_MODES = ("a-priori", "post-hoc")
# Mod başına zorunlu alanlar (sözleşme: varsayılan yok, ilgisiz alan hatadır).
_FIELDS = {"a-priori": ("tails", "dz", "alpha", "power"),
           "post-hoc": ("tails", "dz", "alpha", "n_total")}
_ALL = ("test", "mode", "tails", "dz", "alpha", "power", "n_total")
_KEYS = {"a-priori": ("ncp", "critical_t", "df", "n_total", "actual_power"),
         "post-hoc": ("ncp", "critical_t", "df", "power")}
_INT_KEYS = ("n_total", "df")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise PowerError(message, "UNKNOWN_PARAM", None)


def _build():
    p = _Parser(prog="gpower-clone", add_help=False, allow_abbrev=False)
    for k in _ALL:
        p.add_argument("--" + k, default=None)
    p.add_argument("--n-total", dest="n_total", default=None)  # tire yazımı da kabul
    p.add_argument("--ratio", default=None)  # ortak düzenek tüm ailelere verebilir; eşleştirilmiş testte yok sayılır
    p.add_argument("--version", action="store_true")
    return p


def _fmt(res, mode):
    out = {}
    for k in _KEYS[mode]:
        v = res["actual_power" if (mode == "post-hoc" and k == "power") else k]
        if k in _INT_KEYS:
            out[k] = int(v)
        else:
            v = float(v)
            out[k] = 0.0 if v == 0 else v
    return out


def _run(argv):
    a = _build().parse_args(argv)
    if a.version:
        return None, VERSION
    if a.test is None:
        raise PowerError("--test is required", "MISSING_PARAM", "test")
    if a.test != "t-paired":
        raise PowerError("unsupported test: only --test t-paired is supported", "UNSUPPORTED", "test")
    if a.mode is None:
        raise PowerError("--mode is required", "MISSING_PARAM", "mode")
    if a.mode not in _MODES:
        raise PowerError("unsupported mode: use a-priori or post-hoc", "UNSUPPORTED", "mode")
    need = _FIELDS[a.mode]
    for k in ("tails", "dz", "alpha", "power", "n_total"):
        if getattr(a, k) is not None and k not in need:
            raise PowerError(f"--{k} is not used in mode {a.mode}", "UNKNOWN_PARAM", k)
    for k in need:
        if getattr(a, k) is None:
            raise PowerError(f"--{k} is required in mode {a.mode}", "MISSING_PARAM", k)
    if a.mode == "a-priori":
        return a.mode, a_priori(a.tails, a.dz, a.alpha, a.power)
    return a.mode, post_hoc(a.tails, a.dz, a.alpha, a.n_total)


def _err(e):
    msg = str(e).splitlines()[0] if str(e) else "error"
    return {"error": msg, "code": getattr(e, "code", "INVALID_VALUE"), "field": getattr(e, "field", None)}


def compute(**params):
    """Aynı çekirdeği CLI dışından çağırmak için (MCP adaptörü). Hata: {"error","code","field"}."""
    argv = ["--test", "t-paired"]
    for k, v in params.items():
        if v is not None:
            argv += ["--" + k, str(v)]
    try:
        mode, res = _run(argv)
        return _fmt(res, mode)
    except PowerError as e:
        return _err(e)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        mode, res = _run(argv)
        print(json.dumps(res if mode is None else _fmt(res, mode), separators=(",", ":")))
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
    except PowerError as e:
        print(json.dumps(_err(e), ensure_ascii=False))
        return 2
    except Exception as e:  # iç hata
        print(json.dumps({"error": f"{type(e).__name__}: {e}", "code": "NO_SOLUTION", "field": None}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
