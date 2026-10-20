<div align="center">

# 🌊 Simulasi Risiko Banjir Pesisir dengan Monte Carlo Paralel

**Studi Kasus: Menghubungkan Konsep High Performance Computing (HPC) dengan Persoalan Lokal**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Vectorized-013243?logo=numpy&logoColor=white)
![Parallel](https://img.shields.io/badge/Parallel-multiprocessing-2ea44f)
![Tests](https://img.shields.io/badge/Tests-4%20passed-brightgreen)

*Tugas Resume Sesi 2 — Informatics Practitioner Lecture Series*
*"Bridging Global Infrastructure to Address Local Challenge with HPC"*

</div>

---

## 📑 Daftar Isi
1. [Latar Belakang](#-latar-belakang)
2. [Hubungan dengan Materi Pemateri](#-hubungan-dengan-materi-pemateri)
3. [Rumusan Masalah & Tujuan](#-rumusan-masalah--tujuan)
4. [Batasan Masalah](#-batasan-masalah)
5. [Metode & Arsitektur](#-metode--arsitektur)
6. [Struktur Proyek](#-struktur-proyek)
7. [Cara Menjalankan](#-cara-menjalankan)
8. [Hasil & Analisis](#-hasil--analisis)
9. [Kesimpulan](#-kesimpulan)
10. [Pengembangan Lanjutan](#-pengembangan-lanjutan)

---

## 🎯 Latar Belakang

Banjir adalah salah satu bencana yang paling sering melanda wilayah pesisir. Penilaian risikonya tidak cukup dengan satu perhitungan, karena kejadian banjir dipengaruhi banyak faktor yang tidak pasti, misalnya curah hujan ekstrem dan pasang laut. Pendekatan **Monte Carlo** mengatasi hal ini dengan menjalankan ribuan skenario acak lalu menghitung seberapa sering sebuah lokasi tergenang.

Masalahnya, semakin banyak skenario dan semakin detail peta, semakin lama waktu komputasi. Di sinilah **komputasi paralel** (inti dari HPC) berperan: pekerjaan dibagi ke beberapa prosesor agar hasil diperoleh lebih cepat tanpa mengubah kualitas hasilnya.

## 🔗 Hubungan dengan Materi Pemateri

Materi Asst. Prof. Dr. Worawan Diaz Carballo menekankan bahwa HPC bernilai ketika diarahkan pada kebutuhan nyata, dan mahasiswa dapat berperan sebagai **integrator**. Studi kasus ini memetakan poin-poin tersebut:

| Poin dari materi | Penerapan di proyek ini |
|---|---|
| HPC menyelesaikan masalah kompleks lebih cepat | Simulasi ribuan skenario dibagi ke beberapa proses |
| Aspek kinerja: kecepatan, skalabilitas, efisiensi | Diukur sebagai waktu, *speedup*, dan efisiensi |
| Contoh nyata: prakiraan banjir (Bangladesh) | Kasus yang dipilih adalah risiko banjir pesisir |
| Simulasi untuk menguji skenario tanpa percobaan langsung | Skenario hujan dan pasang diuji secara virtual |
| Integrator: mengatur data, menjalankan, mengevaluasi hasil | Pipeline: buat data → simulasi → reduksi → evaluasi → laporan |
| Pemrograman paralel dan dokumentasi/GitHub | Kode paralel, tes otomatis, dan README ini |
| Data harus disesuaikan dengan kondisi lokal | Parameter model dapat dikalibrasi dengan data daerah |

## ❓ Rumusan Masalah & Tujuan

**Rumusan masalah**
1. Bagaimana memperkirakan probabilitas banjir tiap wilayah pesisir dengan pendekatan Monte Carlo?
2. Seberapa besar percepatan yang diperoleh dengan membagi simulasi ke beberapa proses?
3. Apakah versi paralel menghasilkan keluaran yang sama dengan versi serial?

**Tujuan**
- Membangun simulasi risiko banjir sederhana berbasis grid elevasi.
- Membandingkan waktu eksekusi serial dan paralel (*speedup* dan efisiensi).
- Memverifikasi bahwa hasil paralel identik dengan serial.

## 🚧 Batasan Masalah

1. Data elevasi adalah **sintetis** (dibuat program), bukan data DEM nyata.
2. Model banjir berupa **model ambang (bathtub)**: sel banjir bila elevasinya di bawah tinggi muka air. Aliran air, infiltrasi, dan drainase tidak disimulasikan.
3. Hanya dua faktor acak: **curah hujan** (lognormal) dan **pasang laut** (normal). Faktor lain seperti gelombang dan pasang-surut musiman diabaikan.
4. Pengaruh pasang laut meluruh secara eksponensial terhadap jarak dari pantai.
5. Paralelisasi memakai **multiprocessing pada satu mesin**, belum pada klaster HPC (SLURM/MPI).
6. Hasil bersifat **ilustrasi pembelajaran**, bukan untuk pengambilan keputusan mitigasi bencana.

## 🧠 Metode & Arsitektur

**Alur kerja**

```
 Buat DEM sintetis ──► Bagi N skenario jadi K chunk ──► Proses paralel (tiap chunk
                                                         punya seed sendiri)
                                                                │
 Peta risiko & benchmark ◄── Hitung probabilitas ◄── Reduksi (jumlahkan hitungan)
```

**Model per skenario**

- Hujan `R ~ Lognormal(4.3, 0.6)` mm, pasang `T ~ Normal(0.8, 0.35)` m
- Tinggi muka air pada baris ke-*r* dari pantai: `h(r) = T · e^(−r/25) + 0.006 · R`
- Sel banjir jika `elevasi < h(r)`
- Probabilitas sel = `jumlah skenario banjir / total skenario`

**Metrik kinerja** (sesuai materi)

- Speedup `S = T_serial / T_paralel`
- Efisiensi `E = S / jumlah_worker`

**Reproduksibilitas:** pembagian chunk dan seed dibuat identik pada versi serial dan paralel, sehingga hasil keduanya harus sama persis.

## 📁 Struktur Proyek

```
hpc-flood-montecarlo/
├── src/
│   ├── flood_sim.py        # model, simulasi serial & paralel, ringkasan risiko
│   └── run.py              # CLI benchmark dan penyimpan hasil
├── tests/
│   └── test_flood_sim.py   # 4 tes otomatis
├── results/
│   ├── probabilitas_banjir.csv
│   └── benchmark.json
├── requirements.txt
├── .gitignore
└── README.md
```

## ▶️ Cara Menjalankan

```bash
# 1. Clone dan masuk folder
git clone https://github.com/keniafeblia/Session-02-HPC.git
cd Session-02-HPC

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Jalankan simulasi (default: grid 200x200, 20.000 skenario)
python src/run.py

# Opsi kustom
python src/run.py --size 300 --scenarios 50000 --workers 4

# 4. Jalankan tes
pytest -q
```

## 📊 Hasil & Analisis

Contoh hasil pada mesin 2 inti (grid 200×200, 20.000 skenario):

| Metrik | Nilai |
|---|---|
| Waktu serial | ≈ 0,78 detik |
| Waktu paralel (2 worker) | ≈ 0,40 detik |
| Speedup | ≈ 1,96× |
| Efisiensi | ≈ 98% |
| Hasil serial = paralel | ✅ Identik |

**Ringkasan risiko wilayah:** tinggi (probabilitas ≥ 50%) ≈ 13,9%, sedang (10–50%) ≈ 6,6%, rendah (< 10%) ≈ 79,6%.

**Analisis singkat**
- Wilayah dekat pantai dan alur sungai paling rawan, sesuai model: elevasi rendah dan pengaruh pasang paling kuat.
- Speedup mendekati ideal karena setiap chunk berdiri sendiri (*embarrassingly parallel*), tanpa komunikasi antarproses selain reduksi akhir.
- Pada beban yang lebih kecil, overhead pembuatan proses akan mengurangi keuntungan paralel. Ini sejalan dengan materi bahwa skalabilitas dan efisiensi perlu diukur, bukan diasumsikan.

> Angka waktu bergantung pada perangkat keras; jalankan ulang di mesin Anda untuk nilai sendiri.

## ✅ Kesimpulan

Simulasi Monte Carlo risiko banjir terbukti cocok diparalelkan: waktu komputasi turun hampir setengahnya dengan 2 worker dan hasilnya identik dengan versi serial. Studi kasus ini menunjukkan peran integrator seperti yang disampaikan pemateri, yaitu menerjemahkan persoalan lokal (risiko banjir) menjadi alur kerja komputasi yang dapat dijalankan, diukur, dan dievaluasi.

## 🚀 Pengembangan Lanjutan

- Ganti DEM sintetis dengan data elevasi nyata daerah (mis. DEMNAS) dan kalibrasi parameter hujan serta pasang dari data BMKG.
- Tambahkan model aliran air dan drainase.
- Porting ke MPI (`mpi4py`) atau GPU (CuPy) lalu jalankan di klaster HPC dengan SLURM.
- Tambahkan visualisasi peta berwarna (matplotlib).

---

<div align="center">

### Disusun Oleh:

**Nama:** Kenia Nurma Feblia  
**NPM:** G1A023004  

</div>
