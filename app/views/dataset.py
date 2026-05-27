"""
dataset.py — Halaman 8: Dataset Explorer.
Memberikan wawasan tentang dataset training model AI dan keterbatasan model (bias).
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
from app.components.icons import render_svg


def render() -> None:
    st.title("Dataset Explorer")
    st.caption("Penjelasan dataset training AI, distribusi data awal, serta analisis bias model.")

    # ── DETAIL DATASET ───────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1.5rem; margin-bottom:1rem;">
            Informasi Training Dataset
        </h3>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "Model AI klasifikasi sampah ini dilatih menggunakan dataset terbuka "
        "yang diadaptasi dari dataset **Garbage Classification** publik yang berisi ribuan "
        "gambar berlabel resolusi tinggi. Dataset ini melatih model untuk mengenali fitur tekstur, "
        "warna, dan geometri khas dari masing-masing kategori sampah."
    )

    # ── ESTIMASI DISTRIBUSI KELAS (Editorial Table) ──────────────────────────
    st.markdown(
        """
        <h4 style="font-size:0.95rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; margin-top:1.5rem; margin-bottom:1rem;">
            Distribusi Data Training Awal
        </h4>
        """,
        unsafe_allow_html=True,
    )

    # Simple clean industrial table markdown
    st.markdown(
        """
        | KATEGORI SAMPAH | JUMLAH GAMBAR | PERSENTASE DATASET | METRIK AKURASI MODEL (F1-SCORE) |
        | :--- | :---: | :---: | :---: |
        | **Organik** | ~1.200 | 24% | 91.2% |
        | **Plastik** | ~1.150 | 23% | 88.5% |
        | **Kertas** | ~1.000 | 20% | 89.1% |
        | **Kaca** | ~850 | 17% | 84.7% |
        | **Logam** | ~600 | 12% | 86.4% |
        | **B3 (Berbahaya)** | ~200 | 4% | 81.0% |
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LIMITASI & BIAS MODEL ────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1rem; margin-bottom:1rem;">
            Keterbatasan & Bias Model AI
        </h3>
        """,
        unsafe_allow_html=True,
    )

    col_bias_1, col_bias_2 = st.columns(2)

    with col_bias_1:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 260px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("alert-triangle", size=24, color="#DC2626")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.82rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Bias Bentuk Hancur</strong>
                <p style="color: #475569; font-size: 0.78rem; margin: 0; line-height: 1.6;">
                    Model dilatih dengan mayoritas gambar objek utuh yang bersih. Akibatnya, sampah plastik yang sudah diremuk, disobek, atau berubah bentuk secara ekstrem cenderung mendapatkan skor keyakinan (confidence) yang lebih rendah dibandingkan wujud aslinya.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_bias_2:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 260px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("alert-triangle", size=24, color="#DC2626")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.82rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Ketidakseimbangan Data B3</strong>
                <p style="color: #475569; font-size: 0.78rem; margin: 0; line-height: 1.6;">
                    Jumlah gambar pelatihan untuk kategori B3 (seperti limbah baterai atau medis) jauh lebih sedikit dibanding kategori organik atau plastik. Hal ini menyebabkan bias klasifikasi di mana model lebih cenderung memprediksi kelas dominan ketika dihadapkan pada objek asing.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
