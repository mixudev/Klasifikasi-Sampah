"""
about.py — Halaman 9: Tentang Aplikasi.
Menampilkan misi proyek, stack teknologi, serta disclaimer legalitas AI.
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
from app.components.icons import render_svg


def render() -> None:
    st.title("Tentang WasteAI")
    st.caption("Pelajari filosofi proyek, teknologi yang menopang sistem, dan disclaimer penggunaan.")

    # ── VISI & MISI ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1.5rem; margin-bottom:1rem;">
            Misi Ekologi & AI
        </h3>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "WasteAI dikembangkan sebagai alat bantu digital instan untuk menumbuhkan kesadaran memilah sampah sejak "
        "dari sumbernya (rumah tangga/kantor). Dengan memilah sampah secara tepat, kita dapat meningkatkan rasio "
        "daur ulang nasional, menekan volume penumpukan di Tempat Pembuangan Akhir (TPA), serta mengurangi pencemaran "
        "lingkungan akibat penanganan limbah B3 yang keliru."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STACK TEKNOLOGI (Industrial Cards) ────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1rem;">
            Arsitektur Teknologi
        </h3>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 180px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("settings", size=24, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.82rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Streamlit Core</strong>
                <p style="color: #475569; font-size: 0.78rem; margin: 0; line-height: 1.5;">
                    Framework Python untuk merender antarmuka web secara reaktif, modular, dan hemat memori.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 180px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("recycle", size=24, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.82rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">HuggingFace ViT</strong>
                <p style="color: #475569; font-size: 0.78rem; margin: 0; line-height: 1.5;">
                    Model Vision Transformer (ViT) mutakhir untuk inferensi klasifikasi citra berkurasi tinggi.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 180px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("database", size=24, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.82rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Pillow & Pandas</strong>
                <p style="color: #475569; font-size: 0.78rem; margin: 0; line-height: 1.5;">
                    Library pemrosesan matriks piksel gambar serta manipulasi riwayat analisis data terstruktur.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DISCLAIMER LEGAL ─────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-bottom:1rem;">
            Batasan Hukum & Disclaimer
        </h3>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "DISCLAIMER: Aplikasi WasteAI merupakan alat bantu edukasi berbasis kecerdasan buatan. "
        "Akurasi klasifikasi sangat bergantung pada kualitas pencahayaan, posisi kamera, dan kejelasan objek gambar. "
        "Hasil prediksi tidak boleh dijadikan satu-satunya rujukan hukum untuk mengolah bahan limbah beracun "
        "yang memerlukan regulasi dan sertifikasi keamanan khusus."
    )
