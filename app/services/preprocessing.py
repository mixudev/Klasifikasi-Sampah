"""
preprocessing.py — Pra-pemrosesan gambar sebelum dikirim ke model.
"""

from PIL import Image, ImageOps, ImageEnhance
from app.config import IMAGE_SIZE
import logging

logger = logging.getLogger(__name__)


def preprocess_image(image: Image.Image, target_size: tuple = IMAGE_SIZE) -> Image.Image:
    """
    Standarisasi gambar: convert ke RGB, resize, dan normalisasi orientasi (EXIF).

    Args:
        image: PIL Image dari upload user.
        target_size: Ukuran target (width, height).

    Returns:
        PIL Image siap masuk model.
    """
    try:
        # Perbaiki orientasi dari metadata EXIF (foto kamera)
        image = ImageOps.exif_transpose(image)

        # Pastikan format RGB (bukan RGBA / grayscale)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize ke ukuran model
        image = image.resize(target_size, Image.LANCZOS)

        return image

    except Exception as exc:
        logger.error(f"Preprocessing gagal: {exc}")
        raise ValueError(f"Gagal memproses gambar: {exc}") from exc


def enhance_image(image: Image.Image, brightness: float = 1.1, contrast: float = 1.1) -> Image.Image:
    """
    Opsional: sedikit tingkatkan brightness & contrast agar model lebih mudah mengenali.

    Args:
        image: PIL Image.
        brightness: Faktor brightness (1.0 = asli).
        contrast: Faktor contrast (1.0 = asli).

    Returns:
        PIL Image yang sudah di-enhance.
    """
    try:
        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        return image
    except Exception as exc:
        logger.warning(f"Enhancement gagal, memakai gambar asli: {exc}")
        return image


def validate_image(image: Image.Image, min_size: int = 32) -> tuple[bool, str]:
    """
    Validasi apakah gambar layak diproses.

    Returns:
        (is_valid: bool, pesan: str)
    """
    w, h = image.size
    if w < min_size or h < min_size:
        return False, f"Gambar terlalu kecil ({w}x{h}px). Minimum {min_size}x{min_size}px."
    if image.mode not in ("RGB", "RGBA", "L", "P"):
        return False, f"Format warna '{image.mode}' tidak didukung."
    return True, "OK"
