import base64
from pathlib import Path
from textwrap import dedent
import streamlit as st


def load_image_base64(path: str) -> str:
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


def inject_global_css(
    bg_path: str = "image/bgsrg.png",
    hide_streamlit_topbar: bool = True,
):
    bg_base64 = load_image_base64(bg_path)

    bg_css = ""
    if bg_base64:
        bg_css = f"""
        .stApp {{
            background:
                radial-gradient(1200px 600px at 8% 10%, rgba(124,58,237,.18), transparent 60%),
                radial-gradient(900px 500px at 92% 30%, rgba(56,189,248,.12), transparent 55%),
                linear-gradient(rgba(2,6,23,0.86), rgba(2,6,23,0.86)),
                url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        """

    # Penting: jangan display:none total header, nanti tombol panah sidebar bisa hilang.
    # Kita bikin "invisible" tapi tetap ada.
    hide_bar_css = ""
    if hide_streamlit_topbar:
        hide_bar_css = """
        /* Header/toolbar dibuat transparan tapi tetap ada */
        header[data-testid="stHeader"]{
            background: transparent !important;
            box-shadow: none !important;
        }
        [data-testid="stToolbar"]{
            background: transparent !important;
            box-shadow: none !important;
        }
        [data-testid="stDecoration"]{ display:none !important; }

        /* Sembunyikan Deploy + menu bawaan (beda versi Streamlit bisa beda testid, jadi dibuat banyak selector) */
        [data-testid="stDeployButton"]{ display:none !important; }
        [data-testid="stToolbarActions"]{ display:none !important; }
        button[title="Deploy"]{ display:none !important; }
        #MainMenu{ visibility:hidden !important; }
        footer{ visibility:hidden !important; }

        /* ===== Pastikan tombol expand sidebar (<<) tetap muncul saat sidebar collapse ===== */
        div[data-testid="collapsedControl"],
        div[data-testid="stSidebarCollapsedControl"]{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;

            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 999999 !important;

            background: rgba(2,6,23,.55) !important;
            border: 1px solid rgba(255,255,255,.10) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px !important;
            box-shadow: 0 10px 26px rgba(0,0,0,.35) !important;
        }
        div[data-testid="collapsedControl"] button,
        div[data-testid="stSidebarCollapsedControl"] button{
            color: rgba(255,255,255,.92) !important;
        }

        /* Tombol collapse saat sidebar terbuka (kadang beda selector per versi) */
        button[data-testid="stSidebarCollapseButton"],
        button[title="Collapse sidebar"]{
            background: rgba(2,6,23,.35) !important;
            border: 1px solid rgba(255,255,255,.10) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 26px rgba(0,0,0,.25) !important;
        }
        """

    st.markdown(
        dedent(
            f"""
        <style>
        {bg_css}
        {hide_bar_css}

        /* Layout utama */
        .block-container {{
            padding-top: 1.0rem !important;
            padding-bottom: 2.2rem !important;
            max-width: 1180px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}

        /* =========================
           SIDEBAR PREMIUM LOOK
           ========================= */
        section[data-testid="stSidebar"] {{
            position: relative;
            background:
                radial-gradient(900px 500px at 40% 0%, rgba(124,58,237,.18), transparent 60%),
                radial-gradient(700px 420px at 70% 28%, rgba(56,189,248,.10), transparent 60%),
                linear-gradient(180deg, rgba(2,6,23,.98), rgba(2,6,23,.92)) !important;
            border-right: 1px solid rgba(148,163,184,.14) !important;
        }}
        section[data-testid="stSidebar"]::after {{
            content:"";
            position:absolute;
            top:0; right:0; bottom:0;
            width:1px;
            background: linear-gradient(180deg,
                rgba(124,58,237,.40),
                rgba(56,189,248,.22),
                rgba(255,255,255,.06));
            opacity:.65;
            pointer-events:none;
        }}
        section[data-testid="stSidebar"] * {{
            color: rgba(255,255,255,.92) !important;
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 10px !important;
        }}

        /* Scrollbar sidebar biar lebih halus (Chrome/Edge) */
        section[data-testid="stSidebar"] ::-webkit-scrollbar {{
            width: 10px;
        }}
        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,.10);
            border-radius: 999px;
            border: 2px solid rgba(2,6,23,.8);
        }}
        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {{
            background: rgba(124,58,237,.28);
        }}

        /* NAV pill */
        div[data-testid="stSidebarNav"] {{
            padding: 6px 10px 10px 10px !important;
        }}
        div[data-testid="stSidebarNav"] ul {{
            padding-left: 0 !important;
        }}
        div[data-testid="stSidebarNav"] li {{
            margin: 6px 0 !important;
        }}
        div[data-testid="stSidebarNav"] a {{
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            padding: 10px 12px !important;
            border-radius: 14px !important;
            background: rgba(255,255,255,.03) !important;
            border: 1px solid rgba(255,255,255,.07) !important;
            transition: transform .14s ease, background .14s ease, border .14s ease, box-shadow .14s ease;
            text-decoration: none !important;
        }}
        div[data-testid="stSidebarNav"] a:hover {{
            transform: translateX(3px);
            background: rgba(124,58,237,.16) !important;
            border-color: rgba(124,58,237,.35) !important;
            box-shadow: 0 10px 24px rgba(0,0,0,.25);
        }}
        div[data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: linear-gradient(135deg, rgba(124,58,237,.22), rgba(56,189,248,.12)) !important;
            border-color: rgba(124,58,237,.42) !important;
            box-shadow: 0 10px 26px rgba(124,58,237,.12);
        }}
        div[data-testid="stSidebarNav"] a[aria-current="page"]::before {{
            content:"";
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: rgba(34,197,94,.95);
            box-shadow: 0 0 14px rgba(34,197,94,.55);
            margin-right: 2px;
        }}

        /* =========================
           CARD / HERO
           ========================= */
        .glass {{
            background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
            border: 1px solid rgba(255,255,255,.10);
            box-shadow: 0 16px 40px rgba(0,0,0,.40);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 18px;
        }}

        .hero {{
            display:flex;
            gap:16px;
            align-items:center;
            padding: 18px 18px 16px 18px;
            margin-bottom: 12px;
        }}

        .hero-logo {{
            width: 110px;
            height: 110px;
            border-radius: 18px;
            display:flex;
            align-items:center;
            justify-content:center;
            overflow:hidden;
            flex: 0 0 auto;
            background: rgba(255,255,255,.04);
            border: 1px solid rgba(255,255,255,.10);
        }}
        .hero-logo.nobox {{
            background: transparent !important;
            border: none !important;
        }}
        .hero-logo img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            object-position: center;
            display:block;
            padding: 10px;
            box-sizing: border-box;
            filter: drop-shadow(0 6px 14px rgba(0,0,0,.40));
        }}

        .hero-title {{
            font-size: 28px;
            font-weight: 900;
            line-height: 1.1;
        }}
        .hero-sub {{
            color: rgba(148,163,184,.95);
            font-size: 13px;
            margin-top: 6px;
        }}
        .badge {{
            display:inline-flex;
            gap:8px;
            align-items:center;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(124,58,237,.16);
            border: 1px solid rgba(124,58,237,.35);
            color: rgba(255,255,255,.92);
            font-size: 12px;
            font-weight: 900;
            margin-top: 10px;
        }}

        /* uploader */
        div[data-testid="stFileUploader"] section {{
            border-radius: 14px !important;
            border: 1px dashed rgba(255,255,255,.22) !important;
            background: rgba(255,255,255,.04) !important;
        }}

        /* =========================
           KPI CARDS (rapi)
           ========================= */
        .kpi-grid{{
          display:grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
          margin-top: 12px;
        }}
        @media (max-width: 980px){{
          .kpi-grid{{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (max-width: 560px){{
          .kpi-grid{{ grid-template-columns: 1fr; }}
        }}
        .kpi-card{{
          padding: 14px 14px 12px 14px;
          border-radius: 16px;
          background: linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
          border: 1px solid rgba(255,255,255,.10);
          box-shadow: 0 16px 40px rgba(0,0,0,.28);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          overflow:hidden;
        }}
        .kpi-label{{
          font-size: 12px;
          font-weight: 900;
          letter-spacing: .2px;
          color: rgba(148,163,184,.95);
          margin: 0;
        }}
        .kpi-value{{
          margin-top: 6px;
          font-size: 26px;
          font-weight: 900;
          line-height: 1.05;
        }}
        .kpi-hint{{
          margin-top: 6px;
          font-size: 12px;
          color: rgba(148,163,184,.85);
          line-height: 1.25;
        }}
        </style>
        """
        ),
        unsafe_allow_html=True,
    )


