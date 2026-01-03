import streamlit as st
import pandas as pd
from app.ui import inject_global_css, render_header
from app.core import REQUIRED_COLS, export_excel

st.set_page_config(page_title="Manual Input", page_icon="🧾", layout="wide")
inject_global_css()

inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

st.title("🧾 Manual Input UKM (Dashboard Manual)")

if "df_manual" not in st.session_state:
    st.session_state.df_manual = pd.DataFrame(columns=REQUIRED_COLS)

with st.form("manual_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        bidang = st.text_input("Bidang Usaha", value="")
        nama = st.text_input("Nama Usaha", value="")
        p_ini = st.number_input("Pendapatan Tahun Ini (Rp)", min_value=0.0, value=0.0, step=100000.0)
    with c2:
        p_lalu = st.number_input("Pendapatan Tahun Lalu (Rp)", min_value=0.0, value=0.0, step=100000.0)
        biaya = st.number_input("Total Biaya (Rp)", min_value=0.0, value=0.0, step=100000.0)
        modal = st.number_input("Total Modal/Investasi (Rp)", min_value=0.0, value=0.0, step=100000.0)

    submitted = st.form_submit_button("➕ Tambah UKM", use_container_width=True)

if submitted:
    row = {
        "Bidang Usaha": bidang.strip(),
        "Nama Usaha": nama.strip(),
        "Pendapatan Tahun Ini (Rp)": p_ini,
        "Pendapatan Tahun Lalu (Rp)": p_lalu,
        "Total Biaya (Rp)": biaya,
        "Total Modal/Investasi (Rp)": modal,
    }
    st.session_state.df_manual = pd.concat([st.session_state.df_manual, pd.DataFrame([row])], ignore_index=True)
    st.success("✅ UKM berhasil ditambahkan ke data manual.")

st.markdown("### 📌 Data Manual Saat Ini")
dfm = st.session_state.df_manual.copy()
st.dataframe(dfm, use_container_width=True, hide_index=True, height=420)

c1, c2 = st.columns(2)
with c1:
    if st.button("🗑️ Hapus Semua Data Manual", use_container_width=True):
        st.session_state.df_manual = pd.DataFrame(columns=REQUIRED_COLS)
        st.success("Data manual direset.")
with c2:
    excel_bytes, fname = export_excel(dfm, filename="Data_Manual_UKM.xlsx")
    st.download_button("⬇️ Export Data Manual (Excel)", excel_bytes, file_name=fname, use_container_width=True)

st.info("Data manual akan ikut digabung di Home jika kamu pilih mode 'Gabung Upload + Manual'.")
