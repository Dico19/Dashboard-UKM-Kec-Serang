# pages/Tabel_KPI.py
import streamlit as st
import pandas as pd

from app.ui import inject_global_css, render_header
from app.core import export_excel

st.set_page_config(page_title="Tabel KPI", page_icon="📋", layout="wide")

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# GUARD: data harus dari halaman Upload
# =========================
if "df_filtered" not in st.session_state:
    st.markdown("""
    <div class="glass" style="padding:16px;">
      <div style="font-weight:900; font-size:16px;">⚠️ Data belum tersedia</div>
      <div style="color:rgba(226,232,240,.85); margin-top:6px;">
        Silakan buka menu <b>Upload</b>, upload Excel, lalu atur filter.
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ Ke halaman Upload", use_container_width=True):
        try:
            st.switch_page("pages/00_Upload.py")
        except Exception:
            pass
    st.stop()

df = st.session_state["df_filtered"].copy()

st.title("📋 Tabel Evaluasi KPI (Filtered)")

# =========================
# SEARCH
# =========================
q = st.text_input("🔎 Cari Nama Usaha (opsional):", "")
if q.strip():
    if "Nama Usaha" in df.columns:
        df = df[df["Nama Usaha"].astype(str).str.contains(q, case=False, na=False)].copy()
    else:
        st.warning("Kolom **Nama Usaha** tidak ditemukan, fitur pencarian tidak bisa dipakai.")

# =========================
# COLUMNS TO SHOW (safe)
# =========================
cols_show = [
    "Bidang Usaha", "Nama Usaha",
    "Pendapatan Tahun Lalu (Rp)", "Pendapatan Tahun Ini (Rp)",
    "Total Biaya (Rp)", "Total Modal/Investasi (Rp)",
    "Laba Bersih (Rp)", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)",
    "Cost Ratio",
    "Skor_KPI", "Kategori_Skor", "Valid_Data", "Perlu_Verifikasi"
]
cols_exist = [c for c in cols_show if c in df.columns]

if not cols_exist:
    st.warning("Kolom-kolom tabel tidak ditemukan di data.")
    st.dataframe(df.head(50), use_container_width=True)
    st.stop()

df_show = df[cols_exist].copy()
df_show.insert(0, "No", range(1, len(df_show) + 1))

# =========================
# STYLE KATEGORI
# =========================
def hl(val):
    if val == "Baik":
        return "background-color:#14532d;color:white"
    if val == "Sedang":
        return "background-color:#78350f;color:white"
    if val == "Kurang":
        return "background-color:#7f1d1d;color:white"
    return ""

if "Kategori_Skor" in df_show.columns:
    styled = df_show.style.applymap(hl, subset=["Kategori_Skor"])
else:
    styled = df_show

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True,
    height=520
)

# =========================
# REKOMENDASI
# =========================
if all(c in df.columns for c in ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor", "Rekomendasi"]):
    st.markdown("### 🧠 Rekomendasi Otomatis")
    with st.expander("Lihat rekomendasi per UKM (Top 50 sesuai tabel)"):
        small = df[["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor", "Rekomendasi"]].head(50).copy()
        st.dataframe(small, use_container_width=True, hide_index=True, height=520)
else:
    st.caption("Rekomendasi tidak ditampilkan karena beberapa kolom belum tersedia.")

# =========================
# EXPORT
# =========================
excel_bytes, fname = export_excel(df_show, filename="Tabel_Evaluasi_KPI_UMKM.xlsx")
st.download_button(
    "⬇️ Unduh Tabel (Excel)",
    excel_bytes,
    file_name=fname,
    use_container_width=True
)
