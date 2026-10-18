import argparse
import json
import sys

from .engine import PowerError, a_priori, post_hoc

_MODES = {"a-priori": "a-priori", "a_priori": "a-priori", "apriori": "a-priori",
          "post-hoc": "post-hoc", "post_hoc": "post-hoc", "posthoc": "post-hoc"}
_INT_KEYS = ("n_total", "n1", "n2", "df")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise PowerError(message)


def _build():
    p = _Parser(prog="gpower-clone", add_help=True, allow_abbrev=False)
    p.add_argument("--test", default=None)
    p.add_argument("--mode", default=None)
    p.add_argument("--tails", default=None)
    p.add_argument("--dz", "--d", dest="dz", default=None)
    p.add_argument("--alpha", default=None)
    p.add_argument("--power", default=None)
    p.add_argument("--n", "--n-total", "--sample-size", dest="n", default=None)
    return p


def _fmt(res):
    out = {}
    for k in ("n1", "n2", "n_total", "actual_power", "power", "critical", "df", "ncp"):
        v = res[k]
        if k in _INT_KEYS:
            out[k] = int(v)
        else:
            r = round(float(v), 7)
            out[k] = 0.0 if r == 0 else r
    return out


def _run(argv):
    a = _build().parse_args(argv)
    if a.test != "t-paired":
        raise PowerError("unsupported test: only --test t-paired is supported")
    mode = _MODES.get((a.mode or "").lower())
    if mode is None:
        raise PowerError("mode must be a-priori or post-hoc")
    if mode == "a-priori":
        return a_priori(a.tails, a.dz, a.alpha, a.power)
    return post_hoc(a.tails, a.dz, a.alpha, a.n)


def compute(**params):
    """Aynı çekirdeği CLI dışından çağırmak için (MCP adaptörü kullanır). Hata durumunda {"error": ...} döner."""
    argv = ["--test", "t-paired"]
    for k, v in params.items():
        if v is not None:
            argv += ["--" + k.replace("_", "-"), str(v)]
    try:
        return _fmt(_run(argv))
    except PowerError as e:
        return {"error": str(e).splitlines()[0] if str(e) else "error"}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        res = _fmt(_run(argv))
        print(json.dumps(res, separators=(",", ":")))
        return 0
    except SystemExit as e:  # --help
        return e.code if isinstance(e.code, int) else 0
    except PowerError as e:
        print(json.dumps({"error": str(e).splitlines()[0] if str(e) else "error"}))
        return 2
    except Exception as e:  # unexpected
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
