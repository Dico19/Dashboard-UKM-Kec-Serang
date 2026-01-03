import numpy as np
import pandas as pd
from io import BytesIO
from pathlib import Path

REQUIRED_COLS = [
    "Bidang Usaha",
    "Nama Usaha",
    "Pendapatan Tahun Ini (Rp)",
    "Pendapatan Tahun Lalu (Rp)",
    "Total Biaya (Rp)",
    "Total Modal/Investasi (Rp)",
]


def to_num(s):
    return pd.to_numeric(s, errors="coerce")


def safe_div(a, b):
    """
    Safe division for Series/array-like.
    - Converts to numeric
    - Avoids divide by zero
    """
    a = to_num(a)
    b = to_num(b)
    b_safe = b.where((b != 0) & (~b.isna()))
    return a.div(b_safe)


def clip_minmax_score(series, low_q=0.05, high_q=0.95):
    """Normalize -> 0..100 with quantile clipping for robustness."""
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return pd.Series([np.nan] * len(s), index=s.index)

    lo = s.quantile(low_q)
    hi = s.quantile(high_q)

    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        # fallback: percentile rank
        return s.rank(pct=True) * 100

    sc = s.clip(lo, hi)
    sc = (sc - lo) / (hi - lo)
    return sc * 100


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # coerce numeric
    df["Pendapatan Tahun Ini (Rp)"] = to_num(df["Pendapatan Tahun Ini (Rp)"])
    df["Pendapatan Tahun Lalu (Rp)"] = to_num(df["Pendapatan Tahun Lalu (Rp)"])
    df["Total Biaya (Rp)"] = to_num(df["Total Biaya (Rp)"])
    df["Total Modal/Investasi (Rp)"] = to_num(df["Total Modal/Investasi (Rp)"])

    # KPIs
    df["Laba Bersih (Rp)"] = df["Pendapatan Tahun Ini (Rp)"] - df["Total Biaya (Rp)"]
    df["ROI (%)"] = safe_div(df["Laba Bersih (Rp)"], df["Total Modal/Investasi (Rp)"]) * 100
    df["Profit Margin (%)"] = safe_div(df["Laba Bersih (Rp)"], df["Pendapatan Tahun Ini (Rp)"]) * 100
    df["Growth Rate (%)"] = safe_div(
        (df["Pendapatan Tahun Ini (Rp)"] - df["Pendapatan Tahun Lalu (Rp)"]),
        df["Pendapatan Tahun Lalu (Rp)"],
    ) * 100

    # KPI tambahan
    df["Cost Ratio"] = safe_div(df["Total Biaya (Rp)"], df["Pendapatan Tahun Ini (Rp)"])  # makin kecil makin bagus

    # Valid flags
    df["Valid_Data"] = True
    df.loc[df["Total Modal/Investasi (Rp)"].isna() | (df["Total Modal/Investasi (Rp)"] <= 0), "Valid_Data"] = False
    df.loc[df["Pendapatan Tahun Ini (Rp)"].isna() | (df["Pendapatan Tahun Ini (Rp)"] <= 0), "Valid_Data"] = False
    df.loc[df["Pendapatan Tahun Lalu (Rp)"].isna() | (df["Pendapatan Tahun Lalu (Rp)"] <= 0), "Valid_Data"] = False
    df.loc[df["Total Biaya (Rp)"].isna() | (df["Total Biaya (Rp)"] < 0), "Valid_Data"] = False

    # Outlier detection (robust): ROI > p99.5 OR ProfitMargin > p99.5 OR Growth > p99.5
    df["Perlu_Verifikasi"] = False
    for col in ["ROI (%)", "Profit Margin (%)", "Growth Rate (%)"]:
        s = pd.to_numeric(df[col], errors="coerce")
        if s.dropna().empty:
            continue
        thr = s.quantile(0.995)
        df.loc[s > thr, "Perlu_Verifikasi"] = True

    df = df.round(2)
    return df