def render_header(
    logo_path: str = "image/logo_umkm.png",
    no_logo_box: bool = True,
):
    logo_b64 = load_image_base64(logo_path)
    logo_cls = "hero-logo nobox" if no_logo_box else "hero-logo"

    logo_html = (
        f'<div class="{logo_cls}"><img src="data:image/png;base64,{logo_b64}" alt="Logo"></div>'
        if logo_b64
        else f'<div class="{logo_cls}"></div>'
    )

    st.markdown(
        dedent(
            f"""
        <div class="glass hero">
          {logo_html}
          <div>
            <div class="hero-title">Dashboard Evaluasi Kinerja Keuangan UKM Kecamatan Serang</div>
            <div class="hero-sub">Kecamatan Serang • KPI + Skor (0–100) • Rekomendasi Otomatis</div>
            <div class="badge">✨ App UI • Pages • Plotly • Manual Input • Export Excel/PDF</div>
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


# ===== KPI helpers =====
def _fmt_int(x):
    try:
        return f"{int(x):,}".replace(",", ".")
    except:
        return str(x)


def _fmt_float(x, d=2):
    try:
        return f"{float(x):.{d}f}"
    except:
        return str(x)


def render_kpi_summary(total_ukm, skor_kpi_avg, roi_avg, growth_avg):
    html = f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total UKM</div>
        <div class="kpi-value">{_fmt_int(total_ukm)}</div>
        <div class="kpi-hint">Jumlah sesuai filter</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Skor KPI Rata-rata</div>
        <div class="kpi-value">{_fmt_float(skor_kpi_avg, 2)}</div>
        <div class="kpi-hint">Skor gabungan (0–100)</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Rata-rata ROI</div>
        <div class="kpi-value">{_fmt_float(roi_avg, 2)}%</div>
        <div class="kpi-hint">Return on Investment</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Rata-rata Growth</div>
        <div class="kpi-value">{_fmt_float(growth_avg, 2)}%</div>
        <div class="kpi-hint">Pertumbuhan pendapatan</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
