# pages/Generate_Report.py
import streamlit as st
import pandas as pd

from app.ui import inject_global_css, render_header
from app.core import export_excel, generate_pdf_report

st.set_page_config(page_title="Generate Report", page_icon="📄", layout="wide")

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

st.title("📄 Generate Report (Excel + PDF)")

# =========================
# RINGKASAN OTOMATIS
# =========================
st.markdown("### ✅ Ringkasan Otomatis")

if "Valid_Data" in df.columns:
    valid = df[df["Valid_Data"] == True].copy()
else:
    valid = df.copy()

def safe_mean(frame: pd.DataFrame, col: str) -> float:
    return float(frame[col].mean(skipna=True)) if col in frame.columns and len(frame) else 0.0

baik = int((valid["Kategori_Skor"] == "Baik").sum()) if "Kategori_Skor" in valid.columns else 0
sedang = int((valid["Kategori_Skor"] == "Sedang").sum()) if "Kategori_Skor" in valid.columns else 0
kurang = int((valid["Kategori_Skor"] == "Kurang").sum()) if "Kategori_Skor" in valid.columns else 0

metrics = {
    "total": int(len(df)),
    "avg_roi": safe_mean(valid, "ROI (%)"),
    "avg_pm": safe_mean(valid, "Profit Margin (%)"),
    "avg_gr": safe_mean(valid, "Growth Rate (%)"),
    "avg_score": safe_mean(valid, "Skor_KPI"),
    "baik": baik,
    "sedang": sedang,
    "kurang": kurang,
}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", metrics["total"])
c2.metric("Skor rata-rata", f"{metrics['avg_score']:.2f}")
c3.metric("Baik", baik)
c4.metric("Kurang", kurang)

# =========================
# TOP 10
# =========================
if "Skor_KPI" in valid.columns and len(valid) > 0:
    top_best = valid.sort_values("Skor_KPI", ascending=False).head(10)
    top_risk = valid.sort_values("Skor_KPI", ascending=True).head(10)
else:
    top_best = valid.head(0)
    top_risk = valid.head(0)

st.markdown("### 🏆 Top 10 Terbaik")
cols_best = [c for c in ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor"] if c in top_best.columns]
st.dataframe(top_best[cols_best], use_container_width=True, hide_index=True)

st.markdown("### 🧯 Top 10 Butuh Perhatian")
cols_risk = [c for c in ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor", "Rekomendasi"] if c in top_risk.columns]
st.dataframe(top_risk[cols_risk], use_container_width=True, hide_index=True)

# =========================
# RINGKASAN PER SEKTOR
# =========================
sektor_summary = pd.DataFrame()
if "Bidang Usaha" in valid.columns:
    kpi_cols = [c for c in ["ROI (%)", "Profit Margin (%)", "Growth Rate (%)", "Skor_KPI"] if c in valid.columns]
    if kpi_cols:
        sektor_summary = (
            valid.groupby("Bidang Usaha")[kpi_cols]
            .mean(numeric_only=True)
            .round(2)
            .reset_index()
        )
        if "Growth Rate (%)" in sektor_summary.columns:
            sektor_summary = sektor_summary.sort_values("Growth Rate (%)", ascending=False)

# =========================
# DOWNLOAD
# =========================
st.markdown("---")
st.markdown("## ⬇️ Download")

# Excel
excel_bytes, fname = export_excel(df, filename="Report_Evaluasi_KPI_UMKM.xlsx")
st.download_button(
    "⬇️ Download Excel (Filtered)",
    excel_bytes,
    file_name=fname,
    use_container_width=True
)

# PDF
try:
    pdf_bytes = generate_pdf_report(metrics, top_best, top_risk, sektor_summary)
    st.download_button(
        "⬇️ Download PDF Report",
        pdf_bytes,
        file_name="Report_Evaluasi_KPI_UMKM.pdf",
        use_container_width=True
    )
except Exception as e:
    st.warning(
        f"PDF belum bisa dibuat: {e}\n\n"
        "Solusi: pastikan `reportlab` terinstall (pip install reportlab)."
    )
