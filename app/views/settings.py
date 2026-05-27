"""
settings.py — Halaman 10: Settings & Config.
Pengaturan ambang batas keyakinan, mode inferensi (lokal/cloud/gemini), token API, dan manajemen cache model.
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
import os
from app.utils.cache import get_setting, update_setting, reset_settings, clear_history
from app.services.model_loader import clear_model_cache
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

# Detect Streamlit Cloud
IS_STREAMLIT_CLOUD = os.path.exists(os.path.expanduser("~/.streamlit"))


def render() -> None:
    st.title("Pengaturan Sistem")
    st.caption("Konfigurasi parameter inferensi kecerdasan buatan, perilaku database lokal, dan memori cache.")

    # Show info jika di Streamlit Cloud
    if IS_STREAMLIT_CLOUD:
        st.info(
            "🚀 **Berjalan di Streamlit Cloud**\n\n"
            "**Mode Lokal (Offline)** adalah default untuk performa optimal. "
            "Anda juga bisa menggunakan **Google Gemini** sebagai alternatif jika diperlukan. "
            "(Mode Cloud HuggingFace tidak tersedia karena network restrictions)"
        )

    # ── MODE INFERENSI (Lokal, HF Cloud, Google Gemini) ───────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1.5rem; margin-bottom:1rem;">
            Mode Inferensi (Pemrosesan AI)
        </h3>
        """,
        unsafe_allow_html=True,
    )

    current_mode = get_setting("inference_mode")
    
    # Build mode options - di Streamlit Cloud: Local + Gemini only (no HF Cloud)
    if IS_STREAMLIT_CLOUD:
        mode_options = {
            "Lokal (Offline - Rekomendasi / Default)": "local",
            "Google Gemini AI (Multimodal - Alternatif Backup)": "gemini"
        }
    else:
        mode_options = {
            "Lokal (Offline - Mengunduh Model 343MB ke Komputer Anda)": "local",
            "Cloud (Hugging Face API - Tanpa Download Model, Ringan)": "cloud",
            "Google Gemini AI (Multimodal - Instan, Sangat Cerdas & Presisi Tinggi)": "gemini"
        }

    selected_mode_label = st.radio(
        "Pilih Lokasi Pemrosesan AI",
        list(mode_options.keys()),
        index=list(mode_options.values()).index(current_mode) if current_mode in mode_options.values() else 0
    )
    
    new_mode = mode_options[selected_mode_label]
    if new_mode != current_mode:
        update_setting("inference_mode", new_mode)
        st.success(f"Mode pemrosesan dialihkan ke: {new_mode.upper()}")
        st.rerun()

    # Tampilkan kolom Token / Key tergantung mode
    if new_mode == "cloud" and not IS_STREAMLIT_CLOUD:
        st.info(
            "Info: Mode Cloud berjalan secara instan tanpa mengunduh model. "
            "Sangat disarankan memasukkan Hugging Face Access Token Anda untuk menghindari pembatasan rate limit."
        )
        current_token = get_setting("hf_token")
        new_token = st.text_input(
            "Hugging Face User Access Token (Opsional)",
            value=current_token,
            type="password",
            help="Dapatkan token gratis Anda di: huggingface.co/settings/tokens"
        )
        if new_token != current_token:
            update_setting("hf_token", new_token.strip())
            st.success("Hugging Face API Token diperbarui.")

    elif new_mode == "gemini":
        st.info(
            "Info: Mode Google Gemini menggunakan model multimodal Gemini 1.5 Flash. "
            "Proses identifikasi dilakukan di server Google menggunakan kecerdasan visual yang sangat tinggi. "
            "Anda memerlukan API Key gratis dari Google AI Studio untuk menggunakan fitur ini."
        )
        current_gemini_key = get_setting("gemini_api_key")
        new_gemini_key = st.text_input(
            "Google Gemini API Key (Wajib / Gratis)",
            value=current_gemini_key,
            type="password",
            help="Dapatkan API Key gratis Anda di: aistudio.google.com"
        )
        if new_gemini_key != current_gemini_key:
            update_setting("gemini_api_key", new_gemini_key.strip())
            st.success("Google Gemini API Key diperbarui.")

    st.markdown("---")

    # ── PARAMETER AI ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1rem;">
            Parameter Analisis AI (Khusus Lokal / HF Cloud)
        </h3>
        """,
        unsafe_allow_html=True,
    )

    # 1. Confidence Threshold
    current_threshold = get_setting("confidence_threshold")
    new_threshold = st.slider(
        "Ambang Batas Keyakinan (Confidence Threshold)",
        min_value=0.1,
        max_value=1.0,
        value=float(current_threshold),
        step=0.05,
        help="Hasil pemindaian hanya dianggap TERVERIFIKASI jika tingkat keyakinan melebihi batas ini."
    )
    if new_threshold != current_threshold:
        update_setting("confidence_threshold", new_threshold)
        st.success(f"Ambang batas keyakinan diperbarui menjadi {new_threshold*100:.0f}%.")

    # 2. Model HuggingFace ID
    current_model = get_setting("model_id")
    
    st.markdown("**Konfigurasi Model Hugging Face (Lokal / Cloud):**")
    
    # Tombol pilihan cepat untuk kegunaan yang mudah
    st.caption("Pilihan Cepat Model Populer:")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        if st.button("Model Spesifik Sampah", type="secondary", use_container_width=True, help=f"Setel model ke: {WASTE_MODEL_ID}"):
            update_setting("model_id", WASTE_MODEL_ID)
            st.rerun()
    with col_m2:
        if st.button("Model Google ViT Generik", type="secondary", use_container_width=True, help=f"Setel model ke: {HF_MODEL_ID}"):
            update_setting("model_id", HF_MODEL_ID)
            st.rerun()
    with col_m3:
        if st.button("Model TrashNet ResNet18", type="secondary", use_container_width=True, help="Setel model ke: Sintong/TrashNetResNet18"):
            update_setting("model_id", "Sintong/TrashNetResNet18")
            st.rerun()

    new_model = st.text_input(
        "Hugging Face Model ID Aktif",
        value=current_model,
        help="Masukkan nama repositori model di Hugging Face Hub (misal: wayfarer130/garbage-classification-vit)"
    )
    
    if new_model.strip() != current_model:
        update_setting("model_id", new_model.strip())
        st.success(f"Model ID diperbarui menjadi: {new_model.strip()}")

    st.markdown("---")

    # ── SETTING SISTEM & RIWAYAT ──────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1rem;">
            Manajemen Riwayat & Perilaku Sesi
        </h3>
        """,
        unsafe_allow_html=True,
    )

    # 3. Auto Save
    current_auto_save = get_setting("auto_save_history")
    new_auto_save = st.checkbox(
        "Simpan Hasil Scan ke Riwayat Secara Otomatis",
        value=current_auto_save
    )
    if new_auto_save != current_auto_save:
        update_setting("auto_save_history", new_auto_save)
        st.success("Konfigurasi penyimpanan riwayat diperbarui.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TINDAKAN PEMBERSIHAN ──────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1rem;">
            Pemeliharaan Cache & Reset
        </h3>
        """,
        unsafe_allow_html=True,
    )

    col_btn_1, col_btn_2, col_btn_3 = st.columns(3)

    with col_btn_1:
        if st.button("RESET SETTING KE DEFAULT", type="secondary", use_container_width=True):
            reset_settings()
            st.success("Seluruh pengaturan telah dikembalikan ke default.")
            st.rerun()

    with col_btn_2:
        if st.button("HAPUS CACHE MODEL AI", type="secondary", use_container_width=True):
            clear_model_cache()
            st.success("Memori cache model AI lokal berhasil dikosongkan.")

    with col_btn_3:
        if st.button("KOSONGKAN RIWAYAT SCAN", type="secondary", use_container_width=True):
            clear_history()
            st.success("Seluruh catatan riwayat telah dikosongkan.")
            st.rerun()
