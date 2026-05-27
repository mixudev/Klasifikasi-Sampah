"""
login.py — Halaman Login Utama WasteAI.
Desain ultra-premium, industrial, tanpa emoji, dan sudut siku penuh.
"""

import streamlit as st


def render() -> None:
    # Injeksi CSS khusus untuk halaman login
    st.markdown(
        """
        <style>
        /* Sembunyikan sidebar sepenuhnya */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Pusatkan kontainer form secara vertikal & horizontal */
        div.block-container {
            padding-top: 6rem !important;
            max-width: 450px !important;
            margin: 0 auto !important;
        }
        
        /* Kustomisasi input fields agar tajam & bergaya industrial */
        input {
            border: 1px solid #E2E8F0 !important;
            border-radius: 0px !important;
            padding: 0.6rem 0.8rem !important;
            font-size: 0.95rem !important;
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        input:focus {
            border-color: #16A34A !important;
            background-color: #FFFFFF !important;
            box-shadow: none !important;
        }
        
        /* Kustomisasi Form Container */
        div[data-testid="stForm"] {
            border: 1px solid #E2E8F0 !important;
            border-top: 4px solid #16A34A !important;
            border-radius: 0px !important;
            padding: 2.2rem !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05) !important;
        }
        
        /* Label kolom input */
        label {
            font-weight: 700 !important;
            color: #475569 !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.8px !important;
            text-transform: uppercase !important;
        }
        
        /* Tombol login */
        button[kind="primaryFormSubmit"] {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid #0F172A !important;
            border-radius: 0px !important;
            width: 100% !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            padding: 0.6rem !important;
            text-transform: uppercase !important;
            margin-top: 0.8rem !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
        }
        button[kind="primaryFormSubmit"]:hover {
            background-color: #16A34A !important;
            border-color: #16A34A !important;
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Header Logo & Subtitle
    # Padlock SVG
    padlock_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"><rect x="3" y="11" width="18" height="11" rx="0" ry="0"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>'
    
    header_html = f'<div style="text-align: center; margin-bottom: 2rem;"><div style="margin-bottom: 0.8rem; display: inline-block;">{padlock_svg}</div><h1 style="font-size: 1.8rem; font-weight: 900; color: #0F172A; margin: 0; letter-spacing: -0.5px; text-transform: uppercase;">WasteAI Portal</h1><p style="color: #64748B; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.3rem;">Sistem Klasifikasi Sampah Cerdas</p></div>'
    
    st.markdown(header_html, unsafe_allow_html=True)

    # Form Login
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        submitted = st.form_submit_button("Masuk Ke Sistem")
        
        if submitted:
            if username.strip() == "admin" and password == "admin":
                st.session_state["is_authenticated"] = True
                from app.utils.cache import save_auth_state
                save_auth_state(True)
                st.success("Autentikasi berhasil! Memuat dasbor...")
                st.rerun()
            else:
                st.error("Username atau password salah. Silakan coba lagi.")
