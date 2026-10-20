"""CLI: jalankan simulasi serial vs paralel, cetak benchmark, simpan hasil ke results/."""

import argparse
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from flood_sim import (ascii_map, make_terrain, risk_summary,  # noqa: E402
                       simulate_parallel, simulate_serial)


def main():
    p = argparse.ArgumentParser(description="Simulasi Monte Carlo risiko banjir (serial vs paralel)")
    p.add_argument("--size", type=int, default=200, help="ukuran grid (size x size)")
    p.add_argument("--scenarios", type=int, default=20000, help="jumlah skenario Monte Carlo")
    p.add_argument("--workers", type=int, default=os.cpu_count() or 2, help="jumlah proses paralel")
    p.add_argument("--out", default="results", help="folder keluaran")
    a = p.parse_args()

    terrain = make_terrain(a.size)
    print(f"Grid {a.size}x{a.size} | skenario {a.scenarios} | workers {a.workers}")

    prob_s, t_s = simulate_serial(terrain, a.scenarios)
    prob_p, t_p = simulate_parallel(terrain, a.scenarios, workers=a.workers)

    identik = bool(np.allclose(prob_s, prob_p))
    speedup = t_s / t_p
    efisiensi = speedup / a.workers
    summary = risk_summary(prob_p)

    print(f"\nSerial   : {t_s:.2f} detik")
    print(f"Paralel  : {t_p:.2f} detik")
    print(f"Speedup  : {speedup:.2f}x | Efisiensi: {efisiensi:.0%} | Hasil identik: {identik}")
    print("Luas wilayah -> tinggi {tinggi:.1%}, sedang {sedang:.1%}, rendah {rendah:.1%}".format(**summary))
    print("\nPeta probabilitas banjir (atas = pantai, ' ' aman, '@' sangat rawan):\n")
    print(ascii_map(prob_p))

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "probabilitas_banjir.csv"), "w", newline="") as f:
        csv.writer(f).writerows(np.round(prob_p, 4).tolist())
    with open(os.path.join(a.out, "benchmark.json"), "w") as f:
        json.dump({"grid": a.size, "skenario": a.scenarios, "workers": a.workers,
                   "waktu_serial_s": round(t_s, 3), "waktu_paralel_s": round(t_p, 3),
                   "speedup": round(speedup, 3), "efisiensi": round(efisiensi, 3),
                   "hasil_identik": identik, "ringkasan_risiko": summary}, f, indent=2)
    print(f"\nHasil disimpan di folder '{a.out}/'")


if __name__ == "__main__":
    main()
