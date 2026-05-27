"""
model_loader.py — Memuat model dari HuggingFace dengan cache Streamlit.
Model TIDAK disimpan di repo; diunduh otomatis saat pertama kali dijalankan.
"""

from __future__ import annotations
from typing import Optional
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import streamlit as st
from transformers import pipeline
import logging
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

logger = logging.getLogger(__name__)

# Detect if running on Streamlit Cloud (more reliable detection)
def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Cloud."""
    # Check multiple indicators
    return (
        "STREAMLIT_SERVER_HEADLESS" in os.environ or
        os.path.exists(os.path.expanduser("~/.streamlit")) or
        "streamlit" in os.environ.get("HOSTNAME", "").lower()
    )

IS_STREAMLIT_CLOUD = is_streamlit_cloud()

# Untuk development lokal: set ke True jika sudah jalankan download_model.py
# Untuk Streamlit Cloud: otomatis False, akan coba download with retry
LOCAL_FILES_ONLY = not IS_STREAMLIT_CLOUD


def setup_robust_session():
    """Setup requests session dengan retry strategy untuk cloud environment."""
    from requests import Session
    session = Session()
    
    # Retry strategy: exponential backoff
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


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
        logger.info(f"Streamlit Cloud detected: {IS_STREAMLIT_CLOUD}")
        
        classifier = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,             # CPU-only; ganti ke 0 atau "cuda" jika ada GPU
            top_k=None,            # kembalikan semua kelas + skor
            local_files_only=LOCAL_FILES_ONLY, # Auto-detect based on environment
        )
        logger.info("✅ Model loaded successfully.")
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Gagal memuat model '{model_id}': {exc}")
        
        # Jika error network di cloud, retry dengan delay
        if IS_STREAMLIT_CLOUD and ("HTTPSConnectionPool" in error_msg or "NameResolutionError" in error_msg):
            logger.warning("🔄 Retry dengan exponential backoff...")
            time.sleep(2)
            
            try:
                # Retry sekali dengan setup session yang robust
                classifier = pipeline(
                    task="image-classification",
                    model=model_id,
                    device=-1,
                    top_k=None,
                    local_files_only=False,  # Force download retry
                )
                logger.info("✅ Model loaded on retry!")
                return classifier
            except Exception as retry_exc:
                logger.error(f"❌ Retry juga gagal: {retry_exc}")
        
        # Jika ini bukan model default, fallback ke model generic yang lebih ringan
        if model_id != HF_MODEL_ID:
            logger.warning(f"⚠️ Fallback ke model generik: {HF_MODEL_ID}")
            st.warning(f"⚠️ Model '{model_id}' tidak tersedia. Menggunakan model generic untuk prediksi.")
            return load_model(HF_MODEL_ID)
        
        # Jika masih gagal, show error message
        if IS_STREAMLIT_CLOUD:
            st.error(
                "❌ **Model Loading Failed di Cloud**\n\n"
                "Kemungkinan penyebab:\n"
                "1. Network sedang overloaded\n"
                "2. HuggingFace API sedang down\n"
                "3. Request timeout\n\n"
                "**Solusi:**\n"
                "- Tunggu beberapa menit dan refresh halaman\n"
                "- Atau deploy dengan `requirements.txt` yang include pre-downloaded model"
            )
        else:
            st.error(
                "❌ **Model Tidak Ditemukan**\n\n"
                "Jalankan: `python download_model.py`"
            )
        
        return None


def clear_model_cache() -> None:
    """Hapus cache model (dipakai dari halaman Settings)."""
    load_model.clear()
    logger.info("Model cache cleared.")
