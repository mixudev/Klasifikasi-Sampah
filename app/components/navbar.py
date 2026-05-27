"""
navbar.py — Komponen navigasi sidebar untuk semua halaman.
Bebas emoji, monokromatik, dan tajam sesuai dengan UI_ROLE.md.
"""

import streamlit as st
from app.config import APP_NAME, APP_VERSION, PAGES, STATE_CURRENT_PAGE
from app.components.icons import render_svg


def render_navbar() -> str:
    """
    Render sidebar navigasi dan kembalikan nama halaman yang dipilih.

    Returns:
        Key halaman saat ini (str) dari dict PAGES.
    """
    with st.sidebar:
        # ── Brand Header (SVG Logo + Text) ────────────────
        logo_svg = render_svg("recycle", size=42, color="#16A34A")
        
        st.markdown(
            f"""
            <div style="text-align:center; padding: 1.2rem 0 0.8rem;">
                <div style="margin-bottom:0.4rem;">{logo_svg}</div>
                <h2 style="margin:0; font-size:1.3rem; font-weight:900; letter-spacing:-0.5px; color:#0F172A;">
                    {APP_NAME.upper()}
                </h2>
                <p style="color:#64748B; font-size:0.68rem; font-weight:600; margin:0.1rem 0 0 0; letter-spacing:0.5px;">
                    VERSION {APP_VERSION}
                </p>
            </div>
            <hr style="margin: 0.5rem 0 1rem 0; border: none; border-top: 1px solid #E5E7EB;">
            """,
            unsafe_allow_html=True,
        )

        # ── Navigasi Radio Buttons (Bebas Emoji) ──────────
        page_labels = list(PAGES.keys())

        # Inisialisasi state jika belum ada
        if STATE_CURRENT_PAGE not in st.session_state:
            st.session_state[STATE_CURRENT_PAGE] = page_labels[0]

        # Reset selection if invalid
        if st.session_state[STATE_CURRENT_PAGE] not in page_labels:
            st.session_state[STATE_CURRENT_PAGE] = page_labels[0]

        selected = st.radio(
            label="Navigasi Utama",
            options=page_labels,
            index=page_labels.index(st.session_state[STATE_CURRENT_PAGE]),
            label_visibility="collapsed",
        )

        st.session_state[STATE_CURRENT_PAGE] = selected

        # ── Tombol Keluar (Logout) ─────────────────────
        st.markdown("<hr style='margin: 1.5rem 0 1rem 0; border: none; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        if st.button("KELUAR (LOGOUT)", type="secondary", use_container_width=True):
            st.session_state["is_authenticated"] = False
            from app.utils.cache import save_auth_state
            save_auth_state(False)
            st.rerun()

        # ── Footer Sidebar ─────────────────────────────
        st.markdown(
            """
            <div style="margin-top: 1rem; padding: 0.5rem 0; text-align:center; font-size:0.65rem; color:#94A3B8; font-weight:500; letter-spacing:0.5px;">
                POWERED BY STREAMLIT & HF
            </div>
            """,
            unsafe_allow_html=True,
        )

    return PAGES[selected]
