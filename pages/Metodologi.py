import streamlit as st
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Metodologi", page_icon="📝", layout="wide")
inject_global_css()

st.title("📝 Metodologi Evaluasi KPI")

st.markdown("""
### 1) KPI yang digunakan
**Laba Bersih (Rp)**  
= Pendapatan Tahun Ini − Total Biaya

**ROI (%)**  
= (Laba Bersih / Total Modal/Investasi) × 100

**Profit Margin (%)**  
= (Laba Bersih / Pendapatan Tahun Ini) × 100

**Growth Rate (%)**  
= ((Pendapatan Tahun Ini − Pendapatan Tahun Lalu) / Pendapatan Tahun Lalu) × 100

**Cost Ratio (tambahan)**  
= Total Biaya / Pendapatan Tahun Ini  
(Makin kecil → makin efisien)

---

### 2) Skor KPI 0–100 (Normalisasi)
Setiap KPI utama (ROI, Profit Margin, Growth) dinormalisasi ke skala **0–100** memakai **quantile clipping** (agar tidak rusak oleh outlier).

---

### 3) Skor Total (berbobot)
**Skor KPI = 0.40×Skor_ROI + 0.35×Skor_PM + 0.25×Skor_GR**

Alasan bobot:
- ROI (40%): efektivitas modal/investasi, penting untuk keberlanjutan.
- Profit Margin (35%): kemampuan menghasilkan laba dari penjualan.
- Growth (25%): pertumbuhan bisnis, penting tapi lebih fluktuatif.

---

### 4) Kategori (berdasarkan Skor KPI)
- **Baik**: Skor ≥ 75  
- **Sedang**: 55 ≤ Skor < 75  
- **Kurang**: Skor < 55  
- **Tidak Valid**: data tidak lengkap/0 pada kolom penting (modal, pendapatan)

---

### 5) Data Quality
- Cek nilai 0/negatif pada modal & pendapatan
- Outlier KPI ekstrem ditandai **Perlu Verifikasi** (di atas kuantil 99.5%)
""")
