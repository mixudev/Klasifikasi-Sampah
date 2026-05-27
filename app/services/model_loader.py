"""
model_loader.py — Memuat model dari HuggingFace dengan cache Streamlit.
Mendukung dua mode:
  1. load_model()          — Mode Lokal/Offline (local_files_only=True, model harus sudah ada di cache)
  2. load_model_from_hub() — Mode HF Hub (download otomatis dari HuggingFace, cached setelah unduhan pertama)
"""

from __future__ import annotations
from typing import Optional
import os
import time

import streamlit as st
from transformers import pipeline
import logging
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

logger = logging.getLogger(__name__)


def get_cache_dir():
    """Get HuggingFace cache directory."""
    return os.path.expanduser("~/.cache/huggingface")

@st.cache_resource(show_spinner="📥 Memuat model lokal (mode offline)...")
def load_model(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Mode Lokal/Offline: Load model dari cache lokal saja (local_files_only=True).
    Model harus sudah ada di cache HuggingFace (~/.cache/huggingface).
    Jalankan `python download_model.py` terlebih dahulu untuk men-download model.
    
    Args:
        model_id: ID model di HuggingFace Hub.
    Returns:
        HuggingFace pipeline object, atau None jika model belum ada di cache lokal.
    """
    try:
        logger.info(f"🚀 [Mode Lokal] Loading model dari cache: {model_id}")
        logger.info(f"   Cache dir: {get_cache_dir()}")
        
        classifier = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,  # CPU-only
            top_k=None,
            local_files_only=True,  # HANYA dari cache lokal, tidak download
        )
        logger.info("✅ Model lokal berhasil dimuat!")
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Gagal memuat model lokal '{model_id}': {exc}")
        st.error(
            "❌ **Model Lokal Tidak Ditemukan**\n\n"
            "Model belum di-download ke komputer Anda. Pilihan solusi:\n"
            "- Jalankan `python download_model.py` untuk download offline\n"
            "- Atau ganti ke **Mode HF Hub** di Pengaturan (download otomatis saat pertama kali)\n"
            "- Atau gunakan **Google Gemini** (tidak perlu download model)\n\n"
            f"Error: `{error_msg[:150]}`"
        )
        return None


@st.cache_resource(show_spinner="📥 Mengunduh model dari Hugging Face Hub (hanya sekali)...")
def load_model_from_hub(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Mode HF Hub: Download model langsung dari HuggingFace Hub menggunakan `transformers`.
    Model akan di-cache secara otomatis setelah download pertama.
    Mendukung model publik dari username/repo_name tanpa memerlukan API serverless.
    
    Args:
        model_id: ID model di HuggingFace Hub (contoh: 'wayfarer130/garbage-classification-vit').
    Returns:
        HuggingFace pipeline object, atau None jika gagal.
    """
    try:
        logger.info(f"🚀 [Mode HF Hub] Mengunduh/loading model: {model_id}")
        logger.info(f"   Cache dir: {get_cache_dir()}")
        
        # Set timeout yang lebih panjang untuk download model
        os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"  # 10 menit
        
        classifier = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,   # CPU-only
            top_k=None,
            local_files_only=False,  # Izinkan download dari Hub
        )
        logger.info("✅ Model dari HF Hub berhasil dimuat!")
        return classifier

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Gagal mengunduh model dari HF Hub '{model_id}': {exc}")
        
        # Coba fallback ke model generik jika model spesifik gagal
        if model_id != HF_MODEL_ID:
            logger.warning(f"⚠️ Fallback ke model generik: {HF_MODEL_ID}")
            st.warning(
                f"⚠️ Model **{model_id}** tidak dapat dimuat.\n\n"
                f"Mencoba model alternatif: `{HF_MODEL_ID}`..."
            )
            return load_model_from_hub(HF_MODEL_ID)
        
        st.error(
            "❌ **Gagal Mengunduh Model dari Hugging Face Hub**\n\n"
            "**Kemungkinan Penyebab:**\n"
            "- Tidak ada koneksi internet\n"
            "- Model ID tidak valid atau repositori privat\n"
            "- Server HuggingFace sedang tidak dapat diakses\n\n"
            "**Solusi:**\n"
            "✅ Periksa koneksi internet Anda\n"
            "✅ Verifikasi model ID di: `huggingface.co/<username>/<repo>`\n"
            "✅ Atau gunakan **Google Gemini** (tidak perlu internet untuk model)\n\n"
            f"**Detail Error:** `{error_msg[:200]}`"
        )
        return None


def clear_model_cache() -> None:
    """Hapus cache model (dipakai dari halaman Settings)."""
    load_model.clear()
    load_model_from_hub.clear()
    logger.info("✅ Model cache (lokal & HF Hub) berhasil dikosongkan.")
