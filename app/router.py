"""
router.py — Pengendali rute navigasi aplikasi WasteAI.
Memetakan halaman yang dipilih dari sidebar ke modul render yang sesuai.
"""

import streamlit as st
from app.components.navbar import render_navbar

# Import modul halaman secara dinamis/langsung
import app.views.landing as landing_page
import app.views.scan as scan_page
import app.views.upload as upload_page
import app.views.history as history_page
import app.views.analytics as analytics_page
import app.views.data_manager as data_manager_page
import app.views.dataset as dataset_page
import app.views.tutorial as tutorial_page
import app.views.about as about_page
import app.views.settings as settings_page


def route_page() -> None:
    """Membaca navigasi aktif dari sidebar dan merender modul halaman yang sesuai."""
    # Render navbar sidebar dan dapatkan ID halaman aktif
    active_page_id = render_navbar()

    # Routing ke halaman yang sesuai
    if active_page_id == "landing":
        landing_page.render()
    elif active_page_id == "scan":
        scan_page.render()
    elif active_page_id == "upload":
        upload_page.render()
    elif active_page_id == "history":
        history_page.render()
    elif active_page_id == "analytics":
        analytics_page.render()
    elif active_page_id == "data_manager":
        data_manager_page.render()
    elif active_page_id == "dataset":
        dataset_page.render()
    elif active_page_id == "tutorial":
        tutorial_page.render()
    elif active_page_id == "about":
        about_page.render()
    elif active_page_id == "settings":
        settings_page.render()
    else:
        st.error(f"Halaman '{active_page_id}' tidak ditemukan.")
