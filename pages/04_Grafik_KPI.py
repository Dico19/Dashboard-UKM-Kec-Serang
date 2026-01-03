# pages/Grafik_KPI.py
import streamlit as st
import pandas as pd
import plotly.express as px

from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Grafik KPI", page_icon="📊", layout="wide")

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

st.title("📊 Grafik KPI")

# =========================
# CONTROLS (main content)
# =========================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    view_mode = st.selectbox(
        "Mode",
        ["Top UMKM (Ranking)", "Ringkasan per Bidang", "Distribusi KPI (Box)"],
        index=0
    )

with col2:
    sort_by = st.selectbox(
        "Ranking berdasarkan",
        ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)"],
        index=0
    )

with col3:
    top_n = st.slider(
        "Top N",
        10, 200,
        int(st.session_state.get("top_n", 50)),
        5
    )

# =========================
# SAFETY: pastikan kolom KPI numeric
# =========================
kpi_cols = ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)"]
for c in kpi_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# =========================
# MODE 1: TOP UMKM (RANKING)
# =========================
if view_mode == "Top UMKM (Ranking)":
    if sort_by not in df.columns:
        st.warning(f"Kolom **{sort_by}** tidak ditemukan di data.")
        st.stop()

    d = df.dropna(subset=[sort_by]).sort_values(sort_by, ascending=False).head(top_n).copy()
    if d.empty:
        st.warning("Tidak ada data valid untuk ditampilkan.")
        st.stop()

    if "Nama Usaha" not in d.columns:
        st.warning("Kolom **Nama Usaha** tidak ditemukan.")
        st.stop()

    d["Nama Pendek"] = d["Nama Usaha"].astype(str).str.slice(0, 18) + "…"

    melt_cols = [c for c in kpi_cols if c in d.columns]
    long = d[["Nama Pendek", "Nama Usaha"] + melt_cols].melt(
        id_vars=["Nama Pendek", "Nama Usaha"],
        var_name="KPI",
        value_name="Nilai"
    )

    fig = px.bar(
        long,
        x="Nama Pendek",
        y="Nilai",
        color="KPI",
        barmode="group",
        hover_data={"Nama Usaha": True, "Nama Pendek": False, "Nilai": ":.2f"},
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(tickangle=-30, automargin=True)

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Top {len(d)} berdasarkan **{sort_by}**. Hover untuk nama lengkap.")

# =========================
# MODE 2: RINGKASAN PER BIDANG
# =========================
elif view_mode == "Ringkasan per Bidang":
    if "Bidang Usaha" not in df.columns:
        st.warning("Kolom **Bidang Usaha** tidak ditemukan.")
        st.stop()

    cols_agg = [c for c in kpi_cols if c in df.columns]
    if not cols_agg:
        st.warning("Kolom KPI tidak ditemukan.")
        st.stop()

    summary = (
        df.groupby("Bidang Usaha")[cols_agg]
        .mean(numeric_only=True)
        .round(2)
        .reset_index()
    )
    if "Skor_KPI" in summary.columns:
        summary = summary.sort_values("Skor_KPI", ascending=False)

    st.dataframe(summary, use_container_width=True, hide_index=True, height=360)

    metric = st.selectbox(
        "Grafik bidang berdasarkan:",
        [c for c in ["Skor_KPI", "Growth Rate (%)", "ROI (%)", "Profit Margin (%)"] if c in summary.columns],
        index=0
    )

    fig = px.bar(
        summary,
        x=metric,
        y="Bidang Usaha",
        orientation="h",
        hover_data=[c for c in cols_agg if c in summary.columns]
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# MODE 3: BOX PLOT DISTRIBUSI KPI
# =========================
else:
    kpi = st.selectbox(
        "Pilih KPI:",
        [c for c in kpi_cols if c in df.columns],
        index=0
    )

    d = df.dropna(subset=[kpi]).copy()
    if d.empty:
        st.warning("Tidak ada data valid.")
        st.stop()

    group = st.checkbox("Kelompokkan per Bidang (Top 12)", value=True)

    if group:
        if "Bidang Usaha" not in d.columns:
            st.warning("Kolom **Bidang Usaha** tidak ditemukan.")
            st.stop()

        top_bidang = d["Bidang Usaha"].value_counts().head(12).index
        d = d[d["Bidang Usaha"].isin(top_bidang)]

        fig = px.box(d, x="Bidang Usaha", y=kpi, points="outliers")
        fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=10, b=10))
        fig.update_xaxes(tickangle=-25, automargin=True)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Box plot untuk melihat sebaran + outlier. Ditampilkan Top 12 bidang agar tetap rapi.")
    else:
        fig = px.box(d, y=kpi, points="outliers")
        fig.update_layout(template="plotly_dark", height=520, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
