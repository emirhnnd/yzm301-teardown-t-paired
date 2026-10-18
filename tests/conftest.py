import json, os, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

def run_cli(*args):
    """CLI'yı ayrı süreçte çalıştırır; (çıkış kodu, ayrıştırılmış JSON, ham çıktı) döner."""
    env = dict(os.environ, PYTHONPATH=str(SRC))
    p = subprocess.run([sys.executable, "-m", "powerlab", *map(str, args)],
                       capture_output=True, text=True, env=env)
    out = p.stdout.strip()
    return p.returncode, json.loads(out), out
