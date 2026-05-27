"""
image_utils.py — Fungsi utilitas gambar yang dipakai lintas modul.
"""

from __future__ import annotations
from typing import Optional

from PIL import Image
import io
import base64
import streamlit as st


def pil_to_bytes(image: Image.Image, fmt: str = "JPEG") -> bytes:
    """Konversi PIL Image ke bytes."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def bytes_to_pil(data: bytes) -> Image.Image:
    """Konversi bytes ke PIL Image."""
    return Image.open(io.BytesIO(data))


def pil_to_base64(image: Image.Image, fmt: str = "JPEG") -> str:
    """Konversi PIL Image ke base64 string (untuk HTML embedding)."""
    raw = pil_to_bytes(image, fmt)
    return base64.b64encode(raw).decode("utf-8")


def load_uploaded_file(uploaded_file) -> Optional[Image.Image]:
    """
    Baca file yang di-upload via st.file_uploader dan kembalikan PIL Image.

    Returns:
        PIL Image atau None jika gagal.
    """
    if uploaded_file is None:
        return None
    try:
        return Image.open(uploaded_file)
    except Exception as exc:
        st.error(f"Gagal membuka gambar: {exc}")
        return None


def display_image_preview(image: Image.Image, caption: str = "Preview", max_width: int = 400) -> None:
    """Tampilkan preview gambar dengan lebar maksimum."""
    st.image(image, caption=caption, width=max_width)
