# pages/Data_Quality.py
import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui import inject_global_css, render_header
from app.core import data_quality_summary

st.set_page_config(page_title="Data Quality", page_icon="🧪", layout="wide")

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# GUARD: data harus dari halaman Upload
# =========================
if "df_all" not in st.session_state:
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

df = st.session_state["df_all"].copy()

st.title("🧪 Data Quality & Cleaning")

s = data_quality_summary(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Baris", s["total_rows"])
c2.metric("Valid", s["valid_rows"])
c3.metric("Tidak Valid", s["invalid_rows"])
c4.metric("Perlu Verifikasi (Outlier)", s["need_verify"])

st.markdown("### 🔎 Missing Value per Kolom Wajib")
miss = pd.DataFrame([s["missing_by_col"]]).T.reset_index()
miss.columns = ["Kolom", "Jumlah Missing"]
fig = px.bar(miss, x="Jumlah Missing", y="Kolom", orientation="h")
fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### ⚠️ Baris Bermasalah")

# aman kalau kolom belum ada
valid_col = "Valid_Data" if "Valid_Data" in df.columns else None
verify_col = "Perlu_Verifikasi" if "Perlu_Verifikasi" in df.columns else None

if valid_col and verify_col:
    bad = df[(df[valid_col] == False) | (df[verify_col] == True)].copy()
elif valid_col:
    bad = df[df[valid_col] == False].copy()
elif verify_col:
    bad = df[df[verify_col] == True].copy()
else:
    bad = df.copy()

cols_wanted = [
    "Bidang Usaha","Nama Usaha","Pendapatan Tahun Ini (Rp)","Pendapatan Tahun Lalu (Rp)",
    "Total Biaya (Rp)","Total Modal/Investasi (Rp)",
    "ROI (%)","Profit Margin (%)","Growth Rate (%)",
    "Skor_KPI","Kategori_Skor","Valid_Data","Perlu_Verifikasi"
]
cols_show = [c for c in cols_wanted if c in bad.columns]

st.dataframe(
    bad[cols_show],
    use_container_width=True,
    hide_index=True,
    height=520
)

st.caption("Outlier ditandai jika KPI sangat ekstrem (di atas kuantil 99.5%) → sebaiknya diverifikasi.")
