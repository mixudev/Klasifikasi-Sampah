"""
settings.py — Halaman Pengaturan Sistem WasteAI.

Mengelola konfigurasi mode inferensi (HuggingFace Hub / Google Gemini),
model yang digunakan, ambang batas keyakinan, dan manajemen cache.
"""

import streamlit as st
from app.utils.cache import (
    IS_STREAMLIT_CLOUD,
    get_setting,
    update_setting,
    reset_settings,
    clear_history,
)
from app.services.model_loader import clear_model_cache
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

# Model-model yang direkomendasikan dengan deskripsinya
_RECOMMENDED_MODELS = {
    "wayfarer130/garbage-classification-vit": "🗑️ Waste ViT — Model khusus sampah (ViT, ~350MB)",
    "Sintong/TrashNetResNet18":               "⚡ TrashNet ResNet18 — Ringan & cepat (~45MB)",
    "google/vit-base-patch16-224":            "🤖 Google ViT Base — Model generik ImageNet (~350MB)",
}

_SECTION_STYLE = (
    'font-size:1.1rem; font-weight:800; color:#0F172A; '
    'text-transform:uppercase; letter-spacing:0.5px; '
    'border-left:4px solid #16A34A; padding-left:0.6rem; '
    'margin-top:1.8rem; margin-bottom:0.8rem;'
)


def _section_header(title: str) -> None:
    st.markdown(f'<h3 style="{_SECTION_STYLE}">{title}</h3>', unsafe_allow_html=True)


# ─── Render ───────────────────────────────────────────────────────────────────

