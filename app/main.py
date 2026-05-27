"""
main.py — Entry point utama aplikasi WasteAI.
Mengatur tata letak Streamlit, memicu inisialisasi cache, dan melakukan injeksi CSS global.
"""

import sys
from pathlib import Path

# Tambahkan parent directory ke sys.path agar bisa import `app` module
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.utils.cache import init_session_state
from app.router import route_page
from app.components.footer import render_footer


def main() -> None:
    # 1. Konfigurasi dasar Streamlit
    st.set_page_config(
        page_title="WasteAI — Klasifikasi Sampah Cerdas",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inisialisasi session state (history & settings)
    init_session_state()

    # 3. Cek Autentikasi (Username/Password Guard)
    if "is_authenticated" not in st.session_state:
        from app.utils.cache import load_auth_state
        st.session_state["is_authenticated"] = load_auth_state()

    if not st.session_state["is_authenticated"]:
        import app.views.login as login_page
        login_page.render()
        return

    # 4. Injeksi CSS Global untuk memaksakan sudut siku & styling industrial
    st.markdown(
        """
        <style>
        /* Force sharp corners on everything */
        * {
            border-radius: 0px !important;
        }
        
        /* Adjust native Streamlit alerts for industrial look */
        div.stAlert {
            border-radius: 0px !important;
            border: 1px solid #E5E7EB !important;
            background-color: #F8FAFC !important;
        }
        
        /* Stylize primary buttons */
        div.stButton > button[kind="primary"] {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid #0F172A !important;
            font-weight: 700 !important;
            padding: 0.5rem 1.5rem !important;
            transition: none !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #1E293B !important;
            border-color: #1E293B !important;
            color: #FFFFFF !important;
        }
        
        /* Stylize secondary buttons */
        div.stButton > button[kind="secondary"] {
            background-color: transparent !important;
            color: #0F172A !important;
            border: 1px solid #0F172A !important;
            font-weight: 600 !important;
            transition: none !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
        }
        
        /* Custom tab styles to look like editorial dividers */
        div[data-baseweb="tab-list"] {
            border-bottom: 2px solid #E5E7EB !important;
            gap: 12px !important;
        }
        button[data-baseweb="tab"] {
            border: none !important;
            background: transparent !important;
            color: #64748B !important;
            padding: 0.5rem 1rem !important;
        }
        button[aria-selected="true"] {
            border-bottom: 2px solid #16A34A !important;
            color: #0F172A !important;
            font-weight: 700 !important;
        }
        
        /* Clean fonts styling */
        h1, h2, h3, h4, p, li, button {
            font-family: 'Inter', 'IBM Plex Sans', -apple-system, sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 4. Render navigasi dan halaman aktif
    route_page()

    # 5. Render footer global
    render_footer()


if __name__ == "__main__":
    main()
