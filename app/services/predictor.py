"""
predictor.py — Menjalankan inferensi model dan mengembalikan prediksi terstruktur.
Mendukung tiga mode:
1. Lokal (Offline) -> Kode (L)
2. Hugging Face Serverless Cloud API -> Kode (H)
3. Google Gemini Multimodal AI -> Kode (G)
"""

from PIL import Image, ImageEnhance
from dataclasses import dataclass
from typing import Optional
import logging
import requests
import io
import json
import numpy as np

from app.services.model_loader import load_model
from app.services.preprocessing import preprocess_image, validate_image
from app.config import DEFAULT_CONFIDENCE_THRESHOLD, WASTE_CLASSES, HANDLING_TIPS, CLASS_COLORS
from app.utils.cache import get_setting
from app.utils.image_utils import pil_to_bytes, pil_to_base64

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Struktur hasil prediksi satu gambar."""
    label: str
    confidence: float           # 0.0 – 1.0
    color: str                  # hex warna kelas
    tip: str                    # saran penanganan
    all_scores: list[dict]      # [{"label": ..., "score": ...}, ...]
    is_confident: bool          # apakah melebihi threshold
    source: str                 # sumber AI: "G" (Gemini), "H" (Hugging), "L" (Lokal)
    error: Optional[str] = None # pesan error jika gagal


def _map_label_to_class(raw_label: str) -> str:
    """
    Mapping label mentah dari model ke kelas sampah yang dikenal.
    Jika model sudah pakai label Bahasa Indonesia, biarkan apa adanya.
    """
    label_lower = raw_label.lower()

    mapping = {
        "organic":    "Organik",
        "food":       "Organik",
        "vegetable":  "Organik",
        "plastic":    "Plastik",
        "bottle":     "Plastik",
        "paper":      "Kertas",
        "cardboard":  "Kertas",
        "glass":      "Kaca",
        "metal":      "Logam",
        "can":        "Logam",
        "battery":    "B3 (Berbahaya)",
        "electronic": "B3 (Berbahaya)",
    }

    for keyword, mapped in mapping.items():
        if keyword in label_lower:
            return mapped

    # Cek apakah sudah nama kelas Indonesia
    for cls in WASTE_CLASSES:
        if cls.lower() in label_lower or label_lower in cls.lower():
            return cls

    return raw_label  # kembalikan apa adanya jika tidak dikenali


def _predict_cloud(image: Image.Image, model_id: str, hf_token: str, threshold: float) -> PredictionResult:
    """Melakukan inferensi menggunakan Hugging Face Serverless Inference API -> Kode (H)."""
    try:
        # Convert PIL Image ke bytes JPEG
        img_bytes = pil_to_bytes(image, fmt="JPEG")

        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {}
        if hf_token and hf_token.strip():
            headers["Authorization"] = f"Bearer {hf_token.strip()}"

        logger.info(f"Querying HF Cloud API for model: {model_id}")
        response = requests.post(api_url, headers=headers, data=img_bytes, timeout=15)

        # Cek jika serverless model sedang dimuat (cold start)
        if response.status_code == 503:
            res_json = response.json()
            est_time = res_json.get("estimated_time", 20.0)
            return PredictionResult(
                label="Error", confidence=0.0,
                color="#DC2626", tip="", all_scores=[],
                is_confident=False, source="H",
                error=f"Model sedang dibangunkan di server Hugging Face (cold start). Silakan coba lagi dalam {est_time:.0f} detik."
            )

        if response.status_code != 200:
            try:
                err_msg = response.json().get("error", f"HTTP Error {response.status_code}")
            except Exception:
                err_msg = response.text[:100]
            return PredictionResult(
                label="Error", confidence=0.0,
                color="#DC2626", tip="", all_scores=[],
                is_confident=False, source="H",
                error=f"Gagal memanggil HF Cloud API: {err_msg}"
            )

        raw_results = response.json()
        
        if not isinstance(raw_results, list) or not raw_results:
            return PredictionResult(
                label="Error", confidence=0.0,
                color="#DC2626", tip="", all_scores=[],
                is_confident=False, source="H",
                error="Hugging Face API mengembalikan format respons yang tidak valid."
            )

        # Ambil prediksi terbaik
        top = max(raw_results, key=lambda x: x["score"])
        label = _map_label_to_class(top["label"])
        confidence = float(top["score"])

        return PredictionResult(
            label=label,
            confidence=confidence,
            color=CLASS_COLORS.get(label, "#475569"),
            tip=HANDLING_TIPS.get(label, "Buang ke tempat sampah yang sesuai."),
            all_scores=[
                {"label": _map_label_to_class(r["label"]), "score": float(r["score"])}
                for r in raw_results
            ],
            is_confident=confidence >= threshold,
            source="H",
        )

    except requests.exceptions.Timeout:
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="H",
            error="Koneksi ke Hugging Face API mengalami timeout (waktu habis)."
        )
    except Exception as exc:
        logger.error(f"Cloud prediction failed: {exc}")
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="H", error=f"Inferensi Cloud gagal: {str(exc)}"
        )


def _predict_gemini(image: Image.Image, api_key: str, threshold: float) -> PredictionResult:
    """Melakukan inferensi menggunakan Google Gemini 2.5 Flash API -> Kode (G)."""
    if not api_key or not api_key.strip():
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="G",
            error="Google Gemini API Key belum dimasukkan di halaman Pengaturan."
        )

    try:
        # Convert PIL Image ke base64
        img_b64 = pil_to_base64(image, fmt="JPEG")

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
        
        # Prompt visual spesifik agar hanya menghasilkan satu kata dalam JSON terstruktur
        classes_str = ", ".join(WASTE_CLASSES)
        prompt = (
            f"Klasifikasikan jenis material sampah dari gambar ini.\n"
            f"Pilihan kategori yang harus digunakan: {classes_str}.\n"
            f"Kembalikan respons wajib berupa format JSON mentah tanpa pembungkus markdown ```json.\n"
            f"Skema JSON yang harus Anda kembalikan secara tepat:\n"
            f"{{\n"
            f"  \"label\": \"salah satu kata kategori di atas secara tepat (misal: Plastik, Kaca, Kertas, Organik, Logam, atau B3 (Berbahaya))\",\n"
            f"  \"confidence\": angka desimal antara 0.0 sampai 1.0\n"
            f"}}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        headers = {"Content-Type": "application/json"}
        logger.info("Querying Google Gemini API...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)

        if response.status_code != 200:
            return PredictionResult(
                label="Error", confidence=0.0,
                color="#DC2626", tip="", all_scores=[],
                is_confident=False, source="G",
                error=f"Gagal memanggil Google Gemini API: {response.text[:200]}"
            )

        res_json = response.json()
        
        # Validasi struktur respons Gemini
        if "candidates" not in res_json or not res_json["candidates"]:
            return PredictionResult(
                label="Error", confidence=0.0,
                color="#DC2626", tip="", all_scores=[],
                is_confident=False, source="G",
                error="Google Gemini tidak mengembalikan kandidat respons."
            )

        text_out = res_json["candidates"][0]["content"]["parts"][0]["text"]
        
        # Parse hasil JSON dari Gemini
        data = json.loads(text_out.strip())
        raw_label = data.get("label", "Tidak Dikenali").strip()
        confidence = float(data.get("confidence", 0.95))

        # Cocokkan label dengan daftar WASTE_CLASSES kita
        matched_label = "Tidak Dikenali"
        for cls in WASTE_CLASSES:
            if cls.lower() in raw_label.lower() or raw_label.lower() in cls.lower():
                matched_label = cls
                break

        if matched_label == "Tidak Dikenali":
            matched_label = raw_label

        return PredictionResult(
            label=matched_label,
            confidence=confidence,
            color=CLASS_COLORS.get(matched_label, "#475569"),
            tip=HANDLING_TIPS.get(matched_label, "Buang ke tempat sampah yang sesuai."),
            all_scores=[{"label": matched_label, "score": confidence}],
            is_confident=confidence >= threshold,
            source="G",
        )

    except json.JSONDecodeError:
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="G",
            error=f"Gagal membaca format JSON respons dari Gemini: {text_out[:100]}"
        )
    except Exception as exc:
        logger.error(f"Gemini API failure: {exc}")
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="G",
            error=f"Inferensi Google Gemini gagal: {str(exc)}"
        )


def predict(image: Image.Image, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> PredictionResult:
    """
    Jalankan prediksi pada satu gambar (Lokal, HF Cloud, atau Google Gemini).

    Args:
        image: PIL Image dari user.
        threshold: Batas confidence minimum.

    Returns:
        PredictionResult dengan semua informasi yang dibutuhkan UI.
    """
    # Validasi citra dasar
    is_valid, msg = validate_image(image)
    if not is_valid:
        return PredictionResult(
            label="Tidak Dikenali", confidence=0.0,
            color="#9E9E9E", tip="", all_scores=[],
            is_confident=False, source="L", error=msg,
        )

    # Auto-enhancement untuk kondisi cahaya gelap!
    gray_img = image.convert("L")
    avg_brightness = np.mean(np.array(gray_img))
    
    # Jika tingkat kecerahan di bawah 85 (kondisi gelap), naikkan kecerahan & kontras secara otomatis
    if avg_brightness < 85:
        logger.info(f"Kondisi cahaya gelap terdeteksi (rata-rata kecerahan: {avg_brightness:.1f}). Mengaktifkan auto-brightness & contrast boost...")
        image = ImageEnhance.Brightness(image).enhance(1.6)
        image = ImageEnhance.Contrast(image).enhance(1.3)

    # Deteksi mode inferensi
    inference_mode = get_setting("inference_mode")
    model_id = get_setting("model_id")

    # Mode 3: Google Gemini AI (Multimodal - visual prompting) -> Kode (G)
    if inference_mode == "gemini":
        import importlib
        import app.config as config
        importlib.reload(config)
        gemini_key = config.GEMINI_API_KEY if config.GEMINI_API_KEY else get_setting("gemini_api_key")
        return _predict_gemini(image, gemini_key, threshold)

    # Mode 2: Cloud Inference (Hugging Face API) -> Kode (H)
    if inference_mode == "cloud":
        hf_token = get_setting("hf_token")
        return _predict_cloud(image, model_id, hf_token, threshold)

    # Mode 1: Local Inference (Offline) -> Kode (L)
    model = load_model(model_id)
    if model is None:
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="L",
            error="Model lokal tidak tersedia. Hubungkan ke internet untuk mengunduh model pertama kali.",
        )

    try:
        # Preprocess
        processed = preprocess_image(image)

        # Inferensi lokal
        raw_results: list[dict] = model(processed)   # [{"label": ..., "score": ...}]

        # Ambil prediksi terbaik
        top = max(raw_results, key=lambda x: x["score"])
        label = _map_label_to_class(top["label"])
        confidence = float(top["score"])

        return PredictionResult(
            label=label,
            confidence=confidence,
            color=CLASS_COLORS.get(label, "#475569"),
            tip=HANDLING_TIPS.get(label, "Buang ke tempat sampah yang sesuai."),
            all_scores=[
                {"label": _map_label_to_class(r["label"]), "score": float(r["score"])}
                for r in raw_results
            ],
            is_confident=confidence >= threshold,
            source="L",
        )

    except Exception as exc:
        logger.error(f"Prediksi lokal gagal: {exc}")
        return PredictionResult(
            label="Error", confidence=0.0,
            color="#DC2626", tip="", all_scores=[],
            is_confident=False, source="L", error=str(exc),
        )


def predict_batch(images: list[Image.Image], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> list[PredictionResult]:
    """
    Jalankan prediksi untuk banyak gambar sekaligus.

    Args:
        images: List PIL Image.
        threshold: Batas confidence minimum.

    Returns:
        List PredictionResult.
    """
    return [predict(img, threshold) for img in images]