def score_and_classify(df: pd.DataFrame, w_roi=0.40, w_pm=0.35, w_gr=0.25) -> pd.DataFrame:
    df = df.copy()

    roi_sc = clip_minmax_score(df["ROI (%)"])
    pm_sc = clip_minmax_score(df["Profit Margin (%)"])
    gr_sc = clip_minmax_score(df["Growth Rate (%)"])

    df["Skor_ROI"] = roi_sc
    df["Skor_PM"] = pm_sc
    df["Skor_GR"] = gr_sc

    df["Skor_KPI"] = (w_roi * roi_sc + w_pm * pm_sc + w_gr * gr_sc)

    # jika invalid -> skor NaN
    df.loc[~df["Valid_Data"], ["Skor_ROI", "Skor_PM", "Skor_GR", "Skor_KPI"]] = np.nan

    # kategori berbasis skor
    df["Kategori_Skor"] = "Tidak Valid"
    df.loc[df["Skor_KPI"] >= 75, "Kategori_Skor"] = "Baik"
    df.loc[(df["Skor_KPI"] >= 55) & (df["Skor_KPI"] < 75), "Kategori_Skor"] = "Sedang"
    df.loc[(df["Skor_KPI"] < 55), "Kategori_Skor"] = "Kurang"

    return df


def make_recommendation(row) -> str:
    """Rekomendasi otomatis singkat per UKM."""
    if not bool(row.get("Valid_Data", True)):
        return "⚠️ Data belum valid. Lengkapi pendapatan, biaya, modal, dan pendapatan tahun lalu."

    rec = []
    roi = row.get("ROI (%)", np.nan)
    pm = row.get("Profit Margin (%)", np.nan)
    gr = row.get("Growth Rate (%)", np.nan)
    cr = row.get("Cost Ratio", np.nan)

    # aturan rekomendasi
    if pd.notna(roi) and roi < 10:
        rec.append("ROI rendah → optimalkan penggunaan modal, kurangi aset tidak produktif.")
    if pd.notna(pm) and pm < 5:
        rec.append("Profit Margin rendah → tekan biaya produksi/operasional, evaluasi harga bertahap.")
    if pd.notna(gr) and gr < 0:
        rec.append("Growth negatif → perlu strategi pemasaran/produk baru/ekspansi pasar.")
    if pd.notna(cr) and cr > 0.85:
        rec.append("Cost Ratio tinggi → biaya mendekati pendapatan, fokus efisiensi & kontrol biaya.")

    if not rec:
        rec.append("Kinerja relatif baik → pertahankan strategi dan siapkan rencana ekspansi bertahap.")

    return " • " + "\n • ".join(rec)


def add_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Rekomendasi"] = df.apply(make_recommendation, axis=1)
    return df


def data_quality_summary(df: pd.DataFrame) -> dict:
    s = {}
    s["total_rows"] = int(len(df))
    s["valid_rows"] = int(df["Valid_Data"].sum()) if "Valid_Data" in df.columns else 0
    s["invalid_rows"] = int((~df["Valid_Data"]).sum()) if "Valid_Data" in df.columns else 0
    s["need_verify"] = int(df["Perlu_Verifikasi"].sum()) if "Perlu_Verifikasi" in df.columns else 0

    # missing per required col
    miss = {}
    for c in REQUIRED_COLS:
        if c in df.columns:
            miss[c] = int(df[c].isna().sum())
        else:
            miss[c] = None
    s["missing_by_col"] = miss

    return s


def export_excel(df: pd.DataFrame, filename="KPI_UMKM_Serang.xlsx") -> tuple[bytes, str]:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="KPI")
    return out.getvalue(), filename


