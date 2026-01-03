# pages/00_Upload.py
import streamlit as st
import pandas as pd

from app.ui import inject_global_css, render_header
from app.upload import render_upload_box
from app.core import (
    REQUIRED_COLS,
    compute_kpis,
    score_and_classify,
    add_recommendations,
)

st.set_page_config(
    page_title="Upload Data - KPI UMKM Serang",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================================================
# BERSIHIN SESSION YANG KAMU MAU HAPUS TOTAL
# =========================================================
for k in ["top_n", "sort_by"]:
    st.session_state.pop(k, None)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="glass" style="padding:18px; margin-bottom:14px;">
      <div style="font-weight:900; font-size:18px;">📤 Upload & Siapkan Data Evaluasi</div>
      <div style="color:rgba(226,232,240,.85); margin-top:6px;">
        Upload Excel di bawah ini (atau isi di <b>Manual Input</b>), lalu atur <b>Sumber Data</b> dan <b>Filter Global</b>.
        Setelah itu, buka page <b>Dashboard</b> / <b>Data Quality</b> / dll.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 1) UPLOAD BOX (MAIN CONTENT)
# =========================================================
st.markdown('<div class="glass" style="padding:14px; margin-bottom:14px;">', unsafe_allow_html=True)
render_upload_box()  # wajib: function ini harus set st.session_state["df_upload"]
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SESSION DEFAULTS YANG DIPAKAI APP
# =========================================================
if "df_manual" not in st.session_state:
    st.session_state.df_manual = pd.DataFrame(columns=REQUIRED_COLS)
if "selected_bidang" not in st.session_state:
    st.session_state.selected_bidang = []

df_upload = st.session_state.get("df_upload")              # dari upload_box
df_manual = st.session_state.df_manual.copy()              # dari halaman Manual Input

use_manual = not df_manual.empty
has_upload = df_upload is not None and not getattr(df_upload, "empty", True)

if not has_upload and not use_manual:
    st.warning("Upload Excel dulu (atau isi Manual Input).")
    st.stop()

# =========================================================
# 2) SUMBER DATA (MAIN CONTENT)
# =========================================================
st.markdown('<div class="glass" style="padding:14px; margin-bottom:14px;">', unsafe_allow_html=True)
st.markdown("### 🗃️ Sumber Data")

options = []
if has_upload:
    options.append("Hanya Upload")
if use_manual:
    options.append("Hanya Manual")
if has_upload and use_manual:
    options.insert(0, "Gabung Upload + Manual")

data_mode = st.radio("Pilih data:", options, index=0, horizontal=True)

if data_mode == "Hanya Upload":
    df_raw = df_upload
elif data_mode == "Hanya Manual":
    df_raw = df_manual
else:
    parts = []
    if has_upload:
        parts.append(df_upload)
    if use_manual:
        parts.append(df_manual)
    df_raw = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

st.markdown("</div>", unsafe_allow_html=True)

if df_raw is None or df_raw.empty:
    st.warning("Tidak ada data pada pilihan Sumber Data ini.")
    st.stop()

# =========================================================
# VALIDATE REQUIRED COLS
# =========================================================
missing = [c for c in REQUIRED_COLS if c not in df_raw.columns]
if missing:
    st.error(f"Kolom wajib tidak ada: {missing}")
    st.stop()

# =========================================================
# KPI + SCORE + RECOMMEND
# =========================================================
df = compute_kpis(df_raw)
df = score_and_classify(df, w_roi=0.40, w_pm=0.35, w_gr=0.25)
df = add_recommendations(df)

# =========================================================
# 3) FILTER GLOBAL (MAIN CONTENT) - FIX ERROR DEFAULT NOT IN OPTIONS
# =========================================================
st.markdown('<div class="glass" style="padding:14px; margin-bottom:14px;">', unsafe_allow_html=True)
st.markdown("### 🎛 Filter Global")

bidang_list = sorted(df["Bidang Usaha"].dropna().astype(str).unique().tolist())
if not bidang_list:
    st.warning("Kolom Bidang Usaha kosong. Cek data kamu.")
    st.stop()

# ✅ INI KUNCI PERBAIKAN ERROR:
# default multiselect HARUS subset dari bidang_list
prev_selected = st.session_state.get("selected_bidang", [])
prev_selected = [str(x) for x in prev_selected] if isinstance(prev_selected, (list, tuple)) else []
default_selected = [x for x in prev_selected if x in bidang_list]
if not default_selected:
    default_selected = bidang_list[:]  # default: pilih semua

btn1, btn2, _ = st.columns([1, 1, 3])
with btn1:
    if st.button("✅ Pilih Semua", use_container_width=True):
        default_selected = bidang_list[:]
with btn2:
    if st.button("🧹 Kosongkan", use_container_width=True):
        default_selected = []

selected = st.multiselect(
    "Bidang usaha:",
    options=bidang_list,
    default=default_selected,
)

# simpan lagi (yang sudah valid)
st.session_state.selected_bidang = selected

filtered_df = df[df["Bidang Usaha"].astype(str).isin(selected)].copy()
st.metric("📍 Jumlah UKM ditampilkan", int(len(filtered_df)))

st.markdown("</div>", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("Filter menghasilkan 0 data.")
    st.stop()

# =========================================================
# SIMPAN UNTUK HALAMAN LAIN
# =========================================================
st.session_state["df_all"] = df
st.session_state["df_filtered"] = filtered_df

# =========================================================
# PREVIEW
# =========================================================
st.markdown('<div class="glass" style="padding:14px;">', unsafe_allow_html=True)
st.markdown("<b>✅ Data siap.</b> Kamu bisa buka page <b>Dashboard</b> sekarang.", unsafe_allow_html=True)
st.caption("Preview 20 baris pertama (sesuai filter):")
st.dataframe(filtered_df.head(20), use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)
