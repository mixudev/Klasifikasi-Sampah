"""
model_loader.py — Manajemen pemuatan model dari HuggingFace Hub.

Model diunduh otomatis dari repository publik HuggingFace menggunakan library
`transformers`, kemudian di-cache oleh Streamlit (@st.cache_resource) sehingga
download hanya terjadi SEKALI per sesi — tidak berulang saat pengguna berpindah halaman.

Strategi fallback 3-tier:
  1. Model utama (dipilih pengguna di Pengaturan)
  2. Model khusus sampah ringan: Sintong/TrashNetResNet18 (~45MB)
  3. Model generik ViT: google/vit-base-patch16-224 (~350MB)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import streamlit as st
from transformers import pipeline

from app.config import HF_MODEL_ID, WASTE_MODEL_ID

logger = logging.getLogger(__name__)

# ─── Konstanta ────────────────────────────────────────────────────────────────

# Model fallback yang lebih ringan (~45MB) jika model utama gagal
_FALLBACK_MODEL_ID = "Sintong/TrashNetResNet18"


# ─── Helper ───────────────────────────────────────────────────────────────────

def get_hf_cache_dir() -> str:
    """Kembalikan direktori cache HuggingFace yang aktif."""
    return os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))


def _try_load(model_id: str) -> Optional[pipeline]:
    """
    Upaya tunggal memuat model tanpa fallback.
    Mengembalikan pipeline jika berhasil, None jika gagal.
    """
    try:
        clf = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,      # CPU only — aman di semua environment termasuk Streamlit Cloud
            top_k=None,     # Kembalikan seluruh skor kelas
            local_files_only=False,  # Izinkan download dari Hub jika belum ada di cache
        )
        logger.info(f"[ModelLoader] ✅ Berhasil memuat: {model_id}")
        return clf
    except Exception as exc:
        logger.warning(f"[ModelLoader] ⚠️  Gagal memuat '{model_id}': {type(exc).__name__}: {exc}")
        return None


# ─── Fungsi Utama ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="⏳ Mengunduh model AI dari Hugging Face Hub (hanya pertama kali)...")
def load_model_from_hub(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Muat model image-classification dari HuggingFace Hub.

    Model diunduh secara otomatis dari repository publik HF dan di-cache
    menggunakan @st.cache_resource. Download hanya terjadi sekali per sesi —
    saat app restart, download ulang diperlukan jika cache hilang.

    Strategi fallback otomatis:
      1. Coba model yang diminta (model_id)
      2. Coba model khusus sampah ringan (TrashNetResNet18)
      3. Coba model generik ViT Google

    Args:
        model_id: ID model di HuggingFace Hub (format: 'username/repo-name').
                  Gunakan model publik agar dapat diakses tanpa token.

    Returns:
        HuggingFace pipeline siap pakai untuk image-classification,
        atau None jika semua upaya gagal (kemungkinan tidak ada koneksi internet).
    """
    # Perpanjang timeout untuk download model besar di lingkungan cloud
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")  # 10 menit

    logger.info(f"[ModelLoader] Memulai pemuatan model: {model_id}")
    logger.info(f"[ModelLoader] Cache directory: {get_hf_cache_dir()}")

    # ── Upaya 1: Model yang diminta ──────────────────────────────────────────
    clf = _try_load(model_id)
    if clf is not None:
        return clf

    # ── Upaya 2: Model khusus sampah (lebih ringan) ──────────────────────────
    if model_id != _FALLBACK_MODEL_ID:
        logger.info(f"[ModelLoader] 🔄 Mencoba fallback ringan: {_FALLBACK_MODEL_ID}")
        clf = _try_load(_FALLBACK_MODEL_ID)
        if clf is not None:
            st.warning(
                f"⚠️ Model **{model_id}** tidak dapat dimuat. "
                f"Menggunakan model alternatif: `{_FALLBACK_MODEL_ID}`"
            )
            return clf

    # ── Upaya 3: Model generik ViT Google ───────────────────────────────────
    if model_id != HF_MODEL_ID:
        logger.info(f"[ModelLoader] 🔄 Mencoba model generik: {HF_MODEL_ID}")
        clf = _try_load(HF_MODEL_ID)
        if clf is not None:
            st.warning(
                f"⚠️ Model utama tidak tersedia. "
                f"Menggunakan model generik: `{HF_MODEL_ID}`"
            )
            return clf

    # ── Semua upaya gagal ────────────────────────────────────────────────────
    logger.error("[ModelLoader] ❌ Semua upaya pemuatan model gagal.")
    st.error(
        "❌ **Tidak Dapat Memuat Model dari Hugging Face Hub**\n\n"
        "**Kemungkinan penyebab:**\n"
        "- Tidak ada koneksi internet\n"
        "- Model ID tidak valid atau repositori bersifat privat\n"
        "- Server HuggingFace sedang dalam gangguan\n\n"
        "**Solusi:**\n"
        "✅ Periksa koneksi internet Anda\n"
        "✅ Verifikasi Model ID di `huggingface.co/<username>/<repo>`\n"
        "✅ Atau beralih ke mode **Google Gemini** di halaman Pengaturan"
    )
    return None


def clear_model_cache() -> None:
    """Bersihkan cache resource model agar dapat dimuat ulang saat diperlukan."""
    load_model_from_hub.clear()
    logger.info("[ModelLoader] Cache model berhasil dibersihkan.")
