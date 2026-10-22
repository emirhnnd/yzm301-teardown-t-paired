"""Diferansiyel test: G*Power arayüzünden toplanan vektörler (oracle/) ile CLI çıktısı.
N, n_total, df tam eşleşmeli; diğer değerler ekranda gösterilen 7 basamakta (tolerans 5e-8)."""
import csv, pathlib, pytest
from conftest import run_cli, ROOT

ROWS = list(csv.DictReader(open(ROOT / "oracle" / "oracle_vectors.csv")))
OK = [r for r in ROWS if r["critical_t"]]
ERR = [r for r in ROWS if not r["critical_t"]]
TOL = 5e-8

def _args(r):
    a = ["--test", "t-paired", "--mode", r["mode"], "--tails", r["tails"],
         "--dz", r["dz"], "--alpha", r["alpha"]]
    if r["mode"] == "a-priori":
        a += ["--power", r["power_in"]]
    else:
        a += ["--n_total", r["n_in"]]
    return a

@pytest.mark.parametrize("r", OK, ids=[f"v{r['id']}-{r['mode']}" for r in OK])
def test_vector(r):
    code, js, _ = run_cli(*_args(r))
    assert code == 0, js
    if r["mode"] == "a-priori":
        assert js["n_total"] == int(r["n_total"])
        assert abs(js["actual_power"] - float(r["actual_power"])) <= TOL
    else:
        assert "n_total" not in js
        assert abs(js["power"] - float(r["actual_power"])) <= TOL
    assert js["df"] == int(r["df"])
    assert abs(js["critical_t"] - float(r["critical_t"])) <= TOL
    assert abs(js["ncp"] - float(r["ncp"])) <= TOL

@pytest.mark.parametrize("r", ERR, ids=[f"v{r['id']}-error" for r in ERR])
def test_error_vector(r):
    code, js, _ = run_cli(*_args(r))
    assert code == 2
    assert "error" in js
    key = r["notes"].replace("ERROR: ", "").split("\n")[0]
    # mesajın ayırt edici parçası
    frag = {"27": "Power must be greater", "28": "effect size", "36": "admissible range (3, 2147483646)"}[r["id"]]
    assert frag in js["error"], js
