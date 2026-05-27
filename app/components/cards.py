"""
cards.py — Komponen kartu UI yang dipakai di berbagai halaman.
Menerapkan gaya siku penuh (border-radius: 0px) dan bebas emoji sesuai UI_ROLE.md.
"""

import streamlit as st
from app.services.predictor import PredictionResult
from app.components.icons import render_svg, CLASS_ICON_MAPPING


def render_result_card(result: PredictionResult) -> None:
    """Tampilkan kartu hasil deteksi utama."""
    if result.error:
        st.error(result.error)
        return

    confidence_pct = round(result.confidence * 100, 1)
    
    icon_name = CLASS_ICON_MAPPING.get(result.label, "recycle")
    svg_html = render_svg(icon_name, size=36, color=result.color)

    card_html = f'<div style="border: 1px solid #0F172A; border-left: 6px solid {result.color}; background: #FFFFFF; border-radius: 0px; padding: 1.2rem 1.5rem; margin: 1rem 0;"><div style="margin-bottom: 0.5rem;">{svg_html}</div><h2 style="margin:0 0 0.3rem 0; color:#0F172A; font-weight:800; font-size:1.6rem; letter-spacing:-0.5px;">{result.label.upper()} ({result.source.upper()})</h2><p style="margin:0; color:#475569; font-size:0.9rem;">Tingkat Keyakinan: <strong style="color:#0F172A;">{confidence_pct}%</strong>{" [TERVERIFIKASI]" if result.is_confident else " [DI BAWAH AMBANG BATAS]"}</p></div>'
    st.markdown(card_html, unsafe_allow_html=True)

    # Progress bar confidence
    st.progress(result.confidence, text=f"Tingkat Keyakinan: {confidence_pct}%")

    # Saran penanganan
    with st.expander("Saran Penanganan", expanded=True):
        st.info(result.tip)


def render_class_badge(label: str, color: str) -> None:
    """Badge kecil untuk menampilkan kelas sampah."""
    icon_name = CLASS_ICON_MAPPING.get(label, "recycle")
    svg_html = render_svg(icon_name, size=14, color=color)
    st.markdown(
        f"""
        <span style="
            background:#FFFFFF;
            border:1px solid {color};
            color:{color};
            border-radius:0px;
            padding:3px 8px;
            font-size:0.72rem;
            font-weight:700;
            display:inline-flex;
            align-items:center;
            gap:4px;
            letter-spacing:0.5px;
        ">{svg_html} {label.upper()}</span>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(title: str, value: str | int | float, icon: str = "analytics", color: str = "#0F172A") -> None:
    """Kartu statistik sederhana (dipakai di analytics & dashboard)."""
    svg_html = render_svg(icon, size=24, color=color)
    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border-radius:0px;
            padding:1.2rem;
            text-align:left;
            border:1px solid #E2E8F0;
            border-top: 3px solid {color};
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <span style="font-size:0.75rem; color:#475569; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{title}</span>
                {svg_html}
            </div>
            <div style="font-size:1.8rem; font-weight:900; color:#0F172A; letter-spacing:-1px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
