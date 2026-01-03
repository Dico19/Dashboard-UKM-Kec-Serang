# pages/07_Rekomendasi_Kecamatan.py
import streamlit as st
import pandas as pd

from app.ui import inject_global_css, render_header

st.set_page_config(page_title="Rekomendasi Kecamatan", page_icon="🏛️", layout="wide")
inject_global_css(bg_path="image/bgsrg.png")
render_header(logo_path="image/logo.png")

# =========================
# GUARD: data harus disiapkan dari Upload
# =========================
if "df_all" not in st.session_state:
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

df = st.session_state["df_all"].copy()

# =========================
# HEADER
# =========================
st.markdown("""
<div class="glass" style="padding:18px; margin-bottom:14px;">
  <div style="font-weight:900; font-size:20px;">🏛️ Analisis Sektor & Rekomendasi Kecamatan</div>
  <div style="color:rgba(226,232,240,.85); margin-top:6px; line-height:1.6;">
    Halaman ini menyusun <b>prioritas pembinaan</b> berbasis data KPI (Skor, ROI, Margin, Growth, dan Efisiensi),
    lalu menghasilkan <b>insight kebijakan</b> + rekomendasi program yang bisa dipakai untuk narasi laporan.
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# VALIDASI KOLOM MINIMAL
# =========================
if "Bidang Usaha" not in df.columns:
    st.warning("Kolom **Bidang Usaha** tidak ditemukan.")
    st.dataframe(df.head(50), use_container_width=True)
    st.stop()

kpi_cols_order = ["Skor_KPI", "ROI (%)", "Profit Margin (%)", "Growth Rate (%)", "Cost Ratio"]
kpi_cols = [c for c in kpi_cols_order if c in df.columns]

if not kpi_cols:
    st.warning("Kolom KPI (Skor_KPI / ROI / Profit Margin / Growth / Cost Ratio) tidak ditemukan.")
    st.dataframe(df.head(50), use_container_width=True)
    st.stop()

# pastikan numeric
for c in kpi_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# =========================
# (OPSIONAL) FILTER KECAMATAN kalau ada kolomnya
# =========================
if "Kecamatan" in df.columns:
    st.markdown('<div class="glass" style="padding:14px; margin-bottom:14px;">', unsafe_allow_html=True)
    st.markdown("### 🎯 Fokus Wilayah (Opsional)")
    kec_opts = sorted(df["Kecamatan"].dropna().astype(str).unique().tolist())
    default_kec = ["Serang"] if "Serang" in kec_opts else []
    selected_kec = st.multiselect("Pilih kecamatan:", options=kec_opts, default=default_kec)
    if selected_kec:
        df = df[df["Kecamatan"].astype(str).isin(selected_kec)].copy()
        st.caption(f"Menampilkan data untuk: **{', '.join(selected_kec)}**")
    else:
        st.caption("Tidak memilih kecamatan → menampilkan semua data.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# RINGKASAN SEKTOR (MEAN)
# =========================
sektor = (
    df.groupby("Bidang Usaha")[kpi_cols]
      .mean()
      .round(2)
      .reset_index()
)

# stability: std growth
if "Growth Rate (%)" in df.columns:
    stab = (
        df.groupby("Bidang Usaha")["Growth Rate (%)"]
          .std()
          .reset_index()
          .rename(columns={"Growth Rate (%)": "Std Growth"})
    )
    sektor = sektor.merge(stab, on="Bidang Usaha", how="left")
else:
    sektor["Std Growth"] = pd.NA

# ranking default
if "Skor_KPI" in sektor.columns:
    sektor = sektor.sort_values("Skor_KPI", ascending=False)
else:
    sektor = sektor.sort_values("Bidang Usaha")

# =========================
# RINGKASAN EKSEKUTIF (AUTO)
# =========================
def pick_first(df_, col):
    if col in df_.columns and df_[col].dropna().shape[0] > 0:
        return df_.sort_values(col, ascending=False).iloc[0]["Bidang Usaha"]
    return "-"

top_score_sector = pick_first(sektor, "Skor_KPI")
top_growth_sector = pick_first(sektor, "Growth Rate (%)")
top_roi_sector = pick_first(sektor, "ROI (%)")

stable_sector = "-"
if "Std Growth" in sektor.columns and sektor["Std Growth"].notna().any():
    stable_sector = sektor.sort_values("Std Growth", ascending=True).iloc[0]["Bidang Usaha"]

st.markdown(f"""
<div class="glass insight" style="margin-bottom:14px;">
  <div style="font-size:14px; color: rgba(255,255,255,.92); line-height:1.6;">
    💡 <b>Ringkasan Eksekutif:</b>
    Sektor dengan <b>Skor KPI tertinggi</b> adalah <u>{top_score_sector}</u>,
    sektor dengan <b>pertumbuhan (Growth) tertinggi</b> adalah <u>{top_growth_sector}</u>,
    dan sektor dengan <b>ROI tertinggi</b> adalah <u>{top_roi_sector}</u>.
    Untuk <b>stabilitas pertumbuhan</b>, sektor paling stabil (Std Growth terendah) adalah <u>{stable_sector}</u>.
  </div>
</div>
""", unsafe_allow_html=True)

# =========================
# TABEL RINGKASAN SEKTOR
# =========================
st.markdown("### 📌 Ringkasan Sektor (Rata-rata KPI)")
st.dataframe(sektor, use_container_width=True, hide_index=True, height=420)

# =========================
# INSIGHT + PRIORITAS PROGRAM (lebih "policy")
# =========================
st.markdown("### 🧭 Prioritas Program Pembinaan (Otomatis)")

colA, colB, colC = st.columns(3)

# 1) Stabil (Std Growth kecil)
with colA:
    st.markdown('<div class="glass" style="padding:14px; height:100%;">', unsafe_allow_html=True)
    st.markdown("#### 🧱 Program Stabilitas & Replikasi")
    if "Std Growth" in sektor.columns and sektor["Std Growth"].notna().any():
        stable = sektor.sort_values("Std Growth", ascending=True).head(5)
        st.caption("Target: sektor stabil → mudah direplikasi jadi best practice.")
        for _, r in stable.iterrows():
            val = r.get("Std Growth", None)
            if pd.notna(val):
                st.write(f"- **{r['Bidang Usaha']}** (Std Growth: {float(val):.2f})")
            else:
                st.write(f"- **{r['Bidang Usaha']}**")
    else:
        st.caption("Butuh kolom Growth Rate (%) untuk menghitung stabilitas.")
    st.markdown("</div>", unsafe_allow_html=True)

# 2) Growth tinggi tapi margin rendah
with colB:
    st.markdown('<div class="glass" style="padding:14px; height:100%;">', unsafe_allow_html=True)
    st.markdown("#### 🔥 Program Efisiensi & Harga")
    if "Growth Rate (%)" in sektor.columns and "Profit Margin (%)" in sektor.columns:
        qg = sektor["Growth Rate (%)"].quantile(0.7)
        qm = sektor["Profit Margin (%)"].quantile(0.3)
        mix = sektor[(sektor["Growth Rate (%)"] >= qg) & (sektor["Profit Margin (%)"] <= qm)].copy()
        st.caption("Target: ramai permintaan, tapi profit tipis → butuh efisiensi & strategi harga.")
        if mix.empty:
            st.write("- Tidak ada sektor yang masuk kategori ini (berdasarkan data saat ini).")
        else:
            for _, r in mix.head(8).iterrows():
                st.write(f"- **{r['Bidang Usaha']}** (Growth {r['Growth Rate (%)']:.2f}%, PM {r['Profit Margin (%)']:.2f}%)")
    else:
        st.caption("Butuh Growth Rate (%) + Profit Margin (%).")
    st.markdown("</div>", unsafe_allow_html=True)

# 3) ROI tinggi tapi growth rendah
with colC:
    st.markdown('<div class="glass" style="padding:14px; height:100%;">', unsafe_allow_html=True)
    st.markdown("#### 📣 Program Akses Pasar & Ekspansi")
    if "ROI (%)" in sektor.columns and "Growth Rate (%)" in sektor.columns:
        qroi = sektor["ROI (%)"].quantile(0.7)
        qgl = sektor["Growth Rate (%)"].quantile(0.3)
        mix2 = sektor[(sektor["ROI (%)"] >= qroi) & (sektor["Growth Rate (%)"] <= qgl)].copy()
        st.caption("Target: untung tinggi tapi lambat tumbuh → dorong pemasaran & akses pasar.")
        if mix2.empty:
            st.write("- Tidak ada sektor yang masuk kategori ini (berdasarkan data saat ini).")
        else:
            for _, r in mix2.head(8).iterrows():
                st.write(f"- **{r['Bidang Usaha']}** (ROI {r['ROI (%)']:.2f}%, Growth {r['Growth Rate (%)']:.2f}%)")
    else:
        st.caption("Butuh ROI (%) + Growth Rate (%).")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Rekomendasi Aksi (lebih jelas + bisa dipakai laporan)
# =========================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### ✅ Rekomendasi Aksi Kecamatan (Siap Tempel ke Laporan)")

recs = []

# template rekomendasi
def add_rec(title, when, actions):
    recs.append((title, when, actions))

add_rec(
    "Penguatan Sektor Stabil",
    "Jika sektor punya Std Growth rendah (stabil) dan Skor KPI relatif tinggi.",
    [
        "Jadikan sektor stabil sebagai **model pembinaan** (best practice).",
        "Buat modul pelatihan singkat: SOP produksi, pencatatan keuangan, dan layanan pelanggan.",
        "Dorong kemitraan antar UKM untuk replikasi pola bisnis yang sudah terbukti."
    ]
)

add_rec(
    "Efisiensi Biaya & Perbaikan Harga",
    "Jika Growth tinggi tapi Profit Margin rendah (ramai tapi profit kecil).",
    [
        "Audit biaya: bahan baku, energi, tenaga kerja, logistik → cari pos pemborosan.",
        "Pelatihan **penentuan harga (pricing)** + bundling + strategi promo yang tidak menggerus margin.",
        "Bantu akses supplier lebih murah (koperasi/supplier kolektif)."
    ]
)

add_rec(
    "Akses Pasar & Ekspansi",
    "Jika ROI tinggi tapi Growth rendah (profit bagus tapi kurang berkembang).",
    [
        "Program onboarding marketplace + packaging + branding.",
        "Bantu perluasan channel penjualan: B2B lokal, event kecamatan, dan kemitraan retail.",
        "Fasilitasi perizinan/sertifikasi sederhana agar bisa masuk pasar lebih luas."
    ]
)

add_rec(
    "Efisiensi Operasional",
    "Jika Cost Ratio tinggi (biaya mendekati pendapatan) atau Skor KPI rendah.",
    [
        "Pendampingan pencatatan keuangan sederhana untuk kontrol biaya (harian/mingguan).",
        "Standarisasi proses produksi dan pembelian bahan baku.",
        "Targetkan penurunan Cost Ratio bertahap dalam 1–3 bulan."
    ]
)

for title, when, actions in recs:
    st.markdown(f"""
    <div class="glass" style="padding:14px; margin-bottom:10px;">
      <div style="font-weight:900; font-size:15px;">🧩 {title}</div>
      <div style="color:rgba(226,232,240,.85); margin-top:6px; font-size:13px;">
        <b>Kapan dipakai:</b> {when}
      </div>
      <div style="margin-top:8px; color:rgba(226,232,240,.92); font-size:13px; line-height:1.7;">
        {"".join([f"• {a}<br/>" for a in actions])}
      </div>
    </div>
    """, unsafe_allow_html=True)

st.info("Catatan: rekomendasi bersifat data-driven dari rata-rata KPI per sektor. Kamu bisa pakai ini untuk narasi program kerja kecamatan.")