def render() -> None:
    st.title("Pengaturan Sistem")
    st.caption(
        "Konfigurasi engine AI, model yang digunakan, "
        "ambang batas keyakinan, dan manajemen cache."
    )

    # ── Banner lingkungan ──────────────────────────────────────────────────────
    if IS_STREAMLIT_CLOUD:
        st.info(
            "☁️ **Berjalan di Streamlit Cloud**\n\n"
            "Mode **Hugging Face Hub** akan mengunduh model saat pertama kali digunakan "
            "(tergantung ukuran model: ~1–5 menit). Setelah itu, model di-cache selama sesi berlangsung. "
            "Mode **Google Gemini** tersedia sebagai alternatif instan tanpa download model."
        )

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # BAGIAN 1 — MODE INFERENSI
    # ═══════════════════════════════════════════════════════════════════════════
    _section_header("Mode Inferensi AI")

    current_mode = get_setting("inference_mode") or "hugging"

    MODE_OPTIONS = {
        "🤗 Hugging Face Hub  —  Model diunduh & dijalankan lokal (tanpa batas kuota)": "hugging",
        "✨ Google Gemini AI  —  Multimodal, instan, tanpa download model": "gemini",
    }

    # Pastikan index valid jika mode lama sudah dimigrasi
    mode_values = list(MODE_OPTIONS.values())
    current_index = mode_values.index(current_mode) if current_mode in mode_values else 0

    selected_label = st.radio(
        "Pilih Engine Pemrosesan AI",
        list(MODE_OPTIONS.keys()),
        index=current_index,
        help=(
            "• **HF Hub**: Model diunduh dari HuggingFace dan berjalan di server ini. "
            "Tidak ada batas kuota. Unggul untuk volume prediksi tinggi.\n\n"
            "• **Gemini**: Gambar dikirim ke Google AI. Tidak perlu download model. "
            "Ada batas kuota gratis harian."
        ),
    )

    new_mode = MODE_OPTIONS[selected_label]
    if new_mode != current_mode:
        update_setting("inference_mode", new_mode)
        st.success(f"✅ Mode inferensi berubah ke: **{new_mode.upper()}**")
        st.rerun()

    # ── Info kontekstual per mode ──────────────────────────────────────────────
    if new_mode == "hugging":
        model_id = get_setting("model_id") or WASTE_MODEL_ID
        st.info(
            f"ℹ️ **Mode HuggingFace Hub** aktif.\n\n"
            f"Model saat ini: `{model_id}`\n\n"
            "Model diunduh otomatis dari HuggingFace saat pertama kali digunakan, "
            "kemudian di-cache. Inferensi berjalan sepenuhnya di server — "
            "tidak ada batas kuota penggunaan."
        )
    else:
        current_key = get_setting("gemini_api_key") or ""
        is_key_set = bool(current_key.strip())

        if is_key_set:
            st.success(
                "✅ **Mode Google Gemini** aktif.\n\n"
                "API Key terdeteksi. Prediksi dikirim ke Google AI secara aman. "
                "Batas kuota gratis: ~1.500 permintaan/hari (Gemini 2.0 Flash)."
            )
        else:
            st.warning(
                "⚠️ **Gemini API Key belum dikonfigurasi.**\n\n"
                "Dapatkan API Key gratis di: [aistudio.google.com](https://aistudio.google.com)"
            )

        new_key = st.text_input(
            "Google Gemini API Key",
            value=current_key,
            type="password",
            placeholder="AIzaSy...",
            help="Dapatkan API Key gratis di: aistudio.google.com",
        )
        if new_key.strip() != current_key.strip():
            update_setting("gemini_api_key", new_key.strip())
            st.success("✅ API Key Gemini berhasil diperbarui.")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # BAGIAN 2 — KONFIGURASI MODEL (hanya relevan untuk mode HF Hub)
    # ═══════════════════════════════════════════════════════════════════════════
    _section_header("Konfigurasi Model Hugging Face Hub")

    current_model = get_setting("model_id") or WASTE_MODEL_ID

    st.caption("**Model Rekomendasi** (klik untuk memilih):")
    cols = st.columns(len(_RECOMMENDED_MODELS))
    for col, (model_id_opt, label) in zip(cols, _RECOMMENDED_MODELS.items()):
        with col:
            is_active = (model_id_opt == current_model)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, type=btn_type, use_container_width=True):
                if model_id_opt != current_model:
                    update_setting("model_id", model_id_opt)
                    clear_model_cache()   # Hapus cache agar model baru dimuat
                    st.success(f"✅ Model diubah ke: `{model_id_opt}`")
                    st.rerun()

    new_model = st.text_input(
        "Atau masukkan Model ID kustom",
        value=current_model,
        placeholder="username/nama-repo-model",
        help=(
            "Format: `username/repo-name` sesuai URL di huggingface.co. "
            "Hanya model publik yang dapat diakses tanpa token."
        ),
    )
    if new_model.strip() and new_model.strip() != current_model:
        update_setting("model_id", new_model.strip())
        clear_model_cache()
        st.success(f"✅ Model ID diperbarui: `{new_model.strip()}`")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # BAGIAN 3 — PARAMETER ANALISIS
    # ═══════════════════════════════════════════════════════════════════════════
    _section_header("Parameter Analisis AI")

    current_threshold = float(get_setting("confidence_threshold") or 0.6)
    new_threshold = st.slider(
        "Ambang Batas Keyakinan (Confidence Threshold)",
        min_value=0.10,
        max_value=1.00,
        value=current_threshold,
        step=0.05,
        format="%.0f%%",
        help=(
            "Hasil dianggap TERVERIFIKASI hanya jika tingkat keyakinan model "
            "melebihi nilai ini. Nilai lebih rendah = lebih sensitif namun lebih sering salah."
        ),
    )
    if new_threshold != current_threshold:
        update_setting("confidence_threshold", new_threshold)
        st.success(f"✅ Ambang batas diperbarui: **{new_threshold*100:.0f}%**")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════
    # BAGIAN 4 — MANAJEMEN RIWAYAT & SESI
    # ═══════════════════════════════════════════════════════════════════════════
    _section_header("Manajemen Riwayat & Sesi")

    current_auto_save = bool(get_setting("auto_save_history"))
    new_auto_save = st.checkbox(
        "Simpan Hasil Scan ke Riwayat Secara Otomatis",
        value=current_auto_save,
    )
    if new_auto_save != current_auto_save:
        update_setting("auto_save_history", new_auto_save)
        st.success("✅ Pengaturan penyimpanan riwayat diperbarui.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # BAGIAN 5 — PEMELIHARAAN CACHE & RESET
    # ═══════════════════════════════════════════════════════════════════════════
    _section_header("Pemeliharaan Cache & Reset")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "🔄 Hapus Cache Model AI",
            type="secondary",
            use_container_width=True,
            help="Paksa download ulang model saat prediksi berikutnya.",
        ):
            clear_model_cache()
            st.success("✅ Cache model berhasil dihapus. Model akan diunduh ulang saat prediksi berikutnya.")

    with col2:
        if st.button(
            "🗑️ Kosongkan Riwayat Scan",
            type="secondary",
            use_container_width=True,
        ):
            clear_history()
            st.success("✅ Seluruh riwayat scan berhasil dikosongkan.")
            st.rerun()

    with col3:
        if st.button(
            "⚠️ Reset Semua Pengaturan",
            type="secondary",
            use_container_width=True,
            help="Kembalikan semua pengaturan ke nilai default.",
        ):
            reset_settings()
            clear_model_cache()
            st.success("✅ Semua pengaturan dikembalikan ke default.")
            st.rerun()
