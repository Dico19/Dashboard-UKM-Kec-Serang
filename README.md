# 📊 UKM Dashboard — Evaluasi Kinerja Keuangan UKM Kecamatan Serang (Streamlit)

Aplikasi **Streamlit** untuk mengevaluasi kinerja keuangan UKM berbasis **ROI, Profit Margin, Growth Rate** dan menghasilkan **Skor KPI (0–100)**, lengkap dengan upload data, filter global, analisis visual, data quality, tabel detail, rekomendasi, serta export **Excel & PDF** (dengan logo).

---

## 🧑‍💻 Developer
  **Dicoding**

---

## ✅ Fitur Utama
- **Upload Excel (.xlsx)** + **Manual Input** (opsional)
- Mode data: **Hanya Upload / Hanya Manual / Gabung Upload + Manual**
- **Filter Global** (bidang usaha)
- Halaman analisis: **Dashboard, Data Quality, Grafik KPI, Pertumbuhan, Rata-rata Bidang, Tabel KPI, Generate Report, Rekomendasi Kecamatan, Metodologi**
- Export laporan: **Excel & PDF**

---

## 🧠 Cara Kerja (Alur + Perhitungan) — Ringkas
1) **Input Data**
   - Upload Excel atau isi Manual Input.
   - Pilih mode sumber data: *Hanya Upload / Hanya Manual / Gabung*.
   - Atur **Filter Global** (Bidang Usaha) untuk menentukan data yang ditampilkan di halaman lain.

2) **Hitung KPI**
   - **Laba Bersih (Rp)** = Pendapatan Tahun Ini − Total Biaya  
   - **ROI (%)** = (Laba Bersih / Total Modal/Investasi) × 100  
   - **Profit Margin (%)** = (Laba Bersih / Pendapatan Tahun Ini) × 100  
   - **Growth Rate (%)** = ((Pendapatan Tahun Ini − Pendapatan Tahun Lalu) / Pendapatan Tahun Lalu) × 100  
   - **Cost Ratio** = Total Biaya / Pendapatan Tahun Ini *(lebih kecil = lebih efisien)*

3) **Validasi Data (Data Quality)**
   Data dianggap **Tidak Valid** jika:
   - Modal/Investasi kosong atau ≤ 0
   - Pendapatan Tahun Ini kosong atau ≤ 0
   - Pendapatan Tahun Lalu kosong atau ≤ 0
   - Total Biaya kosong atau < 0  
   Outlier KPI ekstrem ditandai **Perlu_Verifikasi** jika berada di atas **kuantil 99.5%** (ROI/Profit Margin/Growth).

4) **Normalisasi Skor 0–100**
   ROI, Profit Margin, dan Growth dinormalisasi ke skala **0–100** memakai **quantile clipping** (misalnya kuantil 5%–95%) agar tidak “rusak” oleh outlier.

5) **Skor KPI Total (Berbobot)**
   **Skor KPI = 0.40×Skor_ROI + 0.35×Skor_PM + 0.25×Skor_GR**

6) **Kategori Skor**
   - **Baik**: Skor ≥ 75  
   - **Sedang**: 55 ≤ Skor < 75  
   - **Kurang**: Skor < 55  
   - **Tidak Valid**: jika data gagal validasi

7) **Output Aplikasi**
   - **Dashboard** ringkasan & distribusi kategori
   - **Grafik & Analisis** (ranking, per bidang, boxplot, pertumbuhan)
   - **Tabel KPI** + pencarian + highlight kategori
   - **Rekomendasi otomatis** per UKM & rekomendasi kebijakan kecamatan
   - Export **Excel & PDF report**
