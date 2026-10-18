"""CLI ve MCP aynı girdide aynı çıktıyı vermeli (MCP gerçek stdio istemcisiyle çağrılır)."""
import asyncio, csv, json, os, sys
import pytest
from conftest import run_cli, ROOT, SRC

ROWS = list(csv.DictReader(open(ROOT / "oracle" / "oracle_vectors.csv")))

def _cli_args(r):
    a = ["--test", "t-paired", "--mode", r["mode"], "--tails", r["tails"], "--dz", r["dz"], "--alpha", r["alpha"]]
    return a + (["--power", r["power_in"]] if r["mode"] == "a-priori" else ["--n", r["n_in"]])

def _mcp_args(r):
    d = dict(mode=r["mode"], tails=int(r["tails"]), dz=float(r["dz"]), alpha=float(r["alpha"]))
    if r["mode"] == "a-priori": d["power"] = float(r["power_in"])
    else: d["n"] = int(r["n_in"])
    return d

async def _mcp_all(rows):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    sp = StdioServerParameters(command=sys.executable, args=["-m", "powerlab_mcp.server"], env=dict(os.environ, PYTHONPATH=str(SRC)))
    out = []
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            assert [t.name for t in tools.tools] == ["power_analysis_t_paired"]
            for row in rows:
                res = await s.call_tool("power_analysis_t_paired", _mcp_args(row))
                out.append(json.loads(res.content[0].text))
    return out

def test_parity_all_oracle_vectors():
    mcp_out = asyncio.run(_mcp_all(ROWS))
    for row, m in zip(ROWS, mcp_out):
        code, js, _ = run_cli(*_cli_args(row))
        assert m == js, (row["id"], m, js)
