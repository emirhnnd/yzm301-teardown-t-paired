"""Demo videosu üretir (ses yok; sahne etiketleri ve altyazı satırları var). ffmpeg ve Pillow gerekir.

Sahnelerdeki sayılar uydurma değildir:
  * terminal sahnesi gerçek komutları çalıştırır,
  * doğrulama ızgarası oracle/oracle_vectors.csv'yi okur ve her vektörü gerçek motorla yeniden hesaplar,
  * test sayıları `python -m pytest -q tests` çıktısından alınmıştır (109 test, 2026-10-22).
Çalıştırma:  pip install -e ".[test]" pillow ; python demo/make_video.py   ->  demo/demo.mp4
"""
import csv
import os
import pathlib
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from powerlab.cli import compute  # noqa: E402

W, H, FPS = 1920, 1080, 10
OUT = ROOT / "demo" / "demo.mp4"
FR = pathlib.Path(os.environ.get("DEMO_FRAMES", "/tmp/powerlab_demo_frames"))
FD = "/usr/share/fonts/truetype/dejavu/"


def F(name, size):
    return ImageFont.truetype(FD + name, size)


def SANS(s): return F("DejaVuSans.ttf", s)
def SANS_B(s): return F("DejaVuSans-Bold.ttf", s)
def MONO(s): return F("DejaVuSansMono.ttf", s)
def MONO_B(s): return F("DejaVuSansMono-Bold.ttf", s)


BG = (13, 17, 26); PANEL = (24, 30, 44); TXT = (232, 236, 245); MUTED = (140, 152, 175)
TEAL = (45, 212, 191); AMBER = (251, 191, 36); GREEN = (74, 222, 128); RED = (248, 113, 113); LINEC = (48, 58, 80)

# test sayıları: python -m pytest -q tests (2026-10-22)
N_TESTS, N_SCALE, N_PARITY = 109, 560, 40
LLM_EASY, LLM_HARD = "40/40", "29/30"

SEGS = []  # (PIL image, kare sayısı)


def canvas():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def paragraph(d, xy, text, font, fill, maxw, lh):
    x, y = xy
    for ln in wrap(d, text, font, maxw):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def chrome(d, idx, label, sub=None):
    """Sol üstte numaralı sahne etiketi, altta tek satır altyazı, üstte ilerleme çizgisi."""
    d.rectangle([0, 0, int(W * idx / 7), 6], fill=TEAL)
    d.rounded_rectangle([80, 56, 80 + 40 + int(d.textlength(label, font=SANS_B(26))) + 36, 106], radius=25, fill=PANEL, outline=LINEC)
    d.text((100, 81), "%02d" % idx, font=MONO_B(26), fill=TEAL, anchor="lm")
    d.text((150, 81), label, font=SANS_B(26), fill=TXT, anchor="lm")
    if sub:
        d.text((80, H - 90), sub, font=SANS(30), fill=MUTED)


def hold(im, sec):
    SEGS.append((im, max(1, int(round(sec * FPS)))))


def fmt(v, nd=7):
    return ("%.*f" % (nd, v)).replace(".", ",")


# ------------------------------------------------------------ gerçek doğrulama
def verify_rows():
    rows = []
    for r in csv.DictReader(open(ROOT / "oracle" / "oracle_vectors.csv", encoding="utf-8")):
        mode = r["mode"]
        kw = dict(mode=mode, tails=int(r["tails"]), dz=float(r["dz"]), alpha=float(r["alpha"]))
        if mode == "a-priori":
            kw["power"] = float(r["power_in"])
        else:
            kw["n_total"] = int(r["n_in"])
        res = compute(**kw)
        note = r["notes"]
        if note.startswith("ERROR:"):
            exp = note[len("ERROR: "):].split("\n")[0]
            ok = "error" in res and res["error"].startswith(exp[:40])
            kind = "hata"
        else:
            ok = ("error" not in res
                  and abs(res["power" if mode == "post-hoc" else "actual_power"] - float(r["actual_power"])) <= 5e-8
                  and abs(res["critical_t"] - float(r["critical_t"])) <= 5e-8
                  and abs(res["ncp"] - float(r["ncp"])) <= 5e-8
                  and res["df"] == int(r["df"])
                  and (mode == "post-hoc" or res["n_total"] == int(r["n_total"])))
            kind = mode
        rows.append(dict(id=int(r["id"]), ok=ok, kind=kind))
    return rows


ROWS = verify_rows()
N_OK = sum(1 for r in ROWS if r["ok"])
N_APRI = sum(1 for r in ROWS if r["kind"] == "a-priori")
N_POST = sum(1 for r in ROWS if r["kind"] == "post-hoc")
N_ERR = sum(1 for r in ROWS if r["kind"] == "hata")


