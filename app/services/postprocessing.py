"""
postprocessing.py — Mengolah hasil prediksi untuk keperluan penyimpanan & analytics.
"""

import datetime
import uuid
import pandas as pd

from app.services.predictor import PredictionResult


def result_to_record(result: PredictionResult, filename: str = "upload") -> dict:
    """
    Ubah PredictionResult menjadi dict untuk disimpan ke history/session state.

    Args:
        result: Hasil prediksi.
        filename: Nama file gambar.

    Returns:
        Dict record siap simpan.
    """
    return {
        "id":         str(uuid.uuid4())[:8],
        "timestamp":  datetime.datetime.now().isoformat(timespec="seconds"),
        "filename":   filename,
        "label":      result.label,
        "confidence": round(result.confidence * 100, 2),
        "is_confident": result.is_confident,
        "tip":        result.tip,
        "error":      result.error,
        "source":     result.source,
    }


def records_to_dataframe(records: list[dict]) -> pd.DataFrame:
    """
    Konversi list record ke DataFrame pandas untuk tabel & analytics.

    Args:
        records: List dict dari result_to_record.

    Returns:
        pd.DataFrame.
    """
    if not records:
        return pd.DataFrame(columns=["id", "timestamp", "filename", "label", "confidence", "is_confident"])
    return pd.DataFrame(records)


def compute_class_distribution(records: list[dict]) -> dict[str, int]:
    """
    Hitung distribusi kelas dari semua record history.

    Returns:
        {label: count}
    """
    dist: dict[str, int] = {}
    for r in records:
        lbl = r.get("label", "Unknown")
        dist[lbl] = dist.get(lbl, 0) + 1
    return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))


def export_to_csv(records: list[dict]) -> str:
    """
    Ekspor records ke string CSV.

    Returns:
        CSV string (bisa langsung di-download via st.download_button).
    """
    df = records_to_dataframe(records)
    return df.to_csv(index=False)
