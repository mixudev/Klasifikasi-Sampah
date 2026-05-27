"""
model_loader.py — Memuat model dari HuggingFace dengan cache Streamlit.
Model TIDAK disimpan di repo; diunduh otomatis saat pertama kali dijalankan.
"""

from __future__ import annotations
from typing import Optional
import os

import streamlit as st
from transformers import pipeline
import logging
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

logger = logging.getLogger(__name__)

# Detect if running on Streamlit Cloud
IS_STREAMLIT_CLOUD = "STREAMLIT" in os.environ and "streamlit.io" in os.environ.get("STREAMLIT_SERVER_HEADLESS", "")

# Untuk development lokal: set ke True jika sudah jalankan download_model.py
# Untuk Streamlit Cloud: otomatis False, akan download on first run
LOCAL_FILES_ONLY = not IS_STREAMLIT_CLOUD


@st.cache_resource(show_spinner="Memuat model AI, mohon tunggu...")
def load_model(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Load image-classification pipeline dari HuggingFace.
    Di-cache agar tidak reload setiap interaksi.

    Args:
        model_id: ID model di HuggingFace Hub.

    Returns:
        HuggingFace pipeline object, atau None jika gagal.
    """
    try:
        logger.info(f"Loading model: {model_id}")
        logger.info(f"Local files only: {LOCAL_FILES_ONLY}")
        
        classifier = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,             # CPU-only; ganti ke 0 atau "cuda" jika ada GPU
            top_k=None,            # kembalikan semua kelas + skor
            local_files_only=LOCAL_FILES_ONLY, # Auto-detect based on environment
        )
        logger.info("Model loaded successfully.")
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"Gagal memuat model '{model_id}': {exc}")
        
        # Jika network error dan local mode, beri instruksi download offline
        if ("HTTPSConnectionPool" in error_msg or "NameResolutionError" in error_msg) and LOCAL_FILES_ONLY:
            logger.error("🌐 ERROR: Tidak ada koneksi ke HuggingFace API")
            logger.error("💡 SOLUSI: Download model offline dulu dengan menjalankan:")
            logger.error("   python download_model.py")
            st.error(
                "❌ **Model Tidak Ditemukan di Lokal**\n\n"
                "Model belum di-cache local. Silakan jalankan terlebih dahulu:\n"
                "```bash\npython download_model.py\n```\n"
                "Atau jika di Streamlit Cloud, tunggu sampai model selesai di-download (pertama kali saja)."
            )
        
        # Fallback ke model generik jika model sampah tidak tersedia
        if model_id != HF_MODEL_ID:
            logger.warning(f"Fallback ke model generik: {HF_MODEL_ID}")
            return load_model(HF_MODEL_ID)
        return None


def clear_model_cache() -> None:
    """Hapus cache model (dipakai dari halaman Settings)."""
    load_model.clear()
    logger.info("Model cache cleared.")
