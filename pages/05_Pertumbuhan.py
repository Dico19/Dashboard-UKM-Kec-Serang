# pages/Pertumbuhan.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Pertumbuhan", page_icon="📈", layout="wide")

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

st.title("📈 Analisis Pertumbuhan")

# =========================
# SAFE NUMERIC CONVERSION
# =========================
for col in ["Pendapatan Tahun Ini (Rp)", "Pendapatan Tahun Lalu (Rp)", "Growth Rate (%)", "Skor_KPI"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

mode = st.selectbox(
    "Mode",
    ["Scatter (Tahun Lalu vs Tahun Ini)", "Top Growth Rate", "Ringkasan per Bidang"],
    index=0
)

# =========================
# MODE 1: SCATTER
# =========================
if mode == "Scatter (Tahun Lalu vs Tahun Ini)":
    needed = ["Pendapatan Tahun Ini (Rp)", "Pendapatan Tahun Lalu (Rp)"]
    if not all(c in df.columns for c in needed):
        st.warning("Kolom pendapatan tidak lengkap untuk scatter.")
        st.stop()

    d = df.dropna(subset=needed).copy()
    if d.empty:
        st.warning("Data pendapatan belum lengkap.")
        st.stop()

    color_col = "Bidang Usaha" if "Bidang Usaha" in d.columns else None
    hover_name = "Nama Usaha" if "Nama Usaha" in d.columns else None

    hover_data = {}
    if "Growth Rate (%)" in d.columns:
        hover_data["Growth Rate (%)"] = ":.2f"
    if "Skor_KPI" in d.columns:
        hover_data["Skor_KPI"] = ":.2f"
    if "Kategori_Skor" in d.columns:
        hover_data["Kategori_Skor"] = True

    fig = px.scatter(
        d,
        x="Pendapatan Tahun Lalu (Rp)",
        y="Pendapatan Tahun Ini (Rp)",
        color=color_col,
        hover_name=hover_name,
        hover_data=hover_data,
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

    fig.update_layout(template="plotly_dark", height=640, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Di atas garis y=x berarti pendapatan naik.")

# =========================
# MODE 2: TOP GROWTH
# =========================
elif mode == "Top Growth Rate":
    if "Growth Rate (%)" not in df.columns:
        st.warning("Kolom **Growth Rate (%)** tidak ditemukan.")
        st.stop()

    top_n = st.slider("Top N", 10, 200, int(st.session_state.get("top_n", 50)), 5)

    d = df.dropna(subset=["Growth Rate (%)"]).sort_values("Growth Rate (%)", ascending=False).head(top_n).copy()
    if d.empty:
        st.warning("Tidak ada Growth Rate valid.")
        st.stop()

    if "Nama Usaha" in d.columns:
        d["Nama Pendek"] = d["Nama Usaha"].astype(str).str.slice(0, 18) + "…"
        x_col = "Nama Pendek"
    else:
        d["Nama Pendek"] = [f"UKM {i+1}" for i in range(len(d))]
        x_col = "Nama Pendek"

    hover_data = {"Growth Rate (%)": ":.2f"}
    if "Nama Usaha" in d.columns:
        hover_data["Nama Usaha"] = True
        hover_data["Nama Pendek"] = False
    if "Skor_KPI" in d.columns:
        hover_data["Skor_KPI"] = ":.2f"
    if "Kategori_Skor" in d.columns:
        hover_data["Kategori_Skor"] = True

    fig = px.bar(
        d,
        x=x_col,
        y="Growth Rate (%)",
        hover_data=hover_data
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(tickangle=-30, automargin=True)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# MODE 3: RINGKASAN PER BIDANG
# =========================
else:
    if "Bidang Usaha" not in df.columns:
        st.warning("Kolom **Bidang Usaha** tidak ditemukan.")
        st.stop()

    cols = [c for c in ["Pendapatan Tahun Lalu (Rp)", "Pendapatan Tahun Ini (Rp)", "Growth Rate (%)", "Skor_KPI"] if c in df.columns]
    if not cols:
        st.warning("Kolom yang dibutuhkan untuk ringkasan tidak tersedia.")
        st.stop()

    summary = (
        df.groupby("Bidang Usaha")[cols]
        .mean(numeric_only=True)
        .round(2)
        .reset_index()
    )
    if "Growth Rate (%)" in summary.columns:
        summary = summary.sort_values("Growth Rate (%)", ascending=False)

    st.dataframe(summary, use_container_width=True, hide_index=True, height=360)

    if "Growth Rate (%)" in summary.columns:
        hover_cols = [c for c in ["Pendapatan Tahun Lalu (Rp)", "Pendapatan Tahun Ini (Rp)", "Skor_KPI"] if c in summary.columns]
        fig = px.bar(
            summary,
            x="Growth Rate (%)",
            y="Bidang Usaha",
            orientation="h",
            hover_data=hover_cols
        )
        fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Kolom Growth Rate (%) tidak ada, jadi grafik tidak ditampilkan.")
