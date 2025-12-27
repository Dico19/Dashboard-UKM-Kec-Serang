import streamlit as st
import pandas as pd
from app.ui import inject_global_css, render_header
from app.core import export_excel

st.set_page_config(page_title="Tabel KPI", page_icon="📋", layout="wide")
inject_global_css()

if "df_filtered" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_filtered"].copy()
st.title("📋 Tabel Evaluasi KPI (Filtered)")

q = st.text_input("🔎 Cari Nama Usaha (opsional):", "")
if q.strip():
    df = df[df["Nama Usaha"].astype(str).str.contains(q, case=False, na=False)].copy()

cols_show = [
    "Bidang Usaha","Nama Usaha",
    "Pendapatan Tahun Lalu (Rp)","Pendapatan Tahun Ini (Rp)","Total Biaya (Rp)","Total Modal/Investasi (Rp)",
    "Laba Bersih (Rp)","ROI (%)","Profit Margin (%)","Growth Rate (%)","Cost Ratio",
    "Skor_KPI","Kategori_Skor","Valid_Data","Perlu_Verifikasi"
]

df_show = df[cols_show].copy()
df_show.insert(0, "No", range(1, len(df_show)+1))

def hl(val):
    if val == "Baik": return "background-color:#14532d;color:white"
    if val == "Sedang": return "background-color:#78350f;color:white"
    if val == "Kurang": return "background-color:#7f1d1d;color:white"
    return ""

st.dataframe(
    df_show.style.applymap(hl, subset=["Kategori_Skor"]),
    use_container_width=True,
    hide_index=True,
    height=520
)

st.markdown("### 🧠 Rekomendasi Otomatis")
with st.expander("Lihat rekomendasi per UKM (Top 50 sesuai tabel)"):
    small = df[["Nama Usaha","Bidang Usaha","Skor_KPI","Kategori_Skor","Rekomendasi"]].head(50).copy()
    st.dataframe(small, use_container_width=True, hide_index=True, height=520)

excel_bytes, fname = export_excel(df_show, filename="Tabel_Evaluasi_KPI_UMKM.xlsx")
st.download_button("⬇️ Unduh Tabel (Excel)", excel_bytes, file_name=fname)
