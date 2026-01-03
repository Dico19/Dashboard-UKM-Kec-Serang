# Home.py
import streamlit as st
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="UKM Dashboard", page_icon="📊", layout="wide")

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# HERO / INTRO
# =========================
st.markdown("""
<div class="glass" style="padding:20px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:20px;">🏠 UKM Dashboard — Kecamatan Serang</div>
  <div style="color:rgba(226,232,240,.88); margin-top:6px; font-size:13.5px; line-height:1.55;">
    Dashboard evaluasi kinerja UKM berbasis <b>ROI</b>, <b>Profit Margin</b>, dan <b>Growth Rate</b> (skor 0–100),
    dilengkapi analisis visual, quality check, tabel detail, hingga export laporan.
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# AMBIL DATA DARI SESSION
# =========================
df_all = st.session_state.get("df_all")
df_filtered = st.session_state.get("df_filtered")
df_upload = st.session_state.get("df_upload")
df_manual = st.session_state.get("df_manual")

has_upload = df_upload is not None
has_manual = hasattr(df_manual, "empty") and (not df_manual.empty) if df_manual is not None else False

has_all = df_all is not None
has_filtered = df_filtered is not None
is_ready = has_all and has_filtered

total_all = int(len(df_all)) if has_all else 0
total_filtered = int(len(df_filtered)) if has_filtered else 0

# =========================
# STATUS DATA
# =========================
st.markdown('<div class="glass" style="padding:16px; margin-bottom:14px;">', unsafe_allow_html=True)
st.markdown('<div style="font-weight:900; font-size:15px; margin-bottom:10px;">📌 Status Data</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Upload Excel", "✅ Aktif" if has_upload else "— Belum")
c2.metric("Manual Input", "✅ Ada" if has_manual else "— Belum")
c3.metric("Data Siap", "✅ Siap" if is_ready else "⏳ Belum")
c4.metric("Jumlah (Filtered)", total_filtered)

st.caption(f"Total data (semua): **{total_all}** | Total data (sesuai filter): **{total_filtered}**")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# CARA PAKAI
# =========================
st.markdown("""
<div class="glass" style="padding:16px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:15px; margin-bottom:8px;">✨ Cara Pakai (3 Langkah)</div>
  <ol style="margin:0; padding-left:18px; color:rgba(226,232,240,.9); font-size:13px; line-height:1.7;">
    <li><b>Upload</b> file Excel (.xlsx) atau isi data di <b>Manual Input</b></li>
    <li>Atur <b>Sumber Data</b> + <b>Filter Global</b> di halaman Upload</li>
    <li>Buka halaman <b>Dashboard / Data Quality / Grafik / Tabel / Report</b></li>
  </ol>
</div>
""", unsafe_allow_html=True)

# =========================
# QUICK ACTIONS (PATH SUDAH DISAMAKAN)
# =========================
st.markdown('<div class="glass" style="padding:16px;">', unsafe_allow_html=True)
st.markdown('<div style="font-weight:900; font-size:15px; margin-bottom:10px;">🚀 Quick Actions</div>', unsafe_allow_html=True)

b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("📤 Upload Data", use_container_width=True, key="qa_upload"):
        try:
            st.switch_page("pages/00_Upload.py")
        except Exception:
            pass

with b2:
    if st.button("📊 Dashboard", use_container_width=True, disabled=not is_ready, key="qa_dash"):
        try:
            st.switch_page("pages/02_Dashboard.py")
        except Exception:
            pass

with b3:
    if st.button("🧪 Data Quality", use_container_width=True, disabled=not has_all, key="qa_dq"):
        try:
            st.switch_page("pages/03_Data_Quality.py")
        except Exception:
            pass

with b4:
    if st.button("📄 Generate Report", use_container_width=True, disabled=not is_ready, key="qa_report"):
        try:
            st.switch_page("pages/09_Generate_Report.py")
        except Exception:
            pass

st.markdown("""
<div style="margin-top:10px; color:rgba(226,232,240,.7); font-size:12px;">
  Tips: Kalau tombol Dashboard/Report masih nonaktif, berarti data belum disiapkan.
  Masuk dulu ke <b>Upload</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
