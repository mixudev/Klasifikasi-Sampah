"""
data_manager.py — Halaman 3: Manajemen Data (CRUD).
Memungkinkan pengelolaan data riwayat scan sesi ini secara interaktif.
Bebas emoji dan sudut membulat sesuai UI_ROLE.md.
"""

import streamlit as st
import datetime
import uuid
from app.utils.cache import get_history, get_setting
from app.config import WASTE_CLASSES, STATE_SCAN_HISTORY
from app.services.postprocessing import export_to_csv, records_to_dataframe


def delete_record(record_id: str) -> None:
    """Hapus satu record berdasarkan ID."""
    from app.utils.cache import delete_history_record_from_db
    # 1. Hapus dari database SQLite
    delete_history_record_from_db(record_id)
    # 2. Sinkronkan ke session state
    st.session_state[STATE_SCAN_HISTORY] = [r for r in st.session_state[STATE_SCAN_HISTORY] if r.get("id") != record_id]


def update_record(record_id: str, new_label: str, new_conf: float) -> None:
    """Update label dan confidence record berdasarkan ID."""
    history = get_history()
    threshold = get_setting("confidence_threshold")
    for r in history:
        if r.get("id") == record_id:
            r["label"] = new_label
            r["confidence"] = round(new_conf, 2)
            r["is_confident"] = (new_conf / 100.0) >= threshold
            
            # 1. Perbarui di database SQLite
            from app.utils.cache import add_history_to_db
            add_history_to_db(r)
            break
    # 2. Sinkronkan ke session state
    st.session_state[STATE_SCAN_HISTORY] = history


def add_record(filename: str, label: str, conf: float) -> None:
    """Tambah record baru secara manual."""
    history = get_history()
    threshold = get_setting("confidence_threshold")
    record = {
        "id":         str(uuid.uuid4())[:8],
        "timestamp":  datetime.datetime.now().isoformat(timespec="seconds"),
        "filename":   filename,
        "label":      label,
        "confidence": round(conf, 2),
        "is_confident": (conf / 100.0) >= threshold,
        "tip":        f"Data dimasukkan secara manual.",
        "error":      None,
        "source":     "L",
    }
    # 1. Simpan ke database SQLite
    from app.utils.cache import add_history_to_db
    add_history_to_db(record)
    # 2. Sinkronkan ke session state
    history.insert(0, record)
    st.session_state[STATE_SCAN_HISTORY] = history[:200]


def render() -> None:
    st.title("Manajemen Data")
    st.caption("Kelola, saring, tambah, atau perbarui data riwayat hasil scan secara lokal.")

    history = get_history()

    # ── TAB LAYOUT (CRUD) ─────────────────────────────────────────────────────
    tab_list, tab_add, tab_edit = st.tabs(["Daftar Data", "Tambah Data Manual", "Edit / Hapus Data"])

    # 1. TAB DAFTAR DATA
    with tab_list:
        if not history:
            st.info("Belum ada data riwayat yang tersimpan.")
        else:
            # Filter berdasarkan kelas
            col_filter, col_csv = st.columns([2, 1])
            with col_filter:
                selected_class = st.selectbox("Saring Berdasarkan Kategori", ["Semua Kategori"] + WASTE_CLASSES)
            
            filtered_history = history
            if selected_class != "Semua Kategori":
                filtered_history = [r for r in history if r.get("label") == selected_class]

            # Tampilkan dalam bentuk Pandas DataFrame (Industrial Look)
            df = records_to_dataframe(filtered_history)
            
            # Format display headers
            display_cols = ["id", "timestamp", "filename", "label", "confidence", "is_confident", "source"]
            df_display = df[[c for c in display_cols if c in df.columns]].copy()
            df_display.columns = [c.upper() for c in df_display.columns]

            st.dataframe(df_display, use_container_width=True)

            # Export CSV
            with col_csv:
                st.markdown("<br>", unsafe_allow_html=True)
                csv_data = export_to_csv(filtered_history)
                st.download_button(
                    label="DOWNLOAD DATA CSV",
                    data=csv_data,
                    file_name="riwayat_filtered.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # 2. TAB TAMBAH DATA MANUAL
    with tab_add:
        st.markdown("##### INPUT CATATAN SCAN BARU")
        with st.form("form_add_manual"):
            add_filename = st.text_input("Nama File", value="manual_record.jpg")
            add_label = st.selectbox("Kategori Sampah", WASTE_CLASSES)
            add_conf = st.slider("Confidence Level (%)", min_value=0.0, max_value=100.0, value=90.0, step=0.1)
            
            submit_btn = st.form_submit_button("SIMPAN CATATAN", type="primary")
            if submit_btn:
                if not add_filename.strip():
                    st.error("Nama file tidak boleh kosong.")
                else:
                    add_record(add_filename.strip(), add_label, add_conf)
                    st.success("Catatan baru berhasil ditambahkan.")
                    st.rerun()

    # 3. TAB EDIT / HAPUS DATA
    with tab_edit:
        if not history:
            st.info("Belum ada data untuk diedit atau dihapus.")
        else:
            st.markdown("##### EDIT ATAU HAPUS DATA PEMINDAIAN")
            
            # Pilihan record berdasarkan ID & Filename
            record_options = {f"{r['id']} - {r['filename']} ({r['label']})": r['id'] for r in history}
            selected_record_label = st.selectbox("Pilih Record", list(record_options.keys()))
            selected_id = record_options[selected_record_label]

            # Ambil record saat ini
            current_record = next(r for r in history if r['id'] == selected_id)

            col_edit_fields, col_actions = st.columns(2)

            with col_edit_fields:
                st.markdown("**Perbarui Data:**")
                safe_index = WASTE_CLASSES.index(current_record['label']) if current_record['label'] in WASTE_CLASSES else 0
                new_label = st.selectbox("Kategori Baru", WASTE_CLASSES, index=safe_index)
                new_conf = st.slider("Confidence Baru (%)", min_value=0.0, max_value=100.0, value=float(current_record['confidence']), step=0.1)
                
                if st.button("TERAPKAN PERUBAHAN", type="primary", use_container_width=True):
                    update_record(selected_id, new_label, new_conf)
                    st.success(f"Record {selected_id} berhasil diperbarui.")
                    st.rerun()

            with col_actions:
                st.markdown("**Tindakan Destruktif:**")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("HAPUS RECORD INI", type="secondary", use_container_width=True):
                    delete_record(selected_id)
                    st.success(f"Record {selected_id} berhasil dihapus.")
                    st.rerun()
