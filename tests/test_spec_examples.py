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
    assert len(TABLES[0]) == 28 and len(TABLES[1]) == 9 and len(TABLES[2]) == 6


@pytest.mark.parametrize("row", TABLES[0], ids=lambda r: "-".join(r.values())[:40])
def test_a_priori(row):
    cmd = (f"gpower-clone --test t-paired --mode a-priori --tails {row['tails']} "
           f"--dz {row['dz']} --alpha {row['alpha']} --power {row['power']}")
    code, o = run(cmd)
    assert code == 0
    assert o["n_total"] == int(row["n_total"]) == o["n1"] == o["n2"]
    assert o["df"] == int(row["df"])
    for k in ("actual_power", "critical", "ncp"):
        assert abs(o[k] - float(row[k])) <= TOL, k
    assert o["power"] == o["actual_power"]


@pytest.mark.parametrize("row", TABLES[1], ids=lambda r: "-".join(r.values())[:40])
def test_post_hoc(row):
    cmd = (f"gpower-clone --test t-paired --mode post-hoc --tails {row['tails']} "
           f"--dz {row['dz']} --alpha {row['alpha']} --n {row['n']}")
    code, o = run(cmd)
    assert code == 0
    assert o["df"] == int(row["df"])
    for k in ("critical", "ncp"):
        assert abs(o[k] - float(row[k])) <= TOL, k
    assert abs(o["actual_power"] - float(row["power"])) <= TOL


@pytest.mark.parametrize("row", TABLES[2], ids=lambda r: r["mesaj_parçası"][:30])
def test_errors(row):
    code, o = run(row["komut"])
    assert code != 0 and code == 2
    assert list(o) == ["error"]
    assert row["mesaj_parçası"] in o["error"]


def test_error_exact_messages():
    assert engine.RANGE_MSG in run(
        "gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 2")[1]["error"]


def test_example_line_exact():
    cmd = "gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 34"
    r = subprocess.run([sys.executable, "-m", "powerlab"] + shlex.split(cmd)[1:],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.strip() == ('{"n1":34,"n2":34,"n_total":34,"actual_power":0.8077775,'
                                '"power":0.8077775,"critical":2.0345153,"df":33,"ncp":2.9154759}')


def test_boundaries():
    assert run("gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.05")[1]["n_total"] == 2
    o = run("gpower-clone --test t-paired --mode a-priori --tails 2 --dz -0.5 --alpha 0.05 --power 0.80")[1]
    assert (o["n_total"], o["critical"], o["ncp"], o["actual_power"]) == (34, -2.0345153, -2.9154759, 0.8077775)
    assert engine.power(33, 2, 0.5, 0.05) < 0.80 <= engine.power(34, 2, 0.5, 0.05)
    assert engine.round_up_n(27 + 3e-11) == 27
    assert engine.round_up_n(27 + 6e-11) == 28
    # dz exactly 1e-5 valid (error is about N range, not effect size); 1e-6 invalid
    with pytest.raises(engine.PowerError, match="0.00001"):
        engine.a_priori(2, 1e-6, 0.05, 0.8)
    with pytest.raises(engine.PowerError, match="-20, 20"):
        engine.post_hoc(2, 21, 0.05, 10)


def test_aliases():
    a = run("powerlab --test t-paired --mode post_hoc --tails 2 --d 0.5 --alpha 0.05 --sample-size 34")[1]
    b = run("powerlab --test t-paired --mode posthoc --tails 2 --dz 0.5 --alpha 0.05 --n-total 34")[1]
    assert a == b
    assert run("powerlab --test t-paired --mode apriori --tails 2 --dz 0.5 --alpha 0.05 --power 0.8")[1]["n_total"] == 34
