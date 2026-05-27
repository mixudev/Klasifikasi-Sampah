"""
analytics.py — Halaman 7: Analytics.
Menyajikan grafik analisis dari data riwayat scan sesi ini.
Bebas emoji dan menerapkan sudut siku sesuai UI_ROLE.md.
"""

import streamlit as st
import pandas as pd
from app.utils.cache import get_history
from app.components.cards import render_stat_card
from app.services.postprocessing import records_to_dataframe


def render() -> None:
    st.title("Data Analytics")
    st.caption("Visualisasi statistik dan analisis distribusi sampah hasil pemindaian sesi saat ini.")

    history = get_history()

    if not history:
        st.info("Belum ada data riwayat scan untuk dianalisis. Mulailah melakukan scan pada halaman **Scan Sampah**.")
        return

    # Convert history to DataFrame
    df = records_to_dataframe(history)

    # ── RINGKASAN STATISTIK (Editorial Stat Cards) ───────────────────────────
    st.markdown(
        """
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; border-left:4px solid #16A34A; padding-left:0.6rem; margin-top:1.5rem; margin-bottom:1rem;">
            Metrik Utama Sesi Ini
        </h3>
        """,
        unsafe_allow_html=True,
    )

    avg_conf = df["confidence"].mean() if "confidence" in df.columns else 0.0
    verified_pct = (df["is_confident"].sum() / len(df)) * 100 if "is_confident" in df.columns and len(df) > 0 else 0.0
    
    classes = df["label"].tolist() if "label" in df.columns else []
    most_common = max(set(classes), key=classes.count) if classes else "TIDAK ADA"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Total Pemindaian", len(df), icon="recycle", color="#0F172A")
    with c2:
        render_stat_card("Rata-Rata Confidence", f"{avg_conf:.1f}%", icon="analytics", color="#16A34A")
    with c3:
        render_stat_card("Rasio Terverifikasi", f"{verified_pct:.1f}%", icon="check", color="#2563EB")
    with c4:
        render_stat_card("Kategori Terbanyak", most_common.upper(), icon="shield", color="#4B5563")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GRAFIK DISTRIBUSI (Data-First Visualization) ─────────────────────────
    col_chart_1, col_chart_2 = st.columns(2)

    with col_chart_1:
        st.markdown(
            """
            <h4 style="font-size:0.95rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:1rem;">
                Frekuensi Sampah Per Kategori
            </h4>
            """,
            unsafe_allow_html=True,
        )
        if "label" in df.columns:
            # Count occurrences of each category
            class_counts = df["label"].value_counts().reset_index()
            class_counts.columns = ["KATEGORI", "JUMLAH"]
            class_counts = class_counts.set_index("KATEGORI")
            st.bar_chart(class_counts, color="#16A34A")
        else:
            st.info("Data kategori tidak tersedia.")

    with col_chart_2:
        st.markdown(
            """
            <h4 style="font-size:0.95rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:1rem;">
                Distribusi Nilai Keyakinan (Confidence)
            </h4>
            """,
            unsafe_allow_html=True,
        )
        if "confidence" in df.columns:
            # Create confidence intervals
            bins = [0, 50, 60, 70, 80, 90, 100]
            labels = ["<50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
            df["INTERVAL"] = pd.cut(df["confidence"], bins=bins, labels=labels, include_lowest=True)
            conf_counts = df["INTERVAL"].value_counts().reindex(labels).fillna(0).reset_index()
            conf_counts.columns = ["CONFIDENCE INTERVAL", "JUMLAH"]
            conf_counts = conf_counts.set_index("CONFIDENCE INTERVAL")
            st.bar_chart(conf_counts, color="#0F172A")
        else:
            st.info("Data confidence tidak tersedia.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ANALISIS INSIGHTS ────────────────────────────────────────────────────
    st.markdown(
        """
        <h4 style="font-size:0.95rem; font-weight:800; color:#0F172A; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:1rem;">
            Insight Edukasi Lingkungan
        </h4>
        """,
        unsafe_allow_html=True,
    )
    
    total_recyclable = df["label"].isin(["Plastik", "Kertas", "Kaca", "Logam"]).sum()
    recycle_rate = (total_recyclable / len(df)) * 100 if len(df) > 0 else 0.0

    st.info(
        f"Analisis Sesi: **{recycle_rate:.1f}%** dari total sampah yang dipindai merupakan kategori material "
        f"yang **dapat didaur ulang** secara ekonomis (Plastik, Kertas, Kaca, Logam). "
        f"Pastikan material tersebut dibersihkan dari sisa organik sebelum disalurkan ke Bank Sampah terdekat."
    )
