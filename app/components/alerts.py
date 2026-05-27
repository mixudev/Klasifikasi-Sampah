"""
alerts.py — Komponen pesan/alert standar aplikasi.
Bebas emoji sesuai dengan UI_ROLE.md.
"""

import streamlit as st


def alert_success(msg: str) -> None:
    st.success(msg)


def alert_warning(msg: str) -> None:
    st.warning(msg)


def alert_error(msg: str) -> None:
    st.error(msg)


def alert_info(msg: str) -> None:
    st.info(msg)


def alert_model_not_loaded() -> None:
    st.error(
        "**Model AI belum tersedia.**\n\n"
        "Pastikan koneksi internet aktif agar model dapat diunduh dari HuggingFace. "
        "Coba refresh halaman atau buka menu **Pengaturan → Reset Cache Model**."
    )


def alert_low_confidence(threshold_pct: float) -> None:
    st.warning(
        f"Confidence di bawah threshold ({threshold_pct:.0f}%). "
        "Hasil mungkin kurang akurat — pastikan gambar jelas dan cukup cahaya."
    )
