import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Grafik KPI", page_icon="📊", layout="wide")
inject_global_css()

if "df_filtered" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_filtered"].copy()

st.title("📊 Grafik KPI ")

col1, col2, col3 = st.columns([1,1,1])
with col1:
    view_mode = st.selectbox("Mode", ["Top UMKM (Ranking)", "Ringkasan per Bidang", "Distribusi KPI (Box)"])
with col2:
    sort_by = st.selectbox("Ranking berdasarkan", ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)"], index=0)
with col3:
    top_n = st.slider("Top N", 10, 200, int(st.session_state.get("top_n", 50)), 5)

for c in ["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

if view_mode == "Top UMKM (Ranking)":
    d = df.dropna(subset=[sort_by]).sort_values(sort_by, ascending=False).head(top_n).copy()
    if d.empty:
        st.warning("Tidak ada data valid.")
        st.stop()

    d["Nama Pendek"] = d["Nama Usaha"].astype(str).str.slice(0, 18) + "…"
    long = d[["Nama Pendek","Nama Usaha","Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)"]].melt(
        id_vars=["Nama Pendek","Nama Usaha"], var_name="KPI", value_name="Nilai"
    )

    fig = px.bar(
        long,
        x="Nama Pendek",
        y="Nilai",
        color="KPI",
        barmode="group",
        hover_data={"Nama Usaha": True, "Nama Pendek": False, "Nilai":":.2f"},
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(tickangle=-30, automargin=True)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Top {len(d)} berdasarkan **{sort_by}**. Hover untuk nama lengkap.")

elif view_mode == "Ringkasan per Bidang":
    summary = (
        df.groupby("Bidang Usaha")[["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)"]]
          .mean(numeric_only=True)
          .round(2)
          .reset_index()
          .sort_values("Skor_KPI", ascending=False)
    )
    st.dataframe(summary, use_container_width=True, hide_index=True, height=360)

    metric = st.selectbox("Grafik bidang berdasarkan:", ["Skor_KPI","Growth Rate (%)","ROI (%)","Profit Margin (%)"], index=0)
    fig = px.bar(summary, x=metric, y="Bidang Usaha", orientation="h", hover_data=["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)"])
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

else:
    kpi = st.selectbox("Pilih KPI:", ["Skor_KPI","ROI (%)","Profit Margin (%)","Growth Rate (%)"], index=0)
    d = df.dropna(subset=[kpi]).copy()
    if d.empty:
        st.warning("Tidak ada data valid.")
        st.stop()

    group = st.checkbox("Kelompokkan per Bidang (Top 12)", value=True)
    if group:
        top_bidang = d["Bidang Usaha"].value_counts().head(12).index
        d = d[d["Bidang Usaha"].isin(top_bidang)]

        fig = px.box(d, x="Bidang Usaha", y=kpi, points="outliers")
        fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10))
        fig.update_xaxes(tickangle=-25, automargin=True)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Box plot untuk melihat sebaran + outlier. Ditampilkan Top 12 bidang agar tetap rapi.")
    else:
        fig = px.box(d, y=kpi, points="outliers")
        fig.update_layout(template="plotly_dark", height=520, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