# ------------------------------------------------------------------- sahneler
def scene_question():
    im, d = canvas()
    chrome(d, 1, "SORU")
    d.text((80, 240), "Önce ve sonra tansiyon:", font=SANS_B(92), fill=TXT)
    d.text((80, 350), "kaç hasta gerekir?", font=SANS_B(92), fill=TEAL)
    y = paragraph(d, (80, 520), "Eşleştirilmiş t testinin örneklem büyüklüğünü hesaplayan program elimizde yalnızca .exe olarak var: "
                  "kaynak kodu, komut satırı ve yapay zekâ aracı yok.", SANS(38), MUTED, 1450, 56)
    d.text((80, y + 50), "Emirhan Dede · Yazılım Gerçekleme ve Test · YZM301 · Grup 15 · K2", font=SANS(28), fill=MUTED)
    chrome(d, 1, "SORU", "Hedef: G*Power 3.1.9.7 · t testi, eşleştirilmiş ortalamalar (t-paired)")
    hold(im, 6)


def run_cmd(argv):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    p = subprocess.run([sys.executable, "-m", "powerlab"] + argv, capture_output=True, text=True, env=env, cwd=ROOT)
    return p.stdout.strip(), p.returncode


def scene_cli():
    base = ["--test", "t-paired"]
    cmds = [
        ("# etki dz=0,5, alfa=0,05, güç %80: kaç çift?", base + ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "0.80"]),
        ("# aynı soru, güç %95", base + ["--mode", "a-priori", "--tails", "2", "--dz", "0.5", "--alpha", "0.05", "--power", "0.95"]),
        ("# dz = 0 anlamsız: hata JSON'u ve çıkış kodu", base + ["--mode", "a-priori", "--tails", "2", "--dz", "0", "--alpha", "0.05", "--power", "0.8"]),
    ]
    lines = []
    mono = MONO(26)
    G, CY, TY = (120, 230, 150), (125, 205, 255), (130, 142, 165)

    def draw(cur=None):
        im, d = canvas()
        d.rounded_rectangle([80, 150, 1840, 880], radius=18, fill=(8, 11, 18), outline=LINEC)
        d.rectangle([80, 150, 1840, 196], fill=PANEL)
        for i, c in enumerate([(248, 113, 113), (251, 191, 36), (74, 222, 128)]):
            d.ellipse([104 + i * 34, 165, 124 + i * 34, 185], fill=c)
        d.text((230, 173), "gpower-clone · tek satır JSON", font=SANS(22), fill=MUTED, anchor="lm")
        vis = (lines + ([cur] if cur else []))[-15:]
        for i, (t, c) in enumerate(vis):
            d.text((110, 222 + i * 40), t, font=mono, fill=c)
        chrome(d, 2, "TEK KOMUT", "Gerçek komutlar, gerçek çıktılar. Hata durumunda çıkış kodu 2.")
        return im

    for note, argv in cmds:
        out, rc = run_cmd(argv)
        lines.append((note, TY))
        hold(draw(), 0.4)
        shown = "gpower-clone " + " ".join(argv)
        for k in range(10, len(shown) + 10, 10):
            hold(draw(("$ " + shown[:k], G)), 0.08)
        lines.append(("$ " + shown, G))
        for ol in out.splitlines():
            while ol:
                lines.append((ol[:100], CY))
                ol = ol[100:]
        if rc != 0:
            lines.append(("çıkış kodu: %d" % rc, TXT))
        hold(draw(), 1.2)
        lines.append(("", TXT))


