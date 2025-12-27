import streamlit as st
import pandas as pd
import plotly.express as px
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Rata-rata Bidang", page_icon="🏭", layout="wide")
inject_global_css()

if "df_filtered" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_filtered"].copy()
st.title("🏭 Rata-rata KPI per Bidang Usaha")

summary = (
    df.groupby("Bidang Usaha")[["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)","Cost Ratio"]]
      .mean(numeric_only=True)
      .round(2)
      .reset_index()
      .sort_values("Skor_KPI", ascending=False)
)

st.dataframe(summary, use_container_width=True, hide_index=True, height=420)

metric = st.selectbox("Tampilkan grafik:", ["Skor_KPI","Growth Rate (%)","ROI (%)","Profit Margin (%)","Cost Ratio"], index=0)

fig = px.bar(summary, x=metric, y="Bidang Usaha", orientation="h",
             hover_data=["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)","Cost Ratio"])
fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

st.caption("Catatan: Cost Ratio lebih kecil = lebih efisien (biaya dibanding pendapatan).")