def generate_pdf_report(
    metrics: dict,
    top_best: pd.DataFrame,
    top_risk: pd.DataFrame,
    sektor_summary: pd.DataFrame,
    logo_path: str = "image/logo.png",
) -> bytes:
    """PDF sederhana (tanpa chart) pakai reportlab + logo."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.utils import ImageReader
    except Exception as e:
        raise RuntimeError("reportlab belum terinstall. Install: pip install reportlab") from e

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # =========================
    # LOGO (opsional)
    # =========================
    logo_shift = 0
    try:
        p = Path(logo_path)
        if not p.is_absolute():
            # core.py ada di folder app/ -> parent(1) = root project
            p = (Path(__file__).resolve().parents[1] / p).resolve()

        if p.exists():
            img = ImageReader(str(p))
            iw, ih = img.getSize()

            target_w = 2.2 * cm
            target_h = target_w * (ih / iw)

            x = 2 * cm
            y_logo = height - 2 * cm - target_h + 0.2 * cm
            c.drawImage(img, x, y_logo, width=target_w, height=target_h, mask="auto")
            logo_shift = target_w + 0.35 * cm
    except Exception:
        # kalau gagal baca logo, lanjut tanpa logo
        logo_shift = 0

    # =========================
    # HEADER
    # =========================
    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm + logo_shift, y, "Laporan Evaluasi KPI UKM - Kecamatan Serang")
    y -= 1.0 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm + logo_shift, y, f"Total UKM: {metrics.get('total', '-')}")
    y -= 0.55 * cm
    c.drawString(
        2 * cm + logo_shift,
        y,
        f"Rata-rata ROI: {metrics.get('avg_roi', 0):.2f}% | Profit Margin: {metrics.get('avg_pm', 0):.2f}% | Growth: {metrics.get('avg_gr', 0):.2f}%",
    )
    y -= 0.55 * cm
    c.drawString(
        2 * cm + logo_shift,
        y,
        f"Skor KPI rata-rata: {metrics.get('avg_score', 0):.2f} | Baik: {metrics.get('baik', 0)} | Sedang: {metrics.get('sedang', 0)} | Kurang: {metrics.get('kurang', 0)}",
    )
    y -= 0.9 * cm

    def table_block(title, df_block, y_pos):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y_pos, title)
        y_pos -= 0.6 * cm

        cols = ["Nama Usaha", "Bidang Usaha", "Skor_KPI", "Kategori_Skor"]
        df2 = df_block.copy()
        for col in cols:
            if col not in df2.columns:
                df2[col] = np.nan
        df2 = df2[cols].head(10)

        # header table
        c.setFont("Helvetica-Bold", 9)
        x0 = 2 * cm
        colw = [7 * cm, 4 * cm, 2.5 * cm, 3 * cm]
        headers = ["Nama Usaha", "Bidang", "Skor", "Kategori"]

        x = x0
        for htxt, ww in zip(headers, colw):
            c.drawString(x, y_pos, str(htxt))
            x += ww
        y_pos -= 0.45 * cm

        c.setFont("Helvetica", 9)
        for _, r in df2.iterrows():
            x = x0
            vals = [
                str(r["Nama Usaha"])[:42],
                str(r["Bidang Usaha"])[:18],
                f"{float(r['Skor_KPI']):.1f}" if pd.notna(r["Skor_KPI"]) else "-",
                str(r["Kategori_Skor"]),
            ]
            for v, ww in zip(vals, colw):
                c.drawString(x, y_pos, v)
                x += ww
            y_pos -= 0.42 * cm

            if y_pos < 3 * cm:
                c.showPage()
                y_pos = height - 2 * cm

        return y_pos - 0.5 * cm

    y = table_block("Top 10 UKM Terbaik", top_best, y)
    y = table_block("Top 10 UKM Butuh Perhatian", top_risk, y)

    # sektor summary (top 5)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Ringkasan Sektor (Top 5 Growth Rate)")
    y -= 0.6 * cm
    c.setFont("Helvetica", 9)

    ss = sektor_summary.copy()
    for col in ["Bidang Usaha", "Growth Rate (%)", "ROI (%)", "Profit Margin (%)"]:
        if col not in ss.columns:
            ss[col] = np.nan

    ss = ss.head(5)
    for _, r in ss.iterrows():
        bidang = str(r["Bidang Usaha"])
        gr = float(r["Growth Rate (%)"]) if pd.notna(r["Growth Rate (%)"]) else 0.0
        roi = float(r["ROI (%)"]) if pd.notna(r["ROI (%)"]) else 0.0
        pm = float(r["Profit Margin (%)"]) if pd.notna(r["Profit Margin (%)"]) else 0.0

        c.drawString(2 * cm, y, f"- {bidang}: Growth {gr:.2f}%, ROI {roi:.2f}%, PM {pm:.2f}%")
        y -= 0.42 * cm

        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm

    c.showPage()
    c.save()
    return buffer.getvalue()
