import json
import pathlib
import re
import shlex
import subprocess
import sys

import pytest

from powerlab import cli, engine

SPEC = pathlib.Path(__file__).resolve().parents[1] / "SPEC.md"
TOL = 5e-8


def _tables():
    text = SPEC.read_text(encoding="utf-8")
    tables, cur, hdr = [], None, None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Examples:"):
            cur, hdr = [], None
            tables.append(cur)
            continue
        if cur is not None:
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if hdr is None:
                    hdr = cells
                else:
                    cur.append(dict(zip(hdr, cells)))
            elif s.startswith("```") or (s and not s.startswith("|")):
                cur = None
    return tables


TABLES = _tables()


def run(cmd):
    parts = shlex.split(cmd)
    assert parts[0] in ("gpower-clone", "powerlab")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli.main(parts[1:])
    out = buf.getvalue().strip()
    assert "\n" not in out
    return code, json.loads(out)


def test_tables_parsed():
    assert len(TABLES) == 3
    assert len(TABLES[0]) == 28 and len(TABLES[1]) == 9 and len(TABLES[2]) == 10


@pytest.mark.parametrize("row", TABLES[0], ids=lambda r: "-".join(r.values())[:40])
def test_a_priori(row):
    cmd = (f"gpower-clone --test t-paired --mode a-priori --tails {row['tails']} "
           f"--dz {row['dz']} --alpha {row['alpha']} --power {row['power']}")
    code, o = run(cmd)
    assert code == 0
    assert list(o) == ["ncp", "critical_t", "df", "n_total", "actual_power"]
    assert o["n_total"] == int(row["n_total"])
    assert o["df"] == int(row["df"])
    for k in ("actual_power", "critical_t", "ncp"):
        assert abs(o[k] - float(row[k])) <= TOL, k


@pytest.mark.parametrize("row", TABLES[1], ids=lambda r: "-".join(r.values())[:40])
def test_post_hoc(row):
    cmd = (f"gpower-clone --test t-paired --mode post-hoc --tails {row['tails']} "
           f"--dz {row['dz']} --alpha {row['alpha']} --n_total {row['n_total']}")
    code, o = run(cmd)
    assert code == 0
    assert o["df"] == int(row["df"])
    assert list(o) == ["ncp", "critical_t", "df", "power"]
    for k in ("critical_t", "ncp"):
        assert abs(o[k] - float(row[k])) <= TOL, k
    assert abs(o["power"] - float(row["power"])) <= TOL


@pytest.mark.parametrize("row", TABLES[2], ids=lambda r: r["mesaj_parçası"][:30])
def test_errors(row):
    code, o = run(row["komut"])
    assert code == 2
    assert list(o) == ["error", "code", "field"]
    assert row["mesaj_parçası"] in o["error"]
    assert o["code"] == row["kod"]


def test_error_exact_messages():
    assert engine.RANGE_MSG in run(
        "gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 2")[1]["error"]


def test_example_line_exact():
    cmd = "gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 34"
    r = subprocess.run([sys.executable, "-m", "powerlab"] + shlex.split(cmd)[1:],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.strip() == ('{"ncp":2.9154759474226504,"critical_t":2.0345152974493383,'
                                '"df":33,"power":0.8077775012792737}')


def test_boundaries():
    assert run("gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.05")[1]["n_total"] == 2
    o = run("gpower-clone --test t-paired --mode a-priori --tails 2 --dz -0.5 --alpha 0.05 --power 0.80")[1]
    assert (o["n_total"], round(o["critical_t"], 7), round(o["ncp"], 7), round(o["actual_power"], 7)) == (34, -2.0345153, -2.9154759, 0.8077775)
    assert engine.power(33, 2, 0.5, 0.05) < 0.80 <= engine.power(34, 2, 0.5, 0.05)
    assert engine.round_up_n(27 + 3e-11) == 27
    assert engine.round_up_n(27 + 6e-11) == 28
    # dz exactly 1e-5 valid (error is about N range, not effect size); 1e-6 invalid
    with pytest.raises(engine.PowerError, match="0.00001"):
        engine.a_priori(2, 1e-6, 0.05, 0.8)
    with pytest.raises(engine.PowerError, match="-20, 20"):
        engine.post_hoc(2, 21, 0.05, 10)


def test_no_aliases_strict():
    for bad in ("--d 0.5", "--n 34", "--sample-size 34"):
        code, o = run(f"powerlab --test t-paired --mode post-hoc --tails 2 --alpha 0.05 --n_total 34 {bad}")
        assert code == 2 and o["code"] == "UNKNOWN_PARAM"
    code, o = run("powerlab --test t-paired --mode post_hoc --tails 2 --dz 0.5 --alpha 0.05 --n_total 34")
    assert code == 2 and o["code"] == "UNSUPPORTED"
    assert run("powerlab --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n-total 34")[0] == 0


def test_full_precision_and_types():
    o = run("powerlab --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.8")[1]
    assert isinstance(o["n_total"], int) and isinstance(o["df"], int)
    assert o["ncp"] == 0.5 * 34 ** 0.5 and len(repr(o["critical_t"])) > 9


def test_version_and_exit_codes():
    code, o = run("powerlab --version")
    assert code == 0 and o["contract_version"] == "1.0.0"
