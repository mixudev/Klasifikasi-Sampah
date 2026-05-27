"""
upload.py — Halaman 5: Upload Batch Detection.
Upload banyak gambar sekaligus, proses semua, tampilkan tabel hasil.
Bebas emoji dan sudut membulat sesuai UI_ROLE.md.
"""

import streamlit as st
from PIL import Image

from app.services.predictor import predict
from app.services.postprocessing import result_to_record, records_to_dataframe, export_to_csv
from app.utils.image_utils import load_uploaded_file
from app.utils.cache import get_setting, add_to_history
from app.config import MAX_BATCH_UPLOAD


def render() -> None:
    st.title("Upload Batch")
    st.caption(f"Unggah hingga {MAX_BATCH_UPLOAD} file gambar sekaligus untuk analisis massal.")

    threshold = get_setting("confidence_threshold")

    uploaded_files = st.file_uploader(
        "Pilih beberapa gambar",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if not uploaded_files:
        st.info("Pilih beberapa gambar di atas untuk memulai batch detection.")
        return

    if len(uploaded_files) > MAX_BATCH_UPLOAD:
        st.warning(f"Maksimum {MAX_BATCH_UPLOAD} gambar. Sebanyak {len(uploaded_files) - MAX_BATCH_UPLOAD} file diabaikan.")
        uploaded_files = uploaded_files[:MAX_BATCH_UPLOAD]

    if st.button("PROSES BATCH GAMBAR", type="primary"):
        records = []
        progress = st.progress(0, text="Memproses berkas...")
        status_area = st.empty()

        for i, uf in enumerate(uploaded_files):
            status_area.caption(f"Menganalisis: {uf.name} ({i+1}/{len(uploaded_files)})")
            img = load_uploaded_file(uf)
            if img is None:
                continue

            result = predict(img, threshold=threshold)
            record = result_to_record(result, uf.name)
            records.append(record)

            if get_setting("auto_save_history"):
                add_to_history(record)

            progress.progress((i + 1) / len(uploaded_files), text=f"Kemajuan: {i+1} dari {len(uploaded_files)} selesai")

        status_area.empty()
        st.success(f"Analisis batch selesai. Sebanyak {len(records)} berkas berhasil diidentifikasi.")

        # ── Tabel Hasil ──────────────────────────────────────────────────────
        df = records_to_dataframe(records)
        display_cols = ["filename", "label", "confidence", "is_confident", "timestamp"]
        
        # Upper case column headers for an industrial editorial look
        df_display = df[[c for c in display_cols if c in df.columns]].copy()
        df_display.columns = [c.upper() for c in df_display.columns]
        
        st.dataframe(df_display, use_container_width=True)

        # ── Download CSV (Bebas Emoji) ───────────────────────────────────────
        csv_data = export_to_csv(records)
        st.download_button(
            label="DOWNLOAD HASIL ANALISIS (CSV)",
            data=csv_data,
            file_name="batch_detection_results.csv",
            mime="text/csv",
        )
