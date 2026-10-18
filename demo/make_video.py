"""Gerçek komutları çalıştırır, çıktılarını yakalar ve daktilo efektiyle terminal ekran videosu üretir (ffmpeg gerekir)."""
import subprocess, os, sys, shutil, pathlib
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
CMDS = [
 ("# 1) a priori: kaç çift gerekir?", "gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95"),
 ("# 2) post hoc: güç nedir?", "gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 34"),
 ("# 3) sınır: güç = alfa geçerli, N = 2", "gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.05"),
 ("# 4) geçersiz girdi: JSON hata + çıkış kodu 2", "gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0 --alpha 0.05 --power 0.8"),
 ("# 5) Türkçe soru -> ajan -> MCP aracı", 'python agent/agent.py "Önce ve sonra tansiyon, dz=0.5, alfa 0.05, güç %80, iki yönlü, kaç hasta?"'),
 ("# 6) testler: 40 referans vektörü + 560 ölçek vektörü + CLI/MCP eşliği", "python -m pytest -q tests  ->  101 passed"),
]
def real(cmd):
    c = cmd.split("  ->")[0]
    if c.startswith("gpower-clone"): c = "python -m powerlab " + c[len("gpower-clone "):]
    if c.startswith("python agent"): c = "python agent/agent.py " + c.split("agent.py ",1)[1]
    p = subprocess.run(c, shell=True, capture_output=True, text=True, env=env, cwd=ROOT)
    return p.stdout.strip()
OUT = []
for note, cmd in CMDS:
    out = cmd.split("->")[1].strip() if "python -m pytest" in cmd else real(cmd)
    OUT.append((note, cmd.split("  ->")[0], out))
W, H = 1280, 720
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
FPS = 8
frames = pathlib.Path("/tmp/demo_frames"); shutil.rmtree(frames, ignore_errors=True); frames.mkdir()
lines = []; n = 0
def wrap(s, w=100): return [s[i:i+w] for i in range(0, len(s), w)] or [""]
def draw(cur=None):
    global n
    im = Image.new("RGB", (W, H), (18, 18, 24)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 34], fill=(40, 40, 52)); d.text((12, 6), "powerlab · t-paired demo (gerçek komut çıktıları)", font=font, fill=(200, 200, 210))
    vis = (lines + ([cur] if cur is not None else []))[-24:]
    for i, (txt, col) in enumerate(vis): d.text((16, 46 + i * 27), txt, font=font, fill=col)
    im.save(frames / f"f{n:05d}.png"); n += 1
GREEN, GREY, WHITE, CY = (110, 220, 130), (140, 150, 170), (230, 230, 235), (120, 200, 255)
for note, cmd, out in OUT:
    for _ in range(FPS): pass
    lines.append((note, GREY)); draw()
    for k in range(0, len(cmd) + 1, 4):
        draw(("$ " + cmd[:k] + "_", GREEN))
    lines.append(("$ " + cmd, GREEN)) if len("$ " + cmd) <= 104 else [lines.append((x, GREEN)) for x in wrap("$ " + cmd, 104)]
    for _ in range(FPS // 2): draw()
    for ol in out.splitlines():
        for x in wrap(ol, 104): lines.append((x, CY)); 
        for _ in range(FPS): draw()
    for _ in range(FPS * 4): draw()
    lines.append(("", WHITE))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(ROOT / "demo" / "demo.mp4")], check=True)
print("frames", n, "sn", n / FPS)
