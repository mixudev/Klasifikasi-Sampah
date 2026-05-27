"""
model_loader.py — Memuat model dari HuggingFace dengan cache Streamlit.
Model TIDAK disimpan di repo; diunduh otomatis saat pertama kali dijalankan.
Optimized untuk Streamlit Cloud dengan retry logic & fallback mechanisms.
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

# Detect if running on Streamlit Cloud
def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Cloud."""
    return (
        "STREAMLIT_SERVER_HEADLESS" in os.environ or
        os.path.exists(os.path.expanduser("~/.streamlit")) or
        "streamlit" in os.environ.get("HOSTNAME", "").lower()
    )

IS_STREAMLIT_CLOUD = is_streamlit_cloud()
LOCAL_FILES_ONLY = not IS_STREAMLIT_CLOUD

# Progress tracking untuk long-running loads
_model_loading_progress = {}

def get_cache_dir():
    """Get HuggingFace cache directory."""
    return os.path.expanduser("~/.cache/huggingface")

@st.cache_resource(show_spinner="📥 Downloading model AI (first time only)...")
def load_model(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Load image-classification pipeline dari HuggingFace dengan retry logic.
    
    Args:
        model_id: ID model di HuggingFace Hub.
    Returns:
        HuggingFace pipeline object, atau None jika gagal.
    """
    try:
        logger.info(f"🚀 Loading model: {model_id}")
        logger.info(f"   Environment: {'Streamlit Cloud' if IS_STREAMLIT_CLOUD else 'Local'}")
        logger.info(f"   Local files only: {LOCAL_FILES_ONLY}")
        logger.info(f"   Cache dir: {get_cache_dir()}")
        
        # Set longer timeout untuk Streamlit Cloud
        os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"  # 10 menit timeout
        
        classifier = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,  # CPU-only
            top_k=None,
            local_files_only=LOCAL_FILES_ONLY,
        )
        logger.info("✅ Model loaded successfully!")
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Failed to load model '{model_id}': {exc}")
        
        # Jika error karena network/timeout di cloud, retry dengan delay
        if IS_STREAMLIT_CLOUD and ("HTTPSConnectionPool" in error_msg or 
                                    "NameResolutionError" in error_msg or 
                                    "timeout" in error_msg.lower()):
            logger.warning("⏳ Network error on Streamlit Cloud - retrying in 5 seconds...")
            time.sleep(5)
            
            try:
                logger.info(f"🔄 RETRY: Loading model {model_id}")
                classifier = pipeline(
                    task="image-classification",
                    model=model_id,
                    device=-1,
                    top_k=None,
                    local_files_only=False,  # Force download on retry
                )
                logger.info("✅ Model loaded on retry!")
                return classifier
            except Exception as retry_exc:
                logger.error(f"❌ Retry also failed: {retry_exc}")
        
        # Fallback ke model generic jika specific model gagal
        if model_id != HF_MODEL_ID:
            logger.warning(f"⚠️ Fallback ke model generic: {HF_MODEL_ID}")
            st.warning(
                f"⚠️ Model **{model_id}** tidak tersedia.\n\n"
                "Menggunakan model generic untuk prediksi..."
            )
            return load_model(HF_MODEL_ID)
        
        # Final error message untuk user
        if IS_STREAMLIT_CLOUD:
            st.error(
                "❌ **Model Loading Failed di Cloud**\n\n"
                "**Penyebab Umum:**\n"
                "1. First deployment - model sedang di-download (~10 menit)\n"
                "2. Network timeout - HuggingFace API sedang slow\n"
                "3. Memory insufficient - model terlalu besar\n\n"
                "**Solusi:**\n"
                "✅ Tunggu 10-15 menit untuk first run\n"
                "✅ Refresh halaman & coba lagi\n"
                "✅ Atau gunakan **Google Gemini** di Pengaturan\n\n"
                f"**Debug Info:** `{error_msg[:100]}...`"
            )
        else:
            st.error(
                "❌ **Model Tidak Ditemukan**\n\n"
                "Jalankan: `python download_model.py` untuk download offline.\n\n"
                f"Error: {error_msg}"
            )
        
        return None
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Gagal memuat model '{model_id}': {exc}")

def clear_model_cache() -> None:
    """Hapus cache model (dipakai dari halaman Settings)."""
    load_model.clear()
    logger.info("✅ Model cache cleared.")