def box(d, x, y, w, h, title, sub, color):
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=PANEL, outline=color, width=3)
    d.text((x + w // 2, y + 46), title, font=SANS_B(27), fill=TXT, anchor="mm")
    paragraph(d, (x + 22, y + 90), sub, SANS(21), MUTED, w - 44, 30)


def arrow(d, x1, x2, y, color=MUTED):
    d.line([x1, y, x2, y], fill=color, width=4)
    d.polygon([(x2, y), (x2 - 16, y - 10), (x2 - 16, y + 10)], fill=color)


def scene_method():
    im, d = canvas()
    chrome(d, 3, "YÖNTEM")
    d.text((80, 160), "İki ayrı oturum, aralarında yalnızca bir belge", font=SANS_B(58), fill=TXT)
    bw, bh, gap, y = 262, 230, 50, 400
    items = [
        ("GPowerNT.exe", "sadece derlenmiş program; kaynak yok", MUTED),
        ("REA + Ghidra", "Oturum 1: binary'yi inceler", TEAL),
        ("LEDGER + SPEC", "kanıt defteri ve şartname", AMBER),
        ("Yazan ajan", "Oturum 2: yalnızca SPEC.md'yi görür", TEAL),
        ("Motor, CLI, MCP", "yeniden yazılmış hesap", MUTED),
        ("Karşılaştırma", "aynı girdi, iki program", GREEN),
    ]
    x = 80
    xs = []
    for t, s, c in items:
        box(d, x, y, bw, bh, t, s, c)
        xs.append(x)
        x += bw + gap
    for i in range(len(items) - 1):
        arrow(d, xs[i] + bw + 6, xs[i + 1] - 6, y + bh // 2)
    wall = xs[3] - gap // 2
    for yy in range(y - 60, y + bh + 70, 24):
        d.line([wall, yy, wall, yy + 12], fill=AMBER, width=4)
    d.text((wall, y - 90), "temiz oda duvarı", font=SANS_B(24), fill=AMBER, anchor="mm")
    tags = [("[REA]", "binary'den, adresle"), ("[DOK]", "yayımlı kaynakta var"), ("[KÂHİN]", "G*Power penceresinde görüldü"), ("[AJAN]", "çıkarım, testle sınanır")]
    xx = 80
    for tg, ex in tags:
        d.text((xx, 760), tg, font=MONO_B(30), fill=TEAL)
        d.text((xx, 802), ex, font=SANS(24), fill=MUTED)
        xx += 440
    chrome(d, 3, "YÖNTEM", "Her iddia bir kanıt etiketi taşır; yanlış çıkarımlar ayrıca kayda geçer.")
    hold(im, 9)


def scene_evidence():
    cards = [
        ("Yuvarlama", "0x496a20", "Bulunan kesirli N önce 10 ondalığa yuvarlanıyor, sonra yukarı. Kök bir tamsayının 5e-11 kadar üstündeyse o tamsayı seçiliyor."),
        ("N nasıl aranıyor", "0x496aa0", "Brent kök bulucu, aralık [2, 100]; hedef aşılmazsa ×1,6 ile genişliyor; en çok 300 yineleme."),
        ("Sınırlar", "0x4da690", "a priori'de N = 2 olabilir, post hoc'ta N en az 3 olmalı. Güç = alfa geçerli, dz = 0 hata."),
    ]
    im, d = canvas()
    chrome(d, 4, "İKİLİDEN ÇIKANLAR")
    d.text((80, 160), "Kılavuzda hiç geçmeyen üç davranış", font=SANS_B(58), fill=TXT)
    cw, gap, y = 560, 40, 300
    for i, (t, addr, txt) in enumerate(cards):
        x = 80 + i * (cw + gap)
        d.rounded_rectangle([x, y, x + cw, y + 480], radius=20, fill=PANEL, outline=LINEC)
        d.text((x + 36, y + 40), t, font=SANS_B(40), fill=TEAL)
        d.text((x + 36, y + 110), "adres " + addr, font=MONO_B(26), fill=AMBER)
        paragraph(d, (x + 36, y + 170), txt, SANS(29), TXT, cw - 72, 44)
    chrome(d, 4, "İKİLİDEN ÇIKANLAR", "Üçü de [REA] etiketli; ayrıntı ve diğer adresler LEDGER.md'de.")
    hold(im, 8)


def scene_grid():
    n = len(ROWS)
    cols, size, gap = 10, 118, 16
    x0, y0 = 290, 250
    steps = 40
    for s in range(steps + 1):
        im, d = canvas()
        chrome(d, 5, "40 PENCERE")
        d.text((80, 150), "G*Power'dan elle alınan 40 sonuç, motorla karşılaştırıldı", font=SANS_B(46), fill=TXT)
        done = int(n * s / steps)
        for i, r in enumerate(ROWS):
            cx = x0 + (i % cols) * (size + gap)
            cy = y0 + (i // cols) * (size + gap)
            on = i < done
            col = (GREEN if r["ok"] else RED) if on else PANEL
            d.rounded_rectangle([cx, cy, cx + size, cy + size], radius=14, fill=col, outline=LINEC)
            d.text((cx + size // 2, cy + size // 2), "V%02d" % r["id"], font=SANS_B(30), fill=(8, 20, 14) if on else MUTED, anchor="mm")
        ok_now = sum(1 for r in ROWS[:done] if r["ok"])
        d.text((x0, 830), "%d / %d" % (ok_now, n), font=SANS_B(70), fill=GREEN if ok_now == done else RED)
        d.text((x0 + 320, 838), "birebir", font=SANS(34), fill=MUTED)
        d.text((x0 + 320, 882), "a priori %d · post hoc %d · hata mesajı %d" % (N_APRI, N_POST, N_ERR), font=SANS(26), fill=MUTED)
        chrome(d, 5, "40 PENCERE", "Sayısal sonuçlar 5e-8 içinde; N, df ve hata mesajları tam eşleşiyor." if s == steps else "Her kare bir G*Power penceresi + bir motor çalıştırması.")
        SEGS.append((im, 1 if s < steps else 20))


def scene_mistakes():
    items = [
        ("CEff_T_PairedMeans", "ajan bunu hesap motoru sandı; aslında bir iletişim kutusuydu. Doğru sınıf: PowerTPairedMean.", "H1"),
        ("Brent'i çağıran ilk işlev", "N çözücü sanıldı; aslında alfa çözücüydü. Gerçek N çözücü başka bir yuvadaydı.", "H3"),
        ("scipy nct.cdf", "bazı (df, ncp) değerlerinde nan döndürüyor; 560 vektörlük test bunu yakaladı.", "H5"),
    ]
    im, d = canvas()
    chrome(d, 6, "AJAN YANILDI")
    d.text((80, 160), "Yapay zekâ 5 kez yanlış çıkarım yaptı", font=SANS_B(58), fill=TXT)
    d.text((80, 245), "Üçü burada; hepsi nasıl yakalandığıyla HALLUCINATIONS.md'de.", font=SANS(30), fill=MUTED)
    y = 350
    for t, txt, tag in items:
        d.rounded_rectangle([80, y, 1840, y + 150], radius=18, fill=PANEL, outline=LINEC)
        d.text((120, y + 38), t, font=MONO_B(32), fill=AMBER)
        paragraph(d, (120, y + 86), txt, SANS(27), TXT, 1500, 38)
        d.text((1800, y + 38), tag, font=MONO_B(30), fill=TEAL, anchor="ra")
        y += 180
    chrome(d, 6, "AJAN YANILDI", "Kanıtsız çıkarım [AJAN] etiketiyle kalır; testle doğrulanana dek şüphelidir.")
    hold(im, 7)


def scene_close():
    im, d = canvas()
    chrome(d, 7, "DENE")
    stats = [(str(N_TESTS), "test"), ("%d/%d" % (N_SCALE, N_SCALE), "ölçek"), ("%d/%d" % (N_PARITY, N_PARITY), "CLI = MCP"), (LLM_EASY + " · " + LLM_HARD, "ajan")]
    x = 80
    for big, lab in stats:
        d.text((x, 190), big, font=SANS_B(64), fill=TEAL)
        d.text((x, 275), lab, font=SANS(30), fill=MUTED)
        x += 430
    d.rounded_rectangle([80, 400, 1840, 700], radius=18, fill=(8, 11, 18), outline=LINEC)
    for i, (t, c) in enumerate([
        ("git clone https://github.com/emirhnnd/yzm301-teardown-t-paired", (120, 230, 150)),
        ("pip install -e \".[test,mcp]\" && python -m pytest -q tests", (120, 230, 150)),
        ("gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.80", (125, 205, 255)),
    ]):
        d.text((120, 450 + i * 70), ("$ " if i < 3 else "") + t, font=MONO(28), fill=c)
    d.text((80, 780), "Atıf: Faul, Erdfelder, Lang ve Buchner (2007, 2009). Bu proje G*Power değildir ve onun kodunu içermez.", font=SANS(25), fill=MUTED)
    chrome(d, 7, "DENE", "Kaynak kod, kanıt defteri ve testler açık.")
    hold(im, 8)


def mean_abs_diff(a, b):
    a = list(a.resize((96, 54)).tobytes())
    b = list(b.resize((96, 54)).tobytes())
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


if __name__ == "__main__":
    scene_question(); scene_cli(); scene_method(); scene_evidence(); scene_grid(); scene_mistakes(); scene_close()
    shutil.rmtree(FR, ignore_errors=True)
    FR.mkdir(parents=True)
    n_out, prev = 0, None
    for im, n in SEGS:
        for k in range(n):
            if k == 0 and prev is not None and mean_abs_diff(prev, im) > 12:  # sahne geçişi: 2 ara kare
                for a in (0.33, 0.66):
                    Image.blend(prev, im, a).save(FR / ("f%05d.png" % n_out), compress_level=1)
                    n_out += 1
            im.save(FR / ("f%05d.png" % n_out), compress_level=1)
            n_out += 1
            prev = im
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FR / "f%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT)], check=True)
    print("kare:", n_out, "süre ≈ %.1f sn" % (n_out / FPS), "· birebir:", N_OK, "/", len(ROWS))
