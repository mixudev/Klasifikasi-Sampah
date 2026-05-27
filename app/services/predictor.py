"""
predictor.py — Engine inferensi WasteAI.

Mendukung dua mode inferensi yang dapat dipilih pengguna:

  • "hugging" — Model dari HuggingFace Hub (diunduh via transformers, CPU inference)
                Tidak memerlukan API key. Model di-cache setelah download pertama.

  • "gemini"  — Google Gemini Multimodal AI (via REST API)
                Memerlukan Gemini API Key. Tidak memerlukan download model.

Setiap prediksi dikembalikan sebagai PredictionResult yang terstruktur,
berisi label, confidence, tips penanganan, dan metadata sumber prediksi.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import requests
from PIL import Image, ImageEnhance

from app.config import (
    CLASS_COLORS,
    DEFAULT_CONFIDENCE_THRESHOLD,
    GEMINI_API_KEY,
    HANDLING_TIPS,
    WASTE_CLASSES,
    WASTE_MODEL_ID,
)
from app.services.model_loader import load_model_from_hub
from app.services.preprocessing import preprocess_image, validate_image
from app.utils.cache import get_setting
from app.utils.image_utils import pil_to_base64

logger = logging.getLogger(__name__)


# ─── Data Model ──────────────────────────────────────────────────────────────

@dataclass
class PredictionResult:
    """Hasil prediksi klasifikasi sampah untuk satu gambar."""

    label: str                          # Nama kelas (misal: "Plastik", "Kaca")
    confidence: float                   # Tingkat keyakinan 0.0–1.0
    color: str                          # Warna hex untuk representasi visual kelas
    tip: str                            # Saran penanganan sampah untuk kelas ini
    all_scores: list[dict]              # Semua skor kelas: [{"label": ..., "score": ...}]
    is_confident: bool                  # True jika confidence >= threshold
    source: str                         # Sumber: "H" (HuggingFace) | "G" (Gemini)
    error: Optional[str] = None         # Pesan error jika prediksi gagal


# ─── Label Mapping ────────────────────────────────────────────────────────────

# Pemetaan label bahasa Inggris dari model HF → kelas WASTE_CLASSES Indonesia
_LABEL_MAP: dict[str, str] = {
    # Organik
    "organic":    "Organik",
    "food":       "Organik",
    "vegetable":  "Organik",
    "trash":      "Organik",
    "compost":    "Organik",
    # Plastik
    "plastic":    "Plastik",
    "bottle":     "Plastik",
    "container":  "Plastik",
    # Kertas
    "paper":      "Kertas",
    "cardboard":  "Kertas",
    "magazine":   "Kertas",
    "newspaper":  "Kertas",
    # Kaca
    "glass":      "Kaca",
    # Logam
    "metal":      "Logam",
    "can":        "Logam",
    "aluminum":   "Logam",
    "steel":      "Logam",
    # B3
    "battery":    "B3 (Berbahaya)",
    "electronic": "B3 (Berbahaya)",
    "hazardous":  "B3 (Berbahaya)",
    "chemical":   "B3 (Berbahaya)",
}


def _map_label(raw_label: str) -> str:
    """
    Konversi label mentah dari model ke nama kelas WASTE_CLASSES.

    Prioritas resolusi:
      1. Exact match ke WASTE_CLASSES (sudah bahasa Indonesia)
      2. Keyword mapping (bahasa Inggris → Indonesia)
      3. Partial match ke WASTE_CLASSES
      4. Kembalikan label asli jika tidak ada yang cocok
    """
    label_lower = raw_label.lower().strip()

    # 1. Exact match ke WASTE_CLASSES
    for cls in WASTE_CLASSES:
        if cls.lower() == label_lower:
            return cls

    # 2. Keyword mapping
    for keyword, mapped in _LABEL_MAP.items():
        if keyword in label_lower:
            return mapped

    # 3. Partial match
    for cls in WASTE_CLASSES:
        if cls.lower() in label_lower or label_lower in cls.lower():
            return cls

    return raw_label  # kembalikan apa adanya


# ─── Utilitas Internal ────────────────────────────────────────────────────────

def _error_result(source: str, message: str) -> PredictionResult:
    """Buat PredictionResult standar untuk kondisi error."""
    return PredictionResult(
        label="Error",
        confidence=0.0,
        color="#DC2626",
        tip="",
        all_scores=[],
        is_confident=False,
        source=source,
        error=message,
    )


def _auto_enhance(image: Image.Image) -> Image.Image:
    """
    Tingkatkan kecerahan dan kontras secara otomatis jika gambar terlalu gelap.
    Threshold brightness < 85 (skala 0–255) dianggap kondisi cahaya rendah.
    """
    gray = image.convert("L")
    avg_brightness = float(np.mean(np.array(gray)))
    if avg_brightness < 85:
        logger.info(
            f"[Predict] Cahaya rendah terdeteksi (brightness={avg_brightness:.1f}). "
            "Menerapkan auto-enhance."
        )
        image = ImageEnhance.Brightness(image).enhance(1.6)
        image = ImageEnhance.Contrast(image).enhance(1.3)
    return image


# ─── Mode: HuggingFace Hub ───────────────────────────────────────────────────

def _predict_hugging(
    image: Image.Image,
    model_id: str,
    threshold: float,
) -> PredictionResult:
    """
    Jalankan inferensi menggunakan model dari HuggingFace Hub (kode: H).

    Model diunduh via `transformers` dan di-cache oleh Streamlit.
    Inferensi berjalan sepenuhnya di sisi server (CPU) — tidak bergantung
    pada API eksternal setelah model berhasil dimuat.
    """
    model = load_model_from_hub(model_id)
    if model is None:
        return _error_result(
            "H",
            "Model tidak dapat dimuat dari Hugging Face Hub. "
            "Pastikan koneksi internet tersedia, atau beralih ke mode Google Gemini.",
        )

    try:
        processed = preprocess_image(image)
        raw_results: list[dict] = model(processed)

        if not raw_results:
            return _error_result("H", "Model tidak menghasilkan prediksi.")

        # Ambil prediksi dengan skor tertinggi
        top = max(raw_results, key=lambda x: x["score"])
        label = _map_label(top["label"])
        confidence = float(top["score"])

        return PredictionResult(
            label=label,
            confidence=confidence,
            color=CLASS_COLORS.get(label, "#475569"),
            tip=HANDLING_TIPS.get(label, "Buang ke tempat sampah yang sesuai."),
            all_scores=[
                {"label": _map_label(r["label"]), "score": float(r["score"])}
                for r in raw_results
            ],
            is_confident=confidence >= threshold,
            source="H",
        )

    except Exception as exc:
        logger.error(f"[HF Predict] Inferensi gagal: {exc}", exc_info=True)
        return _error_result("H", f"Inferensi HuggingFace gagal: {exc}")


# ─── Mode: Google Gemini ──────────────────────────────────────────────────────

_GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def _predict_gemini(
    image: Image.Image,
    api_key: str,
    threshold: float,
) -> PredictionResult:
    """
    Jalankan inferensi menggunakan Google Gemini Multimodal AI (kode: G).

    Gambar dikirim ke Google API dengan prompt instruksi spesifik.
    Tidak memerlukan download model — seluruh pemrosesan di sisi Google.
    Memerlukan Google Gemini API Key yang valid.
    """
    if not api_key or not api_key.strip():
        return _error_result(
            "G",
            "Google Gemini API Key belum dikonfigurasi. "
            "Dapatkan API Key gratis di: aistudio.google.com, "
            "lalu masukkan di halaman Pengaturan.",
        )

    try:
        img_b64 = pil_to_base64(image, fmt="JPEG")
        classes_str = ", ".join(WASTE_CLASSES)

        prompt = (
            f"Klasifikasikan jenis material sampah dari gambar ini.\n"
            f"Kategori yang tersedia (pilih TEPAT satu): {classes_str}.\n\n"
            f"Kembalikan HANYA JSON mentah (tanpa pembungkus markdown atau teks lain) "
            f"dengan format berikut:\n"
            f'{{"label": "<salah satu kategori di atas>", "confidence": <angka 0.0-1.0>}}'
        )

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}},
                ]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,   # Rendah agar respons konsisten
            },
        }

        url = f"{_GEMINI_API_URL}?key={api_key.strip()}"
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 429:
            return _error_result(
                "G",
                "Google Gemini API telah mencapai batas kuota (rate limit). "
                "Tunggu beberapa saat atau beralih ke mode Hugging Face.",
            )

        if response.status_code != 200:
            return _error_result(
                "G",
                f"Gemini API mengembalikan error {response.status_code}: "
                f"{response.text[:200]}",
            )

        res_json = response.json()
        candidates = res_json.get("candidates", [])
        if not candidates:
            return _error_result("G", "Gemini tidak mengembalikan kandidat respons.")

        text_out = candidates[0]["content"]["parts"][0]["text"].strip()
        data = json.loads(text_out)

        raw_label = str(data.get("label", "Tidak Dikenali")).strip()
        confidence = float(data.get("confidence", 0.9))
        label = _map_label(raw_label)

        return PredictionResult(
            label=label,
            confidence=confidence,
            color=CLASS_COLORS.get(label, "#475569"),
            tip=HANDLING_TIPS.get(label, "Buang ke tempat sampah yang sesuai."),
            all_scores=[{"label": label, "score": confidence}],
            is_confident=confidence >= threshold,
            source="G",
        )

    except json.JSONDecodeError:
        return _error_result(
            "G",
            f"Respons dari Gemini bukan JSON valid: '{text_out[:100]}'"
            if 'text_out' in dir() else "Gagal mem-parse respons JSON dari Gemini.",
        )
    except requests.exceptions.Timeout:
        return _error_result(
            "G",
            "Koneksi ke Google Gemini timeout (>30 detik). "
            "Coba lagi atau beralih ke mode Hugging Face.",
        )
    except Exception as exc:
        logger.error(f"[Gemini Predict] Error tidak terduga: {exc}", exc_info=True)
        return _error_result("G", f"Inferensi Gemini gagal: {exc}")


# ─── Public API ───────────────────────────────────────────────────────────────

def predict(
    image: Image.Image,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> PredictionResult:
    """
    Jalankan prediksi klasifikasi sampah pada satu gambar.

    Mode inferensi dan model dibaca secara otomatis dari pengaturan aplikasi
    (session state → SQLite database → default).

    Args:
        image:     PIL Image dari kamera atau file upload.
        threshold: Ambang batas confidence minimum (default: 0.60 / 60%).

    Returns:
        PredictionResult dengan label, confidence, tips penanganan, dan metadata.
    """
    # ── Validasi gambar ───────────────────────────────────────────────────────
    is_valid, msg = validate_image(image)
    if not is_valid:
        return _error_result("H", f"Gambar tidak valid: {msg}")

    # ── Auto-enhance gambar gelap ─────────────────────────────────────────────
    image = _auto_enhance(image)

    # ── Baca konfigurasi aktif ────────────────────────────────────────────────
    mode = get_setting("inference_mode") or "hugging"
    model_id = get_setting("model_id") or WASTE_MODEL_ID

    logger.info(f"[Predict] Mode={mode} | Model={model_id} | Threshold={threshold}")

    # ── Dispatch ke engine yang sesuai ───────────────────────────────────────
    if mode == "gemini":
        import importlib
        import app.config as cfg
        importlib.reload(cfg)
        api_key = cfg.GEMINI_API_KEY or get_setting("gemini_api_key") or ""
        return _predict_gemini(image, api_key, threshold)

    # Default: mode "hugging"
    return _predict_hugging(image, model_id, threshold)


def predict_batch(
    images: list[Image.Image],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list[PredictionResult]:
    """
    Jalankan prediksi untuk sejumlah gambar sekaligus.

    Args:
        images:    Daftar PIL Image.
        threshold: Ambang batas confidence minimum.

    Returns:
        List PredictionResult dengan urutan yang sama dengan input.
    """
    return [predict(img, threshold) for img in images]
