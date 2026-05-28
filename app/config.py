"""
config.py — Konfigurasi global aplikasi WasteAI
Semua konstanta, setting model, dan parameter default dipusatkan di sini.
"""

# ──────────────────────────────────────────
# APP META
# ──────────────────────────────────────────
APP_NAME = "WasteAI"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Klasifikasi Sampah Cerdas Berbasis AI"

# ⚠️ SECURITY WARNING: JANGAN hardcode API Key di file ini!
# Gunakan environment variables atau .streamlit/secrets.toml
# Baca DEPLOYMENT.md untuk setup yang aman.
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ──────────────────────────────────────────
# MODEL CONFIG
# ──────────────────────────────────────────
# Model diambil dari HuggingFace — tidak disimpan di repo
HF_MODEL_ID = "google/vit-base-patch16-224"   # default; ganti ke model sampah jika tersedia
WASTE_MODEL_ID = "wayfarer130/garbage-classification-vit"  # model spesifik sampah

# Class labels (sesuai model)
WASTE_CLASSES = [
    "Organik",
    "Plastik",
    "Kertas",
    "Kaca",
    "Logam",
    "B3 (Berbahaya)",
]

# Warna per kelas untuk UI (Tailwind HSL tailored professional palette)
CLASS_COLORS = {
    "Organik":       "#16A34A", # Green AI / Eco
    "Plastik":       "#2563EB", # Blue
    "Kertas":        "#4B5563", # Gray
    "Kaca":          "#0D9488", # Teal
    "Logam":         "#475569", # Slate
    "B3 (Berbahaya)":"#DC2626", # Red
}

# ──────────────────────────────────────────
# PREDICTION CONFIG
# ──────────────────────────────────────────
DEFAULT_CONFIDENCE_THRESHOLD = 0.60   # 60%
IMAGE_SIZE = (224, 224)
MAX_BATCH_UPLOAD = 20                  # maks gambar batch upload

# ──────────────────────────────────────────
# EDUCATION / SARAN PENANGANAN
# ──────────────────────────────────────────
HANDLING_TIPS = {
    "Organik": (
        "Masukkan ke tempat sampah organik (hijau). "
        "Ideal untuk dijadikan kompos. Pisahkan dari sampah lain untuk mencegah pembusukan basah."
    ),
    "Plastik": (
        "Pilah berdasarkan kode daur ulang plastik (#1–#7). "
        "Bersihkan wadah dari sisa cairan atau makanan sebelum dibuang ke bank sampah."
    ),
    "Kertas": (
        "Kumpulkan dalam keadaan kering dan rata, lalu jual ke bank sampah. "
        "Hindari membuang kertas basah atau berminyak karena merusak serat daur ulang."
    ),
    "Kaca": (
        "Bungkus pecahan kaca dengan kertas tebal atau karton sebelum dibuang agar tidak melukai petugas kebersihan. "
        "Botol utuh dapat dicuci dan digunakan kembali atau didaur ulang."
    ),
    "Logam": (
        "Kaleng dan besi memiliki nilai ekonomi tinggi. Bersihkan, pipihkan (jika bisa), "
        "dan kumpulkan untuk dijual ke pengepul logam atau bank sampah."
    ),
    "B3 (Berbahaya)": (
        "JANGAN dibuang ke tempat sampah biasa! Kumpulkan batu baterai, lampu bekas, "
        "atau kemasan aerosol secara terpisah dan bawa ke titik pengumpulan B3 resmi Dinas Lingkungan Hidup."
    ),
}

# ──────────────────────────────────────────
# SESSION STATE KEYS
# ──────────────────────────────────────────
STATE_SCAN_HISTORY   = "scan_history"
STATE_SETTINGS       = "app_settings"
STATE_CURRENT_PAGE   = "current_page"

# ──────────────────────────────────────────
# PAGES (Bebas dari Emoji sesuai dengan UI_ROLE.md)
# ──────────────────────────────────────────
PAGES = {
    "Beranda":           "landing",
    "Scan Sampah":       "scan",
    "Upload Batch":      "upload",
    "Riwayat":           "history",
    "Analytics":         "analytics",
    "Manajemen Data":    "data_manager",
    "Dataset":           "dataset",
    "Tutorial":          "tutorial",
    "Tentang":           "about",
    "Pengaturan":        "settings",
}
