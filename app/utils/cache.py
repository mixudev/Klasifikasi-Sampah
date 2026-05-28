"""
cache.py — Manajemen session state untuk history & settings dengan persistensi SQLite database.
"""

import streamlit as st
import sqlite3
import json
import os
from app.config import (
    STATE_SCAN_HISTORY,
    STATE_SETTINGS,
    DEFAULT_CONFIDENCE_THRESHOLD,
    WASTE_MODEL_ID,
    GEMINI_API_KEY,
)

# ─── Default Settings ──────────────────────────────────────────────────────────

# Deteksi lingkungan Streamlit Cloud berdasarkan indikator yang reliabel
IS_STREAMLIT_CLOUD: bool = (
    os.environ.get("STREAMLIT_SHARING_MODE") is not None  # Variabel khusus Streamlit Cloud
    or os.path.exists("/mount/src")                        # Mount point khas Streamlit Cloud
)

# Mode inferensi default: "hugging" (HuggingFace Hub) untuk semua environment
DEFAULT_INFERENCE_MODE = "hugging"

DEFAULT_SETTINGS: dict = {
    "confidence_threshold": DEFAULT_CONFIDENCE_THRESHOLD,
    "model_id":             WASTE_MODEL_ID,
    "light_mode":           False,
    "auto_save_history":    True,
    "inference_mode":       DEFAULT_INFERENCE_MODE,
    "gemini_api_key":       GEMINI_API_KEY,
    "hf_token":             "",  # HuggingFace token untuk akses model private
}

DB_PATH = "waste_db.sqlite"


# ─── SQLite DB Helpers ─────────────────────────────────────────────────────────

def init_db() -> None:
    """Inisialisasi database SQLite untuk history dan settings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buat tabel history jika belum ada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            filename TEXT,
            label TEXT,
            confidence REAL,
            is_confident INTEGER,
            tip TEXT,
            error TEXT,
            source TEXT
        )
    """)
    
    # Buat tabel settings jika belum ada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def get_history_from_db() -> list[dict]:
    """Ambil riwayat scan dari database SQLite, urutkan berdasarkan timestamp DESC."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    history = []
    for row in rows:
        history.append({
            "id":           row["id"],
            "timestamp":    row["timestamp"],
            "filename":     row["filename"],
            "label":        row["label"],
            "confidence":   row["confidence"],
            "is_confident": bool(row["is_confident"]),
            "tip":          row["tip"],
            "error":        row["error"],
            "source":       row["source"],
        })
    conn.close()
    return history


def add_history_to_db(record: dict) -> None:
    """Simpan atau perbarui record history ke database SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO history 
        (id, timestamp, filename, label, confidence, is_confident, tip, error, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("id"),
        record.get("timestamp"),
        record.get("filename"),
        record.get("label"),
        record.get("confidence"),
        1 if record.get("is_confident") else 0,
        record.get("tip"),
        record.get("error"),
        record.get("source"),
    ))
    conn.commit()
    conn.close()


def delete_history_record_from_db(record_id: str) -> None:
    """Hapus satu record dari database SQLite berdasarkan ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def clear_history_in_db() -> None:
    """Kosongkan seluruh data history dari database SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()


def load_settings_from_db() -> dict:
    """Muat seluruh setelan dari database SQLite. Jika kosong, isi dengan DEFAULT_SETTINGS."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    
    settings = DEFAULT_SETTINGS.copy()
    db_keys = []
    for key, value_str in rows:
        try:
            settings[key] = json.loads(value_str)
            db_keys.append(key)
        except Exception:
            pass
            
    # Jika database kosong (belum ada isinya), simpan semua default settings ke DB
    if not db_keys:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for k, v in DEFAULT_SETTINGS.items():
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, json.dumps(v)))
        conn.commit()
        conn.close()
        
    return settings


def update_setting_in_db(key: str, value) -> None:
    """Perbarui satu setelan di database SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()


