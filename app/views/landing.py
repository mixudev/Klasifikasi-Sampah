"""
landing.py — Halaman 4: Landing Page / Beranda.
Menampilkan hero section, penjelasan, dan CTA ke halaman Scan.
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
from app.config import APP_NAME, APP_TAGLINE, CLASS_COLORS, WASTE_CLASSES, STATE_CURRENT_PAGE
from app.components.icons import render_svg, CLASS_ICON_MAPPING


def render() -> None:
    # ── Hero Section (Industrial Style) ──────────────────────────────
    logo_svg = render_svg("recycle", size=64, color="#16A34A")
    st.markdown(
        f"""
        <div style="text-align:center; padding:2rem 1rem 1.5rem;">
            <div style="margin-bottom: 0.8rem;">{logo_svg}</div>
            <h1 style="font-size:2.6rem; font-weight:900; letter-spacing:-1px; margin:0.2rem 0; color:#0F172A;">
                {APP_NAME.upper()}
            </h1>
            <p style="font-size:1.1rem; color:#475569; max-width:600px; margin:0.5rem auto 1.5rem; line-height:1.6;">
                {APP_TAGLINE} — Unggah foto sampah Anda untuk diklasifikasikan secara cerdas. AI akan mengenali kategorinya dan memberikan panduan penanganan demi kelestarian bumi.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_cta, _ = st.columns([1, 2])
    with col_cta:
        # Menghapus emoji dari label tombol
        if st.button("MULAI SCAN SEKARANG", use_container_width=True, type="primary"):
            st.session_state[STATE_CURRENT_PAGE] = "Scan Sampah"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Kelas Sampah ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1.2rem;">
            Kategori Sampah yang Didukung
        </h3>
        """,
        unsafe_allow_html=True,
    )
    
    cols = st.columns(3)
    for i, cls in enumerate(WASTE_CLASSES):
        color = CLASS_COLORS.get(cls, "#475569")
        icon_name = CLASS_ICON_MAPPING.get(cls, "recycle")
        svg_html = render_svg(icon_name, size=32, color=color)
        
        with cols[i % 3]:
            card_html = f'<div style="background:#FFFFFF; border:1px solid #E5E7EB; border-left:4px solid {color}; border-radius:0px; padding:1rem; text-align:left; margin-bottom:0.8rem;"><div style="display:flex; align-items:center; gap:0.6rem;">{svg_html}<span style="font-weight:800; font-size:0.9rem; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px;">{cls}</span></div></div>'
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Dampak Lingkungan (Editorial Metrics) ──────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1.2rem;">
            Mengapa Pemilahan Sampah Penting?
        </h3>
        """,
        unsafe_allow_html=True,
    )
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Estimasi Sampah Indonesia / Hari", "175.000 ton")
    with c2:
        st.metric("Tingkat Daur Ulang Saat Ini", "< 15%")
    with c3:
        st.metric("Potensi Ekonomi Daur Ulang", "Rp 30 Triliun / Tahun")

    st.info(
        "WasteAI memanfaatkan model Computer Vision berbasis Vision Transformer (ViT) "
        "yang dilatih secara khusus untuk mengidentifikasi material daur ulang dan B3 secara instan."
    )
