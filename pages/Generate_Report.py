import streamlit as st
import pandas as pd
from app.ui import inject_global_css, render_header
from app.core import export_excel, generate_pdf_report

st.set_page_config(page_title="Generate Report", page_icon="📄", layout="wide")
inject_global_css()

if "df_filtered" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_filtered"].copy()
st.title("📄 Generate Report (Excel + PDF)")

st.markdown("### ✅ Ringkasan Otomatis")
valid = df[df["Valid_Data"] == True].copy()

baik = int((valid["Kategori_Skor"] == "Baik").sum())
sedang = int((valid["Kategori_Skor"] == "Sedang").sum())
kurang = int((valid["Kategori_Skor"] == "Kurang").sum())

metrics = {
    "total": int(len(df)),
    "avg_roi": float(valid["ROI (%)"].mean(skipna=True)),
    "avg_pm": float(valid["Profit Margin (%)"].mean(skipna=True)),
    "avg_gr": float(valid["Growth Rate (%)"].mean(skipna=True)),
    "avg_score": float(valid["Skor_KPI"].mean(skipna=True)),
    "baik": baik,
    "sedang": sedang,
    "kurang": kurang,
}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", metrics["total"])
c2.metric("Skor rata-rata", f"{metrics['avg_score']:.2f}")
c3.metric("Baik", baik)
c4.metric("Kurang", kurang)

top_best = valid.sort_values("Skor_KPI", ascending=False).head(10)
top_risk = valid.sort_values("Skor_KPI", ascending=True).head(10)

sektor_summary = (
    valid.groupby("Bidang Usaha")[["ROI (%)","Profit Margin (%)","Growth Rate (%)","Skor_KPI"]]
      .mean(numeric_only=True).round(2)
      .reset_index()
      .sort_values("Growth Rate (%)", ascending=False)
)

st.markdown("### 🏆 Top 10 Terbaik")
st.dataframe(top_best[["Nama Usaha","Bidang Usaha","Skor_KPI","Kategori_Skor"]], use_container_width=True, hide_index=True)

st.markdown("### 🧯 Top 10 Butuh Perhatian")
st.dataframe(top_risk[["Nama Usaha","Bidang Usaha","Skor_KPI","Kategori_Skor","Rekomendasi"]], use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("## ⬇️ Download")

# Excel
excel_bytes, fname = export_excel(df, filename="Report_Evaluasi_KPI_UMKM.xlsx")
st.download_button("⬇️ Download Excel (Filtered)", excel_bytes, file_name=fname, use_container_width=True)

# PDF
try:
    pdf_bytes = generate_pdf_report(metrics, top_best, top_risk, sektor_summary)
    st.download_button("⬇️ Download PDF Report", pdf_bytes, file_name="Report_Evaluasi_KPI_UMKM.pdf", use_container_width=True)
except Exception as e:
    st.warning(f"PDF belum bisa dibuat: {e}\n\nSolusi: pastikan `reportlab` terinstall (pip install reportlab).")
