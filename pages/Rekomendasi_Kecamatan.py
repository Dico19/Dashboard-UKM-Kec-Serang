import streamlit as st
import pandas as pd
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Rekomendasi Kecamatan", page_icon="🏛️", layout="wide")
inject_global_css()

if "df_all" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_all"].copy()
st.title("🏛️ Analisis Sektor & Rekomendasi Kecamatan")

sektor = (
    df.groupby("Bidang Usaha")[["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)","Cost Ratio"]]
      .mean(numeric_only=True)
      .round(2)
      .reset_index()
)

# stability: std growth (lebih kecil = stabil)
stab = (
    df.groupby("Bidang Usaha")["Growth Rate (%)"]
      .std(numeric_only=True)
      .reset_index()
      .rename(columns={"Growth Rate (%)":"Std Growth"})
)
sektor = sektor.merge(stab, on="Bidang Usaha", how="left").sort_values("Skor_KPI", ascending=False)

st.markdown("### 📌 Ringkasan Sektor")
st.dataframe(sektor, use_container_width=True, hide_index=True, height=420)

# policy insights
st.markdown("### 🧠 Insight Kebijakan (otomatis)")

# growth tinggi tapi margin rendah
hi_growth = sektor.sort_values("Growth Rate (%)", ascending=False).head(5)
low_margin = sektor.sort_values("Profit Margin (%)", ascending=True).head(5)

# ROI tinggi tapi growth rendah
hi_roi = sektor.sort_values("ROI (%)", ascending=False).head(5)
low_growth = sektor.sort_values("Growth Rate (%)", ascending=True).head(5)

most_stable = sektor.sort_values("Std Growth", ascending=True).head(5)

st.markdown("**1) Sektor paling stabil (Std Growth kecil):**")
for _, r in most_stable.iterrows():
    st.write(f"- {r['Bidang Usaha']} (Std Growth: {r['Std Growth']:.2f}) → cocok untuk penguatan & replikasi best practice.")

st.markdown("**2) Growth tinggi tapi margin relatif rendah (ramai tapi profit kecil):**")
mix = sektor[(sektor["Growth Rate (%)"] >= sektor["Growth Rate (%)"].quantile(0.7)) & (sektor["Profit Margin (%)"] <= sektor["Profit Margin (%)"].quantile(0.3))]
if mix.empty:
    st.write("- Tidak ada kombinasi kuat (berdasarkan data saat ini).")
else:
    for _, r in mix.head(8).iterrows():
        st.write(f"- {r['Bidang Usaha']} → sarankan pendampingan efisiensi biaya & strategi harga.")

st.markdown("**3) ROI tinggi tapi growth rendah (stabil tapi kurang ekspansi):**")
mix2 = sektor[(sektor["ROI (%)"] >= sektor["ROI (%)"].quantile(0.7)) & (sektor["Growth Rate (%)"] <= sektor["Growth Rate (%)"].quantile(0.3))]
if mix2.empty:
    st.write("- Tidak ada kombinasi kuat (berdasarkan data saat ini).")
else:
    for _, r in mix2.head(8).iterrows():
        st.write(f"- {r['Bidang Usaha']} → dorong program pemasaran/akses pasar untuk menaikkan pertumbuhan.")

st.info("Rekomendasi ini bisa kamu pakai untuk narasi laporan: sektor prioritas pembinaan & strategi kecamatan.")
