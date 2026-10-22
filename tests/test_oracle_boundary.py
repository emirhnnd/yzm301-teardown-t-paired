"""Sınır vektörleri (oracle/oracle_boundary.csv): G*Power arayüzünden 22 Ekim'de toplandı (hepsi tek yönlü).
b4 (dz = 1e-5) bilinen sapmadır: G*Power N=61823520102 verir (gerçek güç 0.7999842, hedefin altında); klon matematiksel kökü verir."""
import csv, pytest
from conftest import run_cli, ROOT

ROWS = list(csv.DictReader(open(ROOT / "oracle" / "oracle_boundary.csv")))
TOL = 5e-8

def _args(r):
    a = ["--test", "t-paired", "--mode", r["mode"], "--tails", r["tails"], "--dz", r["dz"], "--alpha", r["alpha"]]
    return a + (["--power", r["power_in"]] if r["mode"] == "a-priori" else ["--n_total", r["n_in"]])

@pytest.mark.parametrize("r", ROWS, ids=[r["id"] for r in ROWS])
def test_boundary_vector(r):
    code, js, _ = run_cli(*_args(r))
    if r["id"] == "b3":
        assert code == 2 and js["code"] == "OUT_OF_RANGE" and js["error"] == "Effect size d is outside the admissible range (-20, 20)"
        return
    assert code == 0, js
    if r["id"] == "b4":
        pytest.xfail("G*Power'ın çok büyük N'deki sayısal kesinlik sınırı; SPEC §8")
    if r["mode"] == "a-priori":
        assert js["n_total"] == int(r["n_total"])
        assert abs(js["actual_power"] - float(r["actual_power"])) <= TOL
    else:
        assert abs(js["power"] - float(r["actual_power"])) <= TOL
    assert js["df"] == int(r["df"])
    assert abs(js["critical_t"] - float(r["critical_t"])) <= TOL
    assert abs(js["ncp"] - float(r["ncp"])) <= 5e-7
