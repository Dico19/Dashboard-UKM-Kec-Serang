import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui import inject_global_css, render_header
from app.core import (
    REQUIRED_COLS,
    compute_kpis,
    score_and_classify,
    add_recommendations,
    export_excel,
)

st.set_page_config(page_title="Dashboard KPI UMKM Serang", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# SESSION DEFAULTS
# =========================
if "selected_bidang" not in st.session_state:
    st.session_state.selected_bidang = []
if "top_n" not in st.session_state:
    st.session_state.top_n = 50
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Growth Rate (%)"
if "df_manual" not in st.session_state:
    st.session_state.df_manual = pd.DataFrame(columns=REQUIRED_COLS)

# =========================
# LOAD DATA (Upload + Manual)
# =========================
st.markdown('<div class="glass" style="padding:16px;">', unsafe_allow_html=True)
st.markdown(
    '<div style="font-weight:900; font-size:14px; margin-bottom:8px;">📂 Upload File Excel</div>'
    '<div style="color:rgba(148,163,184,.95); font-size:12px; margin-bottom:10px;">'
    'Format: .xlsx • Kamu juga bisa input manual di halaman "Manual Input".'
    '</div>',
    unsafe_allow_html=True
)

uploaded = st.file_uploader(label="", type=["xlsx"], label_visibility="collapsed")

use_manual = not st.session_state.df_manual.empty
has_upload = uploaded is not None

if not has_upload and not use_manual:
    st.markdown("""
    <div style="margin-top:12px; padding:14px; border-radius:14px;
                background: rgba(255,255,255,.04);
                border: 1px solid rgba(255,255,255,.10);">
      <div style="font-weight:900; margin-bottom:6px;">✨ Cara pakai</div>
      <ol style="margin:0; padding-left:18px; color:rgba(226,232,240,.9); font-size:13px; line-height:1.6;">
        <li>Upload file Excel (.xlsx) atau input manual</li>
        <li>Atur filter di sidebar</li>
        <li>Pindah halaman: Grafik KPI / Pertumbuhan / Rata-rata / Tabel / Report</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown('</div>', unsafe_allow_html=True)

# dataset source switch
st.sidebar.header("🗃️ Sumber Data")
options = []
if has_upload: options.append("Hanya Upload")
if use_manual: options.append("Hanya Manual")
if has_upload and use_manual: options.insert(0, "Gabung Upload + Manual")

data_mode = st.sidebar.radio("Pilih data:", options, index=0)

df_upload = None
if has_upload:
    df_upload = pd.read_excel(uploaded)

df_manual = st.session_state.df_manual.copy()

if data_mode == "Hanya Upload":
    df_raw = df_upload
elif data_mode == "Hanya Manual":
    df_raw = df_manual
else:
    df_raw = pd.concat([df_upload, df_manual], ignore_index=True)

# =========================
# VALIDATE REQUIRED COLS
# =========================
missing = [c for c in REQUIRED_COLS if c not in df_raw.columns]
if missing:
    st.error(f"Kolom wajib tidak ada: {missing}")
    st.stop()

# =========================
# KPI + SCORE + RECOMMEND
# =========================
df = compute_kpis(df_raw)
df = score_and_classify(df, w_roi=0.40, w_pm=0.35, w_gr=0.25)
df = add_recommendations(df)

# =========================
# SIDEBAR GLOBAL FILTERS
# =========================
st.sidebar.header("🎛 Filter Global")

bidang_list = sorted(df["Bidang Usaha"].dropna().astype(str).unique().tolist())
if not st.session_state.selected_bidang:
    st.session_state.selected_bidang = bidang_list[:]

c1, c2 = st.sidebar.columns(2)
with c1:
    if st.button("✅ Pilih Semua", use_container_width=True):
        st.session_state.selected_bidang = bidang_list[:]
with c2:
    if st.button("🧹 Kosongkan", use_container_width=True):
        st.session_state.selected_bidang = []

selected = st.sidebar.multiselect("Bidang usaha:", options=bidang_list, default=st.session_state.selected_bidang)
st.session_state.selected_bidang = selected

st.sidebar.divider()
st.session_state.top_n = st.sidebar.slider("📌 Top N (grafik/ranking)", 10, 200, int(st.session_state.top_n), 5)
st.session_state.sort_by = st.sidebar.selectbox("Urutkan (Top N) berdasarkan:", ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)"], index=0)

filtered_df = df[df["Bidang Usaha"].astype(str).isin(selected)].copy()
st.sidebar.metric("📍 Jumlah UKM ditampilkan", int(len(filtered_df)))

# save for pages
st.session_state["df_all"] = df
st.session_state["df_filtered"] = filtered_df

if len(filtered_df) == 0:
    st.warning("Filter menghasilkan 0 data.")
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
# KPI CARDS (2 COL)
# =========================
avg_roi = float(filtered_df["ROI (%)"].mean(skipna=True))
avg_pm  = float(filtered_df["Profit Margin (%)"].mean(skipna=True))
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
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=10,b=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TOP 10 BEST + TOP 10 RISK + REKOMENDASI
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

valid_only = filtered_df[filtered_df["Valid_Data"] == True].copy()
best10 = valid_only.sort_values("Skor_KPI", ascending=False).head(10)
risk10 = valid_only.sort_values("Skor_KPI", ascending=True).head(10)

cL, cR = st.columns(2, gap="large")

with cL:
    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">🏆 Top 10 Terbaik</div>', unsafe_allow_html=True)
    st.dataframe(best10[["Nama Usaha","Bidang Usaha","Skor_KPI","Kategori_Skor"]], use_container_width=True, hide_index=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

with cR:
    st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">🧯 Top 10 Butuh Perhatian</div>', unsafe_allow_html=True)
    st.dataframe(risk10[["Nama Usaha","Bidang Usaha","Skor_KPI","Kategori_Skor"]], use_container_width=True, hide_index=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass" style="padding:14px; margin-top:14px;">', unsafe_allow_html=True)
st.markdown('<div class="small-title">🧠 Rekomendasi Otomatis (pilih 1 UKM)</div>', unsafe_allow_html=True)

name_list = valid_only["Nama Usaha"].astype(str).dropna().unique().tolist()
pick = st.selectbox("Pilih UKM:", name_list)
row = valid_only[valid_only["Nama Usaha"].astype(str) == str(pick)].head(1)

if not row.empty:
    r = row.iloc[0]
    st.write(f"**Bidang:** {r['Bidang Usaha']}  |  **Skor KPI:** {r['Skor_KPI']:.2f}  |  **Kategori:** {r['Kategori_Skor']}")
    st.code(r["Rekomendasi"], language="text")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# EXPORT EXCEL (FILTERED)
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
excel_bytes, fname = export_excel(filtered_df, filename="Evaluasi_KPI_UMKM_Serang.xlsx")
st.download_button("⬇️ Unduh Data (Excel) - sesuai filter", excel_bytes, file_name=fname)

st.info("✅ Data tersimpan. Pindah halaman lewat sidebar untuk Grafik/Quality/Manual Input/Report.")
