import streamlit as st
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Metodologi", page_icon="📝", layout="wide")

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# HERO
# =========================
st.markdown("""
<div class="glass" style="padding:18px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:20px;">📝 Metodologi Evaluasi KPI</div>
  <div style="color:rgba(226,232,240,.88); margin-top:6px; font-size:13.5px; line-height:1.6;">
    Halaman ini menjelaskan rumus, proses normalisasi skor, pembobotan, kategori penilaian,
    dan aturan kualitas data yang digunakan pada UKM Dashboard Kecamatan Serang.
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 1) KPI yang digunakan (RAPI: pakai LaTeX)
# =========================
st.markdown("""
<div class="glass" style="padding:16px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:16px; margin-bottom:8px;">1) KPI yang Digunakan</div>
  <div style="color:rgba(226,232,240,.86); font-size:13.5px; line-height:1.7;">
    KPI dihitung dari pendapatan, biaya, dan modal untuk menghasilkan gambaran kinerja keuangan UKM.
  </div>
</div>
""", unsafe_allow_html=True)

k1, k2 = st.columns(2, gap="large")

with k1:
    st.markdown('<div class="glass" style="padding:14px; margin-bottom:12px;">', unsafe_allow_html=True)
    st.markdown("**• Laba Bersih (Rp)**")
    st.latex(r"\text{Laba Bersih}=\text{Pendapatan Tahun Ini}-\text{Total Biaya}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass" style="padding:14px; margin-bottom:12px;">', unsafe_allow_html=True)
    st.markdown("**• ROI (%)**")
    st.latex(r"\text{ROI}(\%)=\left(\frac{\text{Laba Bersih}}{\text{Total Modal/Investasi}}\right)\times 100")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown("**• Profit Margin (%)**")
    st.latex(r"\text{Profit Margin}(\%)=\left(\frac{\text{Laba Bersih}}{\text{Pendapatan Tahun Ini}}\right)\times 100")
    st.markdown("</div>", unsafe_allow_html=True)

with k2:
    st.markdown('<div class="glass" style="padding:14px; margin-bottom:12px;">', unsafe_allow_html=True)
    st.markdown("**• Growth Rate (%)**")
    st.latex(r"\text{Growth Rate}(\%)=\left(\frac{\text{Pendapatan Tahun Ini}-\text{Pendapatan Tahun Lalu}}{\text{Pendapatan Tahun Lalu}}\right)\times 100")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown("**• Cost Ratio (tambahan)**")
    st.latex(r"\text{Cost Ratio}=\frac{\text{Total Biaya}}{\text{Pendapatan Tahun Ini}}")
    st.caption("Semakin kecil → semakin efisien (biaya dibanding pendapatan).")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 2) Normalisasi
# =========================
st.markdown("""
<div class="glass" style="padding:16px; margin:14px 0;">
  <div style="font-weight:900; font-size:16px; margin-bottom:8px;">2) Skor 0–100 (Normalisasi)</div>
  <div style="color:rgba(226,232,240,.9); font-size:13.5px; line-height:1.75;">
    Setiap KPI utama (<b>ROI</b>, <b>Profit Margin</b>, <b>Growth</b>) dinormalisasi ke skala <b>0–100</b>.
    Agar skor tidak “rusak” karena nilai ekstrem, digunakan metode <b>quantile clipping</b>:
    <ul style="margin-top:8px; padding-left:18px;">
      <li>Nilai terlalu rendah/tinggi dipotong pada batas kuantil (mis. 5% dan 95%).</li>
      <li>Setelah itu, nilai dipetakan (min–max) ke rentang 0–100.</li>
    </ul>
    <span style="color:rgba(226,232,240,.8);">Hasilnya: perbandingan antar UKM lebih stabil dan lebih fair.</span>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 3) Skor total (JANGAN KAYA KODE: pakai LaTeX + kartu)
# =========================
st.markdown("""
<div class="glass" style="padding:16px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:16px; margin-bottom:8px;">3) Skor Total (Berbobot)</div>
  <div style="color:rgba(226,232,240,.9); font-size:13.5px; line-height:1.75;">
    Skor total adalah gabungan dari skor ROI, Profit Margin, dan Growth Rate dengan bobot tertentu.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass" style="padding:14px; margin-bottom:12px;">', unsafe_allow_html=True)
st.markdown("**Rumus Skor KPI (0–100):**")
st.latex(r"\text{Skor KPI}=0.40\cdot Skor_{ROI}+0.35\cdot Skor_{PM}+0.25\cdot Skor_{GR}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="glass" style="padding:14px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:14px; margin-bottom:6px;">Alasan Bobot</div>
  <ul style="margin:0; padding-left:18px; color:rgba(226,232,240,.9); font-size:13.5px; line-height:1.75;">
    <li><b>ROI (40%)</b>: efisiensi penggunaan modal/investasi, penting untuk keberlanjutan.</li>
    <li><b>Profit Margin (35%)</b>: kemampuan menghasilkan laba dari penjualan.</li>
    <li><b>Growth (25%)</b>: indikator perkembangan bisnis, namun cenderung lebih fluktuatif.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

# =========================
# 4) Kategori
# =========================
st.markdown("""
<div class="glass" style="padding:16px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:16px; margin-bottom:8px;">4) Kategori (berdasarkan Skor KPI)</div>
  <ul style="margin:0; padding-left:18px; color:rgba(226,232,240,.9); font-size:13.5px; line-height:1.75;">
    <li><b>Baik</b>: Skor ≥ 75</li>
    <li><b>Sedang</b>: 55 ≤ Skor &lt; 75</li>
    <li><b>Kurang</b>: Skor &lt; 55</li>
    <li><b>Tidak Valid</b>: data tidak lengkap/0 pada kolom penting (modal, pendapatan, dll)</li>
  </ul>
  <div style="margin-top:10px; color:rgba(226,232,240,.75); font-size:12.5px;">
    Catatan: Data <b>Tidak Valid</b> tidak dihitung dalam skor (Skor_KPI menjadi kosong/NaN).
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 5) Data Quality
# =========================
st.markdown("""
<div class="glass" style="padding:16px;">
  <div style="font-weight:900; font-size:16px; margin-bottom:8px;">5) Data Quality</div>
  <ul style="margin:0; padding-left:18px; color:rgba(226,232,240,.9); font-size:13.5px; line-height:1.75;">
    <li>Cek nilai 0/negatif pada modal & pendapatan</li>
    <li>Outlier KPI ekstrem ditandai <b>Perlu Verifikasi</b> (di atas kuantil 99.5%)</li>
  </ul>
</div>
""", unsafe_allow_html=True)
