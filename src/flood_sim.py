"""Simulasi Monte Carlo risiko banjir kota pesisir (serial vs paralel).

Model sengaja dibuat sederhana agar mudah dipahami:
- Wilayah berupa grid elevasi (meter) yang landai dari pantai (baris 0) ke daratan.
- Setiap skenario = satu kombinasi hujan ekstrem + pasang laut acak.
- Sebuah sel banjir bila elevasinya lebih rendah dari tinggi muka air di barisnya.
- Probabilitas banjir sel = jumlah skenario yang membuatnya banjir / total skenario.
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

# ---------------------------------------------------------------- parameter model
RAIN_MU, RAIN_SIGMA = 4.3, 0.6      # hujan (mm) ~ lognormal
TIDE_MEAN, TIDE_STD = 0.8, 0.35     # pasang laut (m) ~ normal
RAIN_TO_M = 0.006                   # konversi hujan -> tinggi genangan (m per mm)
TIDE_DECAY = 25.0                   # pengaruh pasang meluruh terhadap jarak dari pantai (sel)


def make_terrain(size: int = 200, seed: int = 42) -> np.ndarray:
    """Buat DEM sintetis: landai dari pantai, ada noise dan satu alur sungai."""
    rng = np.random.default_rng(seed)
    rows = np.linspace(0.0, 6.0, size)[:, None]            # naik 0 -> 6 m ke arah daratan
    noise = rng.normal(0, 0.25, (size, size))
    # lembah sungai di tengah grid
    cols = np.arange(size)[None, :]
    river = -0.8 * np.exp(-((cols - size / 2) ** 2) / (2 * (size / 25) ** 2))
    return np.clip(rows + noise + river, 0.0, None)


def _water_levels(size: int, rain_mm: float, tide_m: float) -> np.ndarray:
    """Tinggi muka air tiap baris untuk satu skenario (vektor panjang `size`)."""
    dist = np.arange(size, dtype=float)
    return tide_m * np.exp(-dist / TIDE_DECAY) + rain_mm * RAIN_TO_M


def run_chunk(args: tuple) -> np.ndarray:
    """Jalankan `n` skenario dan kembalikan jumlah kejadian banjir tiap sel."""
    terrain, n, seed = args
    rng = np.random.default_rng(seed)
    size = terrain.shape[0]
    counts = np.zeros(terrain.shape, dtype=np.int64)
    for _ in range(n):
        rain = rng.lognormal(RAIN_MU, RAIN_SIGMA)
        tide = max(0.0, rng.normal(TIDE_MEAN, TIDE_STD))
        counts += terrain < _water_levels(size, rain, tide)[:, None]
    return counts


def _make_jobs(terrain, n_scenarios, n_chunks, seed):
    base, extra = divmod(n_scenarios, n_chunks)
    sizes = [base + (1 if i < extra else 0) for i in range(n_chunks)]
    return [(terrain, s, seed + i) for i, s in enumerate(sizes)]


def simulate_serial(terrain, n_scenarios, n_chunks=8, seed=7):
    """Versi serial: semua chunk diproses berurutan di satu proses."""
    t0 = time.perf_counter()
    total = sum(run_chunk(j) for j in _make_jobs(terrain, n_scenarios, n_chunks, seed))
    return total / n_scenarios, time.perf_counter() - t0


def simulate_parallel(terrain, n_scenarios, workers=2, n_chunks=8, seed=7):
    """Versi paralel: chunk dibagi ke beberapa proses (pola map-reduce)."""
    t0 = time.perf_counter()
    jobs = _make_jobs(terrain, n_scenarios, n_chunks, seed)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        total = sum(pool.map(run_chunk, jobs))
    return total / n_scenarios, time.perf_counter() - t0


def risk_summary(prob: np.ndarray, high=0.5, medium=0.1) -> dict:
    """Ringkas peta probabilitas ke kategori risiko."""
    n = prob.size
    return {
        "tinggi": float((prob >= high).sum() / n),
        "sedang": float(((prob >= medium) & (prob < high)).sum() / n),
        "rendah": float((prob < medium).sum() / n),
        "rata_rata_prob": float(prob.mean()),
    }


def ascii_map(prob: np.ndarray, width: int = 60) -> str:
    """Peta teks sederhana (rata-rata blok) untuk dilihat di terminal."""
    chars = " .:-=+*#%@"
    step = max(1, prob.shape[0] // width)
    h = prob.shape[0] // step
    w = prob.shape[1] // step
    small = prob[: h * step, : w * step].reshape(h, step, w, step).mean(axis=(1, 3))
    return "\n".join(
        "".join(chars[min(int(v * (len(chars) - 1) + 0.5), len(chars) - 1)] for v in row)
        for row in small
    )
