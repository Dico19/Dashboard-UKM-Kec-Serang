import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Pertumbuhan", page_icon="📈", layout="wide")
inject_global_css()

if "df_filtered" not in st.session_state:
    st.warning("Upload / input data dulu di halaman Home (Dashboard).")
    st.stop()

df = st.session_state["df_filtered"].copy()

st.title("📈 Analisis Pertumbuhan ")

df["Pendapatan Tahun Ini (Rp)"] = pd.to_numeric(df["Pendapatan Tahun Ini (Rp)"], errors="coerce")
df["Pendapatan Tahun Lalu (Rp)"] = pd.to_numeric(df["Pendapatan Tahun Lalu (Rp)"], errors="coerce")
df["Growth Rate (%)"] = pd.to_numeric(df["Growth Rate (%)"], errors="coerce")

mode = st.selectbox("Mode", ["Scatter (Tahun Lalu vs Tahun Ini)", "Top Growth Rate", "Ringkasan per Bidang"], index=0)

if mode == "Scatter (Tahun Lalu vs Tahun Ini)":
    d = df.dropna(subset=["Pendapatan Tahun Ini (Rp)","Pendapatan Tahun Lalu (Rp)"]).copy()
    if d.empty:
        st.warning("Data pendapatan belum lengkap.")
        st.stop()

    fig = px.scatter(
        d,
        x="Pendapatan Tahun Lalu (Rp)",
        y="Pendapatan Tahun Ini (Rp)",
        color="Bidang Usaha",
        hover_name="Nama Usaha",
        hover_data={"Growth Rate (%)":":.2f","Skor_KPI":":.2f","Kategori_Skor":True},
        opacity=0.75
    )

    minv = float(pd.concat([d["Pendapatan Tahun Lalu (Rp)"], d["Pendapatan Tahun Ini (Rp)"]]).min())
    maxv = float(pd.concat([d["Pendapatan Tahun Lalu (Rp)"], d["Pendapatan Tahun Ini (Rp)"]]).max())

    fig.add_trace(go.Scatter(
        x=[minv, maxv],
        y=[minv, maxv],
        mode="lines",
        name="Garis y=x (stabil)",
        line=dict(dash="dash")
    ))

    fig.update_layout(template="plotly_dark", height=640, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Di atas garis y=x berarti pendapatan naik.")

elif mode == "Top Growth Rate":
    top_n = st.slider("Top N", 10, 200, int(st.session_state.get("top_n", 50)), 5)
    d = df.dropna(subset=["Growth Rate (%)"]).sort_values("Growth Rate (%)", ascending=False).head(top_n).copy()
    if d.empty:
        st.warning("Tidak ada Growth Rate valid.")
        st.stop()

    d["Nama Pendek"] = d["Nama Usaha"].astype(str).str.slice(0, 18) + "…"
    fig = px.bar(
        d,
        x="Nama Pendek",
        y="Growth Rate (%)",
        hover_data={"Nama Usaha":True,"Nama Pendek":False,"Skor_KPI":":.2f","Kategori_Skor":True}
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(tickangle=-30, automargin=True)
    st.plotly_chart(fig, use_container_width=True)

else:
    summary = (
        df.groupby("Bidang Usaha")[["Pendapatan Tahun Lalu (Rp)","Pendapatan Tahun Ini (Rp)","Growth Rate (%)","Skor_KPI"]]
          .mean(numeric_only=True)
          .round(2)
          .reset_index()
          .sort_values("Growth Rate (%)", ascending=False)
    )
    st.dataframe(summary, use_container_width=True, hide_index=True, height=360)

    fig = px.bar(summary, x="Growth Rate (%)", y="Bidang Usaha", orientation="h",
                 hover_data=["Pendapatan Tahun Lalu (Rp)","Pendapatan Tahun Ini (Rp)","Skor_KPI"])
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
