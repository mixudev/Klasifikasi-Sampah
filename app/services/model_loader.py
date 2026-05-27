"""
model_loader.py — Manajemen pemuatan model dari HuggingFace Hub.

Model diunduh dari repository publik HF menggunakan library `transformers`,
kemudian di-cache oleh Streamlit sehingga download hanya terjadi SEKALI per sesi.

Strategi fallback 3-tier:
  1. Model utama (dipilih pengguna di Pengaturan)
  2. Model khusus sampah ringan: Sintong/TrashNetResNet18 (~45MB)
  3. Model generik ViT: google/vit-base-patch16-224

Jika semua gagal, predictor akan otomatis beralih ke Gemini sebagai fallback.
"""

from __future__ import annotations

import logging
import os
import socket
from typing import Optional, Tuple

import streamlit as st
from transformers import pipeline

from app.config import HF_MODEL_ID, WASTE_MODEL_ID

logger = logging.getLogger(__name__)

# ─── Konstanta ────────────────────────────────────────────────────────────────

_FALLBACK_MODEL_ID = "Sintong/TrashNetResNet18"  # Model ringan ~45MB sebagai fallback

# Set timeout SEBELUM transformers digunakan (diperlukan di Streamlit Cloud)
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")  # Pastikan download diizinkan


# ─── Connectivity Check ───────────────────────────────────────────────────────

def _check_hf_connectivity(timeout: int = 8) -> Tuple[bool, str]:
    """
    Cek apakah HuggingFace dapat dijangkau via TCP sebelum mencoba download model.

    Returns:
        (is_reachable, error_message)
    """
    try:
        sock = socket.create_connection(("huggingface.co", 443), timeout=timeout)
        sock.close()
        return True, ""
    except socket.timeout:
        return False, "Koneksi ke huggingface.co timeout (>8 detik)"
    except socket.gaierror as e:
        return False, f"DNS gagal me-resolve 'huggingface.co': {e}"
    except OSError as e:
        return False, f"Koneksi gagal: {e}"


# ─── Model Loader ─────────────────────────────────────────────────────────────

def _try_load_pipeline(model_id: str) -> Tuple[Optional[pipeline], str]:
    """
    Satu upaya memuat model pipeline. Mengembalikan (pipeline, error_str).
    Jika berhasil: (pipeline_object, "").
    Jika gagal:    (None, "pesan error aktual").
    """
    try:
        clf = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,           # CPU only — aman di semua environment
            top_k=None,          # Kembalikan seluruh skor kelas
            local_files_only=False,
        )
        logger.info(f"[ModelLoader] ✅ Berhasil: {model_id}")
        return clf, ""
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        logger.warning(f"[ModelLoader] ⚠️  Gagal '{model_id}': {err}")
        return None, err


@st.cache_resource(show_spinner="⏳ Mengunduh model AI dari Hugging Face Hub...")
def load_model_from_hub(model_id: str = WASTE_MODEL_ID) -> Optional[pipeline]:
    """
    Muat model image-classification dari HuggingFace Hub.

    Alur eksekusi:
      1. Uji konektivitas ke huggingface.co
      2. Coba model yang diminta (model_id)
      3. Fallback ke TrashNetResNet18 (lebih ringan)
      4. Fallback ke google/vit-base-patch16-224 (generik)
      5. Jika semua gagal → return None (predictor akan beralih ke Gemini)

    Args:
        model_id: ID model di HuggingFace Hub (format: 'username/repo-name').

    Returns:
        HuggingFace pipeline siap pakai, atau None jika semua upaya gagal.
    """
    logger.info(f"[ModelLoader] Memulai pemuatan: {model_id}")

    # ── Langkah 1: Cek konektivitas ke HuggingFace ───────────────────────────
    is_reachable, conn_err = _check_hf_connectivity()
    if not is_reachable:
        logger.error(f"[ModelLoader] ❌ HuggingFace tidak terjangkau: {conn_err}")
        st.error(
            "❌ **HuggingFace Tidak Dapat Dijangkau**\n\n"
            f"**Detail error:** `{conn_err}`\n\n"
            "Kemungkinan penyebab di Streamlit Cloud:\n"
            "- Pembatasan jaringan pada deployment ini\n"
            "- Gangguan sementara pada server HuggingFace\n\n"
            "⚡ **Solusi cepat:** Beralih ke mode **Google Gemini** di halaman Pengaturan "
            "(tidak memerlukan download model dan tidak bergantung pada HuggingFace)."
        )
        return None

    logger.info("[ModelLoader] ✅ HuggingFace terjangkau. Memulai download...")
    last_error = ""

    # ── Langkah 2: Coba model yang diminta ───────────────────────────────────
    clf, err = _try_load_pipeline(model_id)
    if clf is not None:
        return clf
    last_error = err

    # ── Langkah 3: Fallback ke model ringan ──────────────────────────────────
    if model_id != _FALLBACK_MODEL_ID:
        logger.info(f"[ModelLoader] 🔄 Fallback ke model ringan: {_FALLBACK_MODEL_ID}")
        clf, err = _try_load_pipeline(_FALLBACK_MODEL_ID)
        if clf is not None:
            st.warning(
                f"⚠️ Model `{model_id}` gagal dimuat. "
                f"Menggunakan model alternatif: `{_FALLBACK_MODEL_ID}`"
            )
            return clf
        last_error = err

    # ── Langkah 4: Fallback ke model generik ─────────────────────────────────
    if model_id != HF_MODEL_ID and _FALLBACK_MODEL_ID != HF_MODEL_ID:
        logger.info(f"[ModelLoader] 🔄 Fallback terakhir: {HF_MODEL_ID}")
        clf, err = _try_load_pipeline(HF_MODEL_ID)
        if clf is not None:
            st.warning(
                f"⚠️ Model utama tidak tersedia. "
                f"Menggunakan model generik: `{HF_MODEL_ID}`"
            )
            return clf
        last_error = err

    # ── Semua upaya gagal ─────────────────────────────────────────────────────
    logger.error(f"[ModelLoader] ❌ Semua upaya gagal. Error terakhir: {last_error}")
    st.error(
        "❌ **Gagal Memuat Model dari HuggingFace Hub**\n\n"
        f"**Error teknis:** `{last_error}`\n\n"
        "**Yang sudah dicoba:**\n"
        f"- `{model_id}`\n"
        f"- `{_FALLBACK_MODEL_ID}` (fallback ringan)\n"
        f"- `{HF_MODEL_ID}` (fallback generik)\n\n"
        "⚡ Aplikasi akan otomatis beralih ke **Google Gemini** untuk prediksi ini."
    )
    return None


# ─── Cache Management ─────────────────────────────────────────────────────────

def clear_model_cache() -> None:
    """Bersihkan cache resource model agar dapat dimuat ulang saat diperlukan."""
    load_model_from_hub.clear()
    logger.info("[ModelLoader] Cache model berhasil dibersihkan.")
