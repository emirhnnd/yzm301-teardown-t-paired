#!/usr/bin/env bash
# 60 sn demo: ekran kaydı için
set -e
echo "# a priori"; gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95
echo "# post hoc"; gpower-clone --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 34
echo "# sinir: guc = alfa"; gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.05
echo "# gecersiz"; gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0 --alpha 0.05 --power 0.8 || true
echo "# ajan"; python agent/agent.py "Önce ve sonra tansiyon, dz=0.5, alfa 0.05, güç %80, iki yönlü, kaç hasta?"