def reset_settings_in_db() -> None:
    """Kembalikan semua setelan ke default di database SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for k, v in DEFAULT_SETTINGS.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, json.dumps(v)))
    conn.commit()
    conn.close()


# ─── Streamlit Cache & State Bridges ───────────────────────────────────────────

# Mode yang valid di versi baru aplikasi ini
_VALID_MODES = {"hugging", "gemini"}

# Pemetaan mode lama ke mode baru
_LEGACY_MODE_MAP = {
    "local": "hugging",   # Mode lokal dihapus → gunakan HF Hub
    "cloud": "hugging",   # Mode cloud API lama → gunakan HF Hub
}


def _migrate_legacy_settings(settings: dict) -> dict:
    """
    Migrasi pengaturan dari versi lama aplikasi ke versi baru.

    Konversi:
      - inference_mode "local" → "hugging"
      - inference_mode "cloud" → "hugging"
      - Sinkronisasi gemini_api_key dari config.py
      - Hapus key usang (hf_token)
    """
    import importlib
    import app.config as cfg
    importlib.reload(cfg)

    changed = False

    # Konversi mode lama ke mode baru
    current_mode = settings.get("inference_mode", DEFAULT_INFERENCE_MODE)
    if current_mode not in _VALID_MODES:
        new_mode = _LEGACY_MODE_MAP.get(current_mode, DEFAULT_INFERENCE_MODE)
        settings["inference_mode"] = new_mode
        update_setting_in_db("inference_mode", new_mode)
        changed = True

    # Selalu sinkronkan gemini_api_key dari config.py (source of truth)
    if cfg.GEMINI_API_KEY and settings.get("gemini_api_key") != cfg.GEMINI_API_KEY:
        settings["gemini_api_key"] = cfg.GEMINI_API_KEY
        update_setting_in_db("gemini_api_key", cfg.GEMINI_API_KEY)
        changed = True

    if changed:
        import logging
        logging.getLogger(__name__).info("[Cache] Pengaturan lama berhasil dimigrasi.")

    return settings


def init_session_state() -> None:
    """Inisialisasi semua session state yang dibutuhkan aplikasi dari SQLite."""
    init_db()

    # Load riwayat scan
    if STATE_SCAN_HISTORY not in st.session_state:
        st.session_state[STATE_SCAN_HISTORY] = get_history_from_db()

    # Load dan migrasi pengaturan
    if STATE_SETTINGS not in st.session_state:
        loaded = load_settings_from_db()
        st.session_state[STATE_SETTINGS] = _migrate_legacy_settings(loaded)
    else:
        # Tetap sinkronkan Gemini key jika config.py diperbarui
        st.session_state[STATE_SETTINGS] = _migrate_legacy_settings(
            st.session_state[STATE_SETTINGS]
        )


def get_history() -> list[dict]:
    """Ambil riwayat scan dari session state atau database SQLite."""
    if STATE_SCAN_HISTORY not in st.session_state or not st.session_state[STATE_SCAN_HISTORY]:
        st.session_state[STATE_SCAN_HISTORY] = get_history_from_db()
    return st.session_state[STATE_SCAN_HISTORY]


def add_to_history(record: dict) -> None:
    """Tambah record baru ke history (simpan ke SQLite & update session state)."""
    # 1. Simpan ke database SQLite
    add_history_to_db(record)
    # 2. Sinkronkan dengan session state
    st.session_state[STATE_SCAN_HISTORY] = get_history_from_db()[:200]


def clear_history() -> None:
    """Hapus seluruh riwayat scan (dari SQLite & session state)."""
    # 1. Hapus dari database SQLite
    clear_history_in_db()
    # 2. Hapus dari session state
    st.session_state[STATE_SCAN_HISTORY] = []


def get_setting(key: str):
    """Ambil satu nilai setting dari session state."""
    settings = st.session_state.get(STATE_SETTINGS, None)
    if settings is None:
        settings = load_settings_from_db()
        st.session_state[STATE_SETTINGS] = settings
    return settings.get(key, DEFAULT_SETTINGS.get(key))


def update_setting(key: str, value) -> None:
    """Update satu nilai setting (simpan ke SQLite & update session state)."""
    if STATE_SETTINGS not in st.session_state:
        st.session_state[STATE_SETTINGS] = load_settings_from_db()
    st.session_state[STATE_SETTINGS][key] = value
    # Simpan ke database SQLite
    update_setting_in_db(key, value)


def reset_settings() -> None:
    """Reset semua setting ke default (SQLite & session state)."""
    # 1. Reset di SQLite
    reset_settings_in_db()
    # 2. Reset di session state
    st.session_state[STATE_SETTINGS] = DEFAULT_SETTINGS.copy()


# ─── Auth State Persistence (Across Refreshes) ─────────────────────────────────

AUTH_FILE_PATH = ".auth_state"


def save_auth_state(authenticated: bool) -> None:
    """Simpan status autentikasi ke file lokal agar bertahan saat refresh (F5)."""
    try:
        with open(AUTH_FILE_PATH, "w") as f:
            f.write("1" if authenticated else "0")
    except Exception:
        pass


def load_auth_state() -> bool:
    """Muat status autentikasi dari file lokal."""
    if not os.path.exists(AUTH_FILE_PATH):
        return False
    try:
        with open(AUTH_FILE_PATH, "r") as f:
            val = f.read().strip()
            return val == "1"
    except Exception:
        return False
