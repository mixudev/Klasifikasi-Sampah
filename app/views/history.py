"""
history.py — Halaman 6: Riwayat Deteksi.
Menampilkan timeline hasil scan dalam sesi ini.
Bebas emoji dan sudut membulat sesuai UI_ROLE.md.
"""

import streamlit as st
from app.utils.cache import get_history, clear_history
from app.services.postprocessing import export_to_csv
from app.config import CLASS_COLORS
from app.components.icons import render_svg, CLASS_ICON_MAPPING


def render() -> None:
    st.title("Riwayat Deteksi")
    st.caption("Linimasa hasil klasifikasi sampah yang telah dilakukan pada sesi aktif ini.")

    history = get_history()

    if not history:
        st.info("Belum ada riwayat pemindaian pada sesi ini. Silakan mulai di menu **Scan Sampah**.")
        return

    # ── Ringkasan (Editorial Style Metrics) ───────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pemindaian", len(history))
    with col2:
        confident = sum(1 for r in history if r.get("is_confident"))
        st.metric("Terverifikasi (>= threshold)", confident)
    with col3:
        if history:
            classes = [r["label"] for r in history]
            most_common = max(set(classes), key=classes.count)
            st.metric("Kelas Dominan", most_common.upper())

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Aksi (Bebas Emoji, Sharp Corners) ─────────────────────────────────────
    col_dl, col_clr, _ = st.columns([1, 1, 3])
    with col_dl:
        csv = export_to_csv(history)
        st.download_button("EXPORT CSV", data=csv, file_name="riwayat_scan.csv", mime="text/csv", type="secondary")
    with col_clr:
        if st.button("HAPUS SEMUA", type="secondary", use_container_width=True):
            clear_history()
            st.rerun()

    st.markdown("---")

    # ── Timeline (Industrial Layout with SVG and Sharp Corners) ───────────────
    for record in history:
        label = record.get("label", "Tidak Dikenali")
        color = CLASS_COLORS.get(label, "#475569")
        conf  = record.get("confidence", 0)
        ts    = record.get("timestamp", "")
        fname = record.get("filename", "")
        confident = record.get("is_confident", False)
        source = record.get("source", "L")

        icon_name = CLASS_ICON_MAPPING.get(label, "recycle")
        svg_html = render_svg(icon_name, size=18, color=color)

        badge_html = f"<span style='color:#16A34A; font-weight:700; font-size:0.68rem; border:1px solid #16A34A; padding:2px 6px; letter-spacing:0.5px;'>TERVERIFIKASI</span>" if confident else f"<span style='color:#DC2626; font-weight:700; font-size:0.68rem; border:1px solid #DC2626; padding:2px 6px; letter-spacing:0.5px;'>KURANG YAKIN</span>"
        
        timeline_html = f'<div style="border: 1px solid #E5E7EB; border-left: 5px solid {color}; padding: 0.8rem 1rem; margin-bottom: 0.6rem; background: #FFFFFF; border-radius: 0px; display: flex; align-items: center; justify-content: space-between;"><div style="display: flex; align-items: center; gap: 0.8rem;">{svg_html}<div><strong style="color:#0F172A; text-transform: uppercase; font-size:0.85rem; letter-spacing:0.5px;">{label} ({source.upper()})</strong><span style="color:#64748B; font-size:0.75rem; margin-left:0.5rem;"> · {conf:.1f}% · {fname} · {ts}</span></div></div><div>{badge_html}</div></div>'
        
        st.markdown(timeline_html, unsafe_allow_html=True)

