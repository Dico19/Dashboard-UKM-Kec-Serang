# app/upload.py
import io
import hashlib
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def _read_excel_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(file_bytes))

def render_upload_box():
    """
    Kotak upload untuk ditaruh di MAIN CONTENT (bukan sidebar).
    Simpan hasil ke st.session_state["df_upload"].
    """
    st.markdown("### 📤 Upload Excel")
    uploaded = st.file_uploader(
        "Pilih file Excel (.xlsx)",
        type=["xlsx"],
        key="excel_uploader_main",
        label_visibility="collapsed",
    )

    # status upload aktif
    if st.session_state.get("df_upload") is not None:
        name = st.session_state.get("upload_name", "(tanpa nama)")
        df = st.session_state["df_upload"]
        st.success(f"Data upload aktif: **{name}**")
        st.caption(f"Baris: {len(df):,} | Kolom: {df.shape[1]}")

        if st.button("🧹 Hapus data upload", use_container_width=True):
            for k in ["df_upload", "upload_name", "upload_hash", "df_all", "df_filtered"]:
                st.session_state.pop(k, None)
            st.rerun()

    # upload baru
    if uploaded is not None:
        file_bytes = uploaded.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        if st.session_state.get("upload_hash") != file_hash:
            st.session_state["df_upload"] = _read_excel_bytes(file_bytes)
            st.session_state["upload_name"] = uploaded.name
            st.session_state["upload_hash"] = file_hash
            st.success("✅ Upload berhasil. Data tersimpan.")
            st.rerun()
