# pages/Rata_rata_Bidang.py
import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Rata-rata Bidang", page_icon="🏭", layout="wide")

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

st.title("🏭 Rata-rata KPI per Bidang Usaha")

if "Bidang Usaha" not in df.columns:
    st.warning("Kolom **Bidang Usaha** tidak ditemukan.")
    st.stop()

kpi_cols_all = ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)", "Cost Ratio"]
kpi_cols = [c for c in kpi_cols_all if c in df.columns]

if not kpi_cols:
    st.warning("Kolom KPI tidak ditemukan.")
    st.dataframe(df.head(50), use_container_width=True)
    st.stop()

summary = (
    df.groupby("Bidang Usaha")[kpi_cols]
    .mean(numeric_only=True)
    .round(2)
    .reset_index()
)

if "Skor_KPI" in summary.columns:
    summary = summary.sort_values("Skor_KPI", ascending=False)

st.dataframe(summary, use_container_width=True, hide_index=True, height=420)

metric_options = [c for c in ["Skor_KPI", "Growth Rate (%)", "ROI (%)", "Profit Margin (%)", "Cost Ratio"] if c in summary.columns]
metric = st.selectbox("Tampilkan grafik:", metric_options, index=0)

hover_cols = [c for c in kpi_cols_all if c in summary.columns]

fig = px.bar(
    summary,
    x=metric,
    y="Bidang Usaha",
    orientation="h",
    hover_data=hover_cols
)
fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

st.caption("Catatan: Cost Ratio lebih kecil = lebih efisien (biaya dibanding pendapatan).")
