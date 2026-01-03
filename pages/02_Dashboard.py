# pages/01_Dashboard.py
import streamlit as st
import plotly.express as px

from app.ui import inject_global_css, render_header
from app.core import export_excel

st.set_page_config(
    page_title="Dashboard KPI UMKM Serang",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# GET DATA FROM SESSION (dari page Upload)
# =========================
filtered_df = st.session_state.get("df_filtered")
df_all = st.session_state.get("df_all")

if filtered_df is None or df_all is None:
    st.markdown("""
    <div class="glass" style="padding:16px;">
      <div style="font-weight:900; font-size:16px;">⚠️ Data belum siap</div>
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

# =========================
# QUICK INSIGHT
# =========================
dominan = filtered_df["Kategori_Skor"].value_counts().idxmax()

top_sektor = (
    filtered_df.groupby("Bidang Usaha")["Growth Rate (%)"]
    .mean(numeric_only=True)
    .sort_values(ascending=False)
)
top_sektor_name = top_sektor.index[0] if len(top_sektor) else "-"

st.markdown(f"""
<div class="glass insight">
  <div style="font-size:14px; color: rgba(255,255,255,.92);">
    💡 <b>Mayoritas UKM berada pada kategori <u>{dominan}</u></b>,
    dan sektor <b><u>{top_sektor_name}</u></b> memiliki rata-rata <b>Growth Rate</b> tertinggi.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# KPI CARDS
# =========================
avg_roi = float(filtered_df["ROI (%)"].mean(skipna=True))
avg_pm  = float(filtered_df["Profit Margin (%)"].mean(skipna=True)) if "Profit Margin (%)" in filtered_df.columns else 0.0
avg_gr  = float(filtered_df["Growth Rate (%)"].mean(skipna=True))
avg_sc  = float(filtered_df["Skor_KPI"].mean(skipna=True))

baik = int((filtered_df["Kategori_Skor"] == "Baik").sum())
sedang = int((filtered_df["Kategori_Skor"] == "Sedang").sum())
kurang = int((filtered_df["Kategori_Skor"] == "Kurang").sum())

st.markdown(f"""
<div class="kpi-grid">
  <div class="glass kpi-card">
    <div class="kpi-icon">👥</div>
    <div class="kpi-label">Total UKM</div>
    <div class="kpi-value">{len(filtered_df)}</div>
    <div class="kpi-hint">Jumlah sesuai filter</div>
  </div>

  <div class="glass kpi-card">
    <div class="kpi-icon">⭐</div>
    <div class="kpi-label">Skor KPI rata-rata</div>
    <div class="kpi-value">{avg_sc:.2f}</div>
    <div class="kpi-hint">Gabungan ROI/PM/Growth (0–100)</div>
  </div>

  <div class="glass kpi-card">
    <div class="kpi-icon">📈</div>
    <div class="kpi-label">Rata-rata ROI</div>
    <div class="kpi-value">{avg_roi:.2f}%</div>
    <div class="kpi-hint">Return on Investment</div>
  </div>

  <div class="glass kpi-card">
    <div class="kpi-icon">🚀</div>
    <div class="kpi-label">Rata-rata Growth</div>
    <div class="kpi-value">{avg_gr:.2f}%</div>
    <div class="kpi-hint">Pertumbuhan pendapatan</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# MINI SUMMARY + PIE
# =========================
colA, colB = st.columns([1.15, 1.0], gap="large")

with colA:
    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">📌 Mini Summary</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Baik ✅", baik)
    m2.metric("Sedang ⚠️", sedang)
    m3.metric("Kurang ❌", kurang)
    st.caption("Kategori berbasis Skor KPI (0–100).")
    st.markdown('</div>', unsafe_allow_html=True)

with colB:
    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">🍩 Distribusi Kategori</div>', unsafe_allow_html=True)
    cc = filtered_df["Kategori_Skor"].value_counts().reset_index()
    cc.columns = ["Kategori", "Jumlah"]
    fig = px.pie(cc, names="Kategori", values="Jumlah", hole=0.55)
    fig.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text=""
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TOP 10 (optional, tapi bagus buat dashboard)
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if "Valid_Data" in filtered_df.columns:
    valid_only = filtered_df[filtered_df["Valid_Data"] == True].copy()
else:
    valid_only = filtered_df.copy()

if "Skor_KPI" in valid_only.columns and len(valid_only) > 0:
    best10 = valid_only.sort_values("Skor_KPI", ascending=False).head(10)
    risk10 = valid_only.sort_values("Skor_KPI", ascending=True).head(10)

    cL, cR = st.columns(2, gap="large")
    with cL:
        st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="small-title">🏆 Top 10 Terbaik</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor"] if c in best10.columns]
        st.dataframe(best10[cols_show], use_container_width=True, hide_index=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)

    with cR:
        st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="small-title">🧯 Top 10 Butuh Perhatian</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor"] if c in risk10.columns]
        st.dataframe(risk10[cols_show], use_container_width=True, hide_index=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# EXPORT
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
excel_bytes, fname = export_excel(filtered_df, filename="Evaluasi_KPI_UMKM_Serang.xlsx")
st.download_button(
    "⬇️ Unduh Data (Excel) - sesuai filter",
    excel_bytes,
    file_name=fname,
    use_container_width=True
)
