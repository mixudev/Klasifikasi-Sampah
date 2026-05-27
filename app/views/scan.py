"""
scan.py — Halaman 1: Scan Sampah (Core Feature).
Upload gambar / kamera → prediksi AI → tampilkan hasil + edukasi.
Bebas emoji dan sudut membulat sesuai UI_ROLE.md.
"""

import streamlit as st
from PIL import Image

from app.services.predictor import predict
from app.services.postprocessing import result_to_record
from app.utils.image_utils import load_uploaded_file, display_image_preview
from app.utils.cache import get_setting, add_to_history
from app.components.cards import render_result_card
from app.components.alerts import alert_model_not_loaded, alert_low_confidence


def render() -> None:
    st.title("Scan Sampah")
    st.caption("Unggah gambar material sampah atau ambil foto secara langsung menggunakan kamera.")

    threshold = get_setting("confidence_threshold")

    # ── Input Gambar (Bebas Emoji) ──────────────────────────────────────────
    tab_upload, tab_camera = st.tabs(["Upload Gambar", "Kamera"])

    image: Image.Image | None = None
    filename = "unknown"

    with tab_upload:
        uploaded = st.file_uploader(
            "Pilih gambar sampah",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        if uploaded:
            image = load_uploaded_file(uploaded)
            filename = uploaded.name

    with tab_camera:
        cam = st.camera_input("Ambil foto sampah", label_visibility="collapsed")
        if cam:
            image = load_uploaded_file(cam)
            filename = "kamera.jpg"

    # ── Preview + Tombol Scan ────────────────────────────────────────────────
    if image:
        col_img, col_action = st.columns([2, 1])
        with col_img:
            display_image_preview(image, caption=filename)
        with col_action:
            st.markdown("<br><br>", unsafe_allow_html=True)
            scan_btn = st.button(
                "MULAI ANALISIS AI",
                use_container_width=True,
                type="primary",
            )

        # ── Prediksi ────────────────────────────────────────────────────────
        if scan_btn:
            with st.spinner("AI sedang menganalisis objek..."):
                result = predict(image, threshold=threshold)

            if result.error and "model" in result.error.lower() and get_setting("inference_mode") == "local":
                alert_model_not_loaded()
                return

            st.markdown(
                """
                <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; margin-top:1.5rem;">
                    Hasil Deteksi
                </h3>
                """,
                unsafe_allow_html=True,
            )
            render_result_card(result)

            if not result.is_confident:
                alert_low_confidence(threshold * 100)

            # Distribusi semua kelas (Bebas Emoji)
            if result.all_scores:
                with st.expander("Distribusi Confidence Semua Kelas", expanded=False):
                    for item in sorted(result.all_scores, key=lambda x: x["score"], reverse=True):
                        st.progress(
                            item["score"],
                            text=f"{item['label']}: {item['score']*100:.1f}%",
                        )

            # Simpan ke history jika diaktifkan
            if get_setting("auto_save_history"):
                record = result_to_record(result, filename)
                add_to_history(record)
                st.caption("Disimpan ke dalam riwayat sesi.")

    else:
        st.info("Unggah gambar atau gunakan kamera di atas untuk memulai analisis.")
