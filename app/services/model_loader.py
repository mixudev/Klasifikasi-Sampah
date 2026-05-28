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
from huggingface_hub import login as hf_login

from app.config import HF_MODEL_ID, WASTE_MODEL_ID

logger = logging.getLogger(__name__)

# ─── Konstanta ────────────────────────────────────────────────────────────────

_FALLBACK_MODEL_ID = "Sintong/TrashNetResNet18"  # Model ringan ~45MB sebagai fallback

# Set timeout SEBELUM transformers digunakan (diperlukan di Streamlit Cloud)
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")  # Pastikan download diizinkan


# ─── HuggingFace Authentication ───────────────────────────────────────────────

def _setup_hf_authentication(hf_token: str = "") -> None:
    """
    Setup HuggingFace authentication.
    Jika token diberikan, gunakan untuk akses model private di HF.
    
    Args:
        hf_token: HuggingFace token untuk autentikasi (optional).
    """
    if hf_token and hf_token.strip():
        try:
            # Simpan token di environment variable untuk transformers library
            os.environ["HF_TOKEN"] = hf_token.strip()
            os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token.strip()
            # Login ke HuggingFace Hub
            hf_login(token=hf_token.strip(), add_to_git_credential=False)
            logger.info("[ModelLoader] ✅ HuggingFace authentication berhasil.")
        except Exception as e:
            logger.warning(f"[ModelLoader] ⚠️ HF authentication gagal: {e}")
    else:
        # Pastikan tidak ada token yang tersimpan
        os.environ.pop("HF_TOKEN", None)
        os.environ.pop("HUGGINGFACE_HUB_TOKEN", None)
        logger.info("[ModelLoader] HuggingFace authentication: mode publik.")


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

def _try_load_pipeline(model_id: str, hf_token: str = "") -> Tuple[Optional[pipeline], str]:
    """
    Satu upaya memuat model pipeline. Mengembalikan (pipeline, error_str).
    Jika berhasil: (pipeline_object, "").
    Jika gagal:    (None, "pesan error aktual").
    
    Args:
        model_id: ID model di HuggingFace Hub.
        hf_token: Token HuggingFace untuk akses model private (optional).
    """
    try:
        # Setup authentication jika ada token
        _setup_hf_authentication(hf_token)
        
        # Load pipeline dengan atau tanpa token
        clf = pipeline(
            task="image-classification",
            model=model_id,
            device=-1,           # CPU only — aman di semua environment
            top_k=None,          # Kembalikan seluruh skor kelas
            token=hf_token.strip() if hf_token else None,  # Pass token jika ada
        )
        logger.info(f"[ModelLoader] ✅ Berhasil: {model_id}")
        return clf, ""
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        logger.warning(f"[ModelLoader] ⚠️  Gagal '{model_id}': {err}")
        return None, err


@st.cache_resource(show_spinner="⏳ Mengunduh model AI dari Hugging Face Hub...")
def load_model_from_hub(model_id: str = WASTE_MODEL_ID, hf_token: str = "") -> Optional[pipeline]:
    """
    Muat model image-classification dari HuggingFace Hub.

    Alur eksekusi:
      1. Setup HuggingFace authentication (jika ada token)
      2. Uji konektivitas ke huggingface.co
      3. Coba model yang diminta (model_id)
      4. Fallback ke TrashNetResNet18 (lebih ringan)
      5. Fallback ke google/vit-base-patch16-224 (generik)
      6. Jika semua gagal → return None (predictor akan beralih ke Gemini)

    Args:
        model_id: ID model di HuggingFace Hub (format: 'username/repo-name').
        hf_token: Token HuggingFace untuk akses model private (optional).

    Returns:
        HuggingFace pipeline siap pakai, atau None jika semua upaya gagal.
    """
    logger.info(f"[ModelLoader] Memulai pemuatan: {model_id}")
    
    # ── Langkah 0: Setup HuggingFace authentication ────────────────────────
    _setup_hf_authentication(hf_token)

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
    clf, err = _try_load_pipeline(model_id, hf_token)
    if clf is not None:
        return clf
    last_error = err

    # ── Langkah 3: Fallback ke model ringan ──────────────────────────────────
    if model_id != _FALLBACK_MODEL_ID:
        logger.info(f"[ModelLoader] 🔄 Fallback ke model ringan: {_FALLBACK_MODEL_ID}")
        clf, err = _try_load_pipeline(_FALLBACK_MODEL_ID, hf_token)
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
        clf, err = _try_load_pipeline(HF_MODEL_ID, hf_token)
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
