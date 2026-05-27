"""
footer.py — Footer bawah halaman utama.
Bebas emoji sesuai dengan UI_ROLE.md.
"""

import streamlit as st
from app.config import APP_NAME, APP_VERSION


def render_footer() -> None:
    st.markdown(
        """
        <div style="margin-top: 3rem; margin-bottom: 0;">
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin-bottom: 1rem;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="text-align:center; color:#94A3B8; font-size:0.7rem; font-weight:500; padding:0 0 1.5rem 0; letter-spacing:0.5px;">
            {APP_NAME.upper()} PROYEK AKURASI TINGGI &nbsp;·&nbsp; VERSI {APP_VERSION} &nbsp;·&nbsp;
            DIBUAT DENGAN STREAMLIT &amp; HUGGINGFACE TRANSFORMERS &nbsp;·&nbsp;
            <a href="#" style="color:#64748B; text-decoration:none; font-weight:600;">KEBIJAKAN DATA</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
