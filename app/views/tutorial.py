"""
tutorial.py — Halaman 2: Tutorial & Cara Pakai.
Panduan pengambilan foto sampah yang benar dan contoh visualisasi panduan.
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
from app.components.icons import render_svg


def render() -> None:
    st.title("Panduan Pengguna")
    st.caption("Pelajari cara mengambil gambar yang optimal agar model AI dapat mengklasifikasikan sampah secara akurat.")

    # ── PRINSIP FOTOGRAFI AI (Editorial Layout) ──────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1.5rem; margin-bottom:1rem;">
            TIPS PENGAMBILAN GAMBAR YANG BENAR
        </h3>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 210px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("settings", size=28, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.85rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Cahaya Cukup</strong>
                <p style="color: #475569; font-size: 0.8rem; margin: 0; line-height: 1.5;">
                    Pastikan objek sampah tidak tertutup bayangan tebal atau terkena cahaya berlebih (backlight) agar detail warna/tekstur terlihat jelas oleh model AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 210px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("camera", size=28, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.85rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Satu Objek Utama</strong>
                <p style="color: #475569; font-size: 0.8rem; margin: 0; line-height: 1.5;">
                    Tempatkan hanya satu objek sampah di tengah frame. Gambar yang berisi tumpukan berbagai jenis sampah akan membingungkan model prediksi.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="border: 1px solid #E5E7EB; padding: 1.2rem; background: #FFFFFF; height: 210px;">
                <div style="margin-bottom: 0.5rem;">{render_svg("recycle", size=28, color="#16A34A")}</div>
                <strong style="color: #0F172A; text-transform: uppercase; font-size: 0.85rem; letter-spacing:0.5px; display:block; margin-bottom:0.5rem;">Latar Belakang Polos</strong>
                <p style="color: #475569; font-size: 0.8rem; margin: 0; line-height: 1.5;">
                    Gunakan latar belakang netral atau polos jika memungkinkan (seperti lantai ubin atau meja kayu) untuk meminimalkan distorsi deteksi objek.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DO & DON'T (Editorial Table) ─────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1rem; margin-bottom:1rem;">
            PERBANDINGAN DO & DON'T
        </h3>
        """,
        unsafe_allow_html=True,
    )

    c_do, c_dont = st.columns(2)

    with c_do:
        st.markdown(
            f"""
            <div style="border:1px solid #16A34A; border-top: 4px solid #16A34A; padding:1.2rem; background:#FFFFFF;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;">
                    {render_svg("check", size=22, color="#16A34A")}
                    <strong style="color:#16A34A; text-transform:uppercase; font-size:0.9rem; letter-spacing:0.5px;">REKOMENDASI (DO)</strong>
                </div>
                <ul style="color:#475569; font-size:0.82rem; line-height:1.7; padding-left:1.2rem; margin:0;">
                    <li>Objek berada di jarak dekat (30 - 50 cm dari kamera).</li>
                    <li>Sudut pengambilan gambar tegak lurus ke arah objek.</li>
                    <li>Wadah plastik/kaca telah dikosongkan dari isinya.</li>
                    <li>Gambar tajam dan fokus (tidak buram/goyang).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_dont:
        st.markdown(
            f"""
            <div style="border:1px solid #DC2626; border-top: 4px solid #DC2626; padding:1.2rem; background:#FFFFFF;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;">
                    {render_svg("alert-triangle", size=22, color="#DC2626")}
                    <strong style="color:#DC2626; text-transform:uppercase; font-size:0.9rem; letter-spacing:0.5px;">HINDARI (DON'T)</strong>
                </div>
                <ul style="color:#475569; font-size:0.82rem; line-height:1.7; padding-left:1.2rem; margin:0;">
                    <li>Memotret tempat pembuangan sampah penuh dari kejauhan.</li>
                    <li>Menggunakan gambar resolusi terlalu rendah (&lt; 32x32 piksel).</li>
                    <li>Memotret objek yang hancur parah sehingga wujud aslinya hilang.</li>
                    <li>Membiarkan bayangan tebal menutupi bentuk utama sampah.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FAQ SINGKAT ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1rem; margin-bottom:1rem;">
            FAQ (PERTANYAAN UMUM)
        </h3>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Mengapa AI salah mengklasifikasikan botol kaca menjadi plastik?", expanded=False):
        st.write(
            "Model Vision Transformer mengandalkan tekstur permukaan, transparansi, dan refleksi cahaya. "
            "Botol kaca yang sangat jernih dan tipis terkadang terlihat mirip dengan plastik PET. "
            "Cobalah mengambil foto dengan latar belakang gelap agar refleksi kaca lebih jelas terlihat."
        )

    with st.expander("Bagaimana cara klasifikasi sampah B3?", expanded=False):
        st.write(
            "Sampah B3 seperti baterai, akumulator, atau kaleng aerosol memiliki corak teks atau bentuk yang sangat spesifik. "
            "Pastikan simbol bahaya atau label tulisan pada baterai/kaleng menghadap langsung ke arah kamera saat memotret."
        )
