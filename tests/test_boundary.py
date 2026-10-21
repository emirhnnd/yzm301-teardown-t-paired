"""Sınır değerler: motor ve CLI."""
import math, pytest
from scipy import stats, optimize
from conftest import run_cli

def test_power_equals_alpha_gives_n2():
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",0.05)
    assert code == 0 and js["n_total"] == 2 and abs(js["actual_power"] - 0.0619486) < 5e-8

def test_power_below_alpha_errors():
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",0.04)
    assert code != 0 and "Power must be greater" in js["error"]

def test_dz_exactly_1e5_not_rejected_by_effect_rule():
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.00001,"--alpha",0.05,"--power",0.8)
    # N çok büyük olacağı için üst sınır hatası da olabilir; dz kuralı mesajı OLMAMALI
    assert "effect size be greater" not in json_error(js)

def json_error(js): return js.get("error", "")

def test_dz_just_below_1e5_rejected():
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.000009,"--alpha",0.05,"--power",0.8)
    assert code != 0 and "effect size be greater" in js["error"]

def test_posthoc_n2_rejected_n3_ok():
    c2, j2, _ = run_cli("--test","t-paired","--mode","post-hoc","--tails",2,"--dz",0.5,"--alpha",0.05,"--n",2)
    c3, j3, _ = run_cli("--test","t-paired","--mode","post-hoc","--tails",2,"--dz",0.5,"--alpha",0.05,"--n",3)
    assert c2 != 0 and c3 == 0 and abs(j3["actual_power"] - 0.0841071) < 5e-8

def test_negative_dz_signs():
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",1,"--dz",-0.5,"--alpha",0.05,"--power",0.8)
    assert js["n_total"] == 27 and js["critical"] < 0 and js["ncp"] < 0

def test_one_tailed_vs_two_tailed_n():
    c1, j1, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",1,"--dz",0.5,"--alpha",0.05,"--power",0.8)
    c2, j2, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",0.8)
    assert j1["n_total"] < j2["n_total"]

def test_previous_n_misses_target():
    # N-1 hedefi sağlamaz, N sağlar
    from test_scale_scipy import power
    code, js, _ = run_cli("--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",0.8)
    n = js["n_total"]
    assert power(n - 1, 2, 0.5, 0.05) < 0.8 <= power(n, 2, 0.5, 0.05)

def test_n_star_just_above_integer():
    """N* bir tamsayının 3e-11 üstündeyse G*Power'ın 10 ondalık yuvarlaması o tamsayıyı seçer."""
    def r(x): return math.ceil(math.floor(x * 1e10 + 0.5) / 1e10)
    assert r(34 + 3e-11) == 34
    assert r(34 + 3e-10) == 35
    assert r(34.0) == 34

def test_invalid_inputs():
    bad = [
        ["--test","t-paired","--mode","post-hoc","--tails",3,"--dz",0.5,"--alpha",0.05,"--n",20],
        ["--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",1.5,"--power",0.8],
        ["--test","t-paired","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",1.2],
        ["--test","t2-indep","--mode","a-priori","--tails",2,"--dz",0.5,"--alpha",0.05,"--power",0.8],
        ["--test","t-paired","--mode","a-priori","--tails",2,"--alpha",0.05,"--power",0.8],
        ["--test","t-paired","--mode","post-hoc","--tails",2,"--dz",0.5,"--alpha",0.05],
        ["--test","t-paired","--mode","post-hoc","--tails",2,"--dz",0.5,"--alpha",0.05,"--n",2147483647],
        ["--test","t-paired","--mode","a-priori","--tails",2,"--dz","abc","--alpha",0.05,"--power",0.8],
    ]
    for a in bad:
        code, js, raw = run_cli(*a)
        assert code != 0 and "error" in js, (a, raw)


def test_ratio_flag_accepted_and_ignored():
    """Ortak test düzeneği --ratio 1 gönderebilir; sonuç değişmemeli."""
    import subprocess, sys, json, os, pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    base = [sys.executable, "-m", "powerlab", "--test", "t-paired", "--mode", "a-priori", "--tails", "2", "--d", "0.5", "--alpha", "0.05", "--power", "0.95"]
    a = subprocess.run(base, capture_output=True, text=True, env=env)
    b = subprocess.run(base + ["--ratio", "1"], capture_output=True, text=True, env=env)
    assert a.returncode == 0 and b.returncode == 0
    assert json.loads(a.stdout) == json.loads(b.stdout)
