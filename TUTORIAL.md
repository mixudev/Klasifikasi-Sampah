# Panduan Penggunaan Sistem WasteAI

Dokumen ini berisi panduan lengkap untuk memasang, menjalankan, dan menggunakan aplikasi web WasteAI. Aplikasi ini dirancang menggunakan arsitektur modular reaktif berbasis Streamlit, model HuggingFace Vision Transformer (ViT), dan integrasi model Multimodal Google Gemini 1.5 Flash.

---

## 1. Persyaratan Sistem & Instalasi

Sebelum menjalankan aplikasi, pastikan Anda memiliki Python versi 3.10 atau yang lebih baru terinstal di komputer Anda.

### Langkah 1: Pasang Dependensi
Buka Terminal atau Command Prompt di folder proyek `SAMPAH` Anda, lalu jalankan perintah berikut untuk menginstal semua pustaka yang dibutuhkan:

```bash
pip install -r requirements.txt
```

*Catatan: Dependensi utama meliputi `streamlit`, `transformers`, `torch`, `torchvision`, `pillow`, dan `pandas`.*

---

## 2. Cara Menjalankan Aplikasi

Setelah dependensi berhasil diinstal, jalankan aplikasi web menggunakan perintah Streamlit berikut:

```bash
streamlit run app/main.py
```

Setelah perintah dijalankan, Streamlit akan otomatis membuka tab baru di peramban (browser) Anda dengan alamat default `http://localhost:8501`.

---

## 3. Struktur Antarmuka & 10 Halaman Utama

Aplikasi WasteAI didesain dengan konsep **Minimalist Functional UI / Industrial Look** yang bersih, monokromatik, bersudut tajam (sharp), serta bebas dari dekorasi emoji. Berikut adalah penjelasan fungsi dari 10 menu utama yang tersedia di sidebar kiri:

### 1. Beranda (Landing Page)
Halaman awal yang menyajikan ringkasan visi WasteAI, daftar kategori sampah yang didukung oleh model AI saat ini, serta statistik editorial mengenai urgensi pemilahan sampah di tingkat nasional.

### 2. Scan Sampah (Core Feature)
Fitur pemindaian tunggal yang mendukung dua metode input:
- **Upload Gambar**: Unggah file foto lokal dengan format JPG, PNG, atau WebP.
- **Kamera**: Gunakan kamera/webcam laptop atau ponsel Anda secara langsung untuk memotret objek.
Setelah memotret atau mengunggah, klik tombol **MULAI ANALISIS AI** untuk mendeteksi jenis sampah secara instan.

### 3. Upload Batch (Batch Detection)
Fitur pemindaian massal yang memungkinkan Anda mengunggah hingga 20 berkas gambar sekaligus. Sistem akan memproses seluruh gambar secara berurutan, menampilkan bilah kemajuan (progress bar), memuat tabel ringkasan hasil secara tabular, serta menyediakan tombol unduh **DOWNLOAD HASIL ANALISIS (CSV)**.

### 4. Riwayat (Session History)
Menampilkan seluruh daftar pemindaian yang dilakukan pada sesi aktif. Menampilkan visualisasi linimasa tajam dengan ikon SVG monokromatik penanda jenis sampah, tingkat keyakinan (confidence score), penanda verifikasi threshold, serta opsi **EXPORT CSV** dan **HAPUS SEMUA**.

### 5. Analytics (Statistik Visual)
Visualisasi grafis reaktif dari seluruh data pemindaian sesi ini menggunakan:
- Kartu statistik metrik utama (Rata-rata keyakinan, Kategori dominan, dan Rasio terverifikasi).
- Grafik batang distribusi frekuensi sampah per kategori.
- Grafik batang sebaran interval keyakinan prediksi.

### 6. Manajemen Data (CRUD Interface)
Antarmuka manajemen database sesi terintegrasi yang mencakup kemampuan:
- **Daftar Data**: Menyaring tabel riwayat berdasarkan kategori tertentu dan mengunduh data saringan.
- **Tambah Data**: Menginput catatan scan secara manual (Create) untuk keperluan pengujian.
- **Edit / Hapus Data**: Memilih record tertentu berdasarkan ID untuk memperbarui label/skor keyakinan (Update) atau menghapusnya secara permanen dari database lokal (Delete).

### 7. Dataset Explorer (Model & Data Info)
Halaman edukasi teknis yang menjelaskan metadata dataset pelatihan asli model AI (Garbage Classification Dataset), rincian jumlah gambar per kelas, metrik akurasi F1-Score model, serta analisis potensi bias klasifikasi (seperti bias bentuk hancur dan ketidakseimbangan data B3).

### 8. Panduan Pengguna (Tutorial)
Tutorial visual detail mengenai cara mengambil foto sampah yang benar agar mendapatkan akurasi klasifikasi AI tertinggi. Halaman ini menyediakan tabel komparasi **DO (Rekomendasi)** dan **DON'T (Hindari)** yang disajikan secara berdampingan.

### 9. Tentang Aplikasi (Tech Stack & Disclaimer)
Halaman profil proyek yang memuat stack arsitektur teknologi yang digunakan, misi ekologi WasteAI, serta batasan hukum resmi (Disclaimer) mengenai hasil analisis kecerdasan buatan.

### 10. Pengaturan (Settings & Config)
Pusat kontrol sistem yang menyediakan:
- **Mode Inferensi**: Memilih pemrosesan AI secara **Lokal (Offline)**, **Hugging Face Cloud (API)**, atau **Google Gemini AI (Multimodal)** untuk analisis instan super akurat.
- **Gemini API Key**: Kolom input untuk kunci API Google Gemini Anda.
- **HF User Token**: Memasukkan Token Hugging Face gratis Anda agar kueri API cloud berjalan tanpa terkena batasan kuota.
- **Slider Confidence Threshold**: Menentukan batas tingkat keyakinan minimum (default 60%). Jika hasil AI di bawah batas ini, sistem akan memberikan peringatan 'Kurang Yakin' (Low Confidence).
- **Pemilihan Model**: Mengubah model inferensi antara model ViT spesifik sampah atau model generic ViT sebagai fallback (khusus mode Lokal/HF Cloud).
- **Tindakan Pembersihan**: Tombol pintas untuk mengosongkan riwayat sesi, mereset semua setting, atau membersihkan memori cache model AI.

---

## 4. Cara Mengaktifkan Mode Google Gemini AI (Sangat Akurat & Ringan)

Mode ini menggunakan teknologi VLM (Vision Language Model) **Gemini 1.5 Flash** dari Google. Dengan memanfaatkan kemampuan pemahaman visual tingkat lanjut, AI dapat menganalisis dan mengelompokkan jenis sampah secara instan dan sangat presisi tanpa perlu mengunduh file model lokal apa pun.

Langkah-langkah aktivasi:
1. Buka menu **Pengaturan** di sidebar kiri.
2. Pada bagian **Mode Inferensi (Pemrosesan AI)**, pilih opsi **Google Gemini AI (Multimodal - Instan, Sangat Cerdas & Presisi Tinggi)**.
3. Dapatkan API Key gratis Anda dengan mendaftar di [Google AI Studio (aistudio.google.com)](https://aistudio.google.com).
4. Buat kunci API baru secara gratis pada menu **Get API Key**.
5. Tempelkan kunci tersebut pada kolom **Google Gemini API Key** di halaman Pengaturan aplikasi Anda.
6. Selesai! Sekarang Anda dapat melakukan scan di halaman **Scan Sampah** secara instan dan akurat.

---

## 5. Panduan Pemanggilan File Model di Hugging Face (Developer Tutorial)

Hugging Face mempermudah developer untuk memanggil model machine learning baik secara lokal maupun menggunakan infrastruktur server cloud (Serverless API). Berikut adalah 2 cara utama untuk memanggil file model:

### Metode A: Memanggil via Cloud Serverless API (Menggunakan HTTP Request)
Metode ini adalah metode yang digunakan pada mode Cloud WasteAI. Anda tidak perlu mengunduh file model, cukup mengirimkan data biner gambar langsung ke endpoint model Hugging Face.

#### Contoh Kode Python (Tanpa Download Model):
```python
import requests

# 1. Definisikan ID Model Hugging Face dan token Anda
MODEL_ID = "wayfarer130/garbage-classification-vit"
HF_TOKEN = "isi_dengan_hf_token_gratis_anda"  # Dapatkan di huggingface.co/settings/tokens

# 2. Definisikan endpoint API kueri Hugging Face
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_model_from_cloud(image_path: str):
    # 3. Baca gambar dalam format biner (bytes)
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    
    # 4. Kirim permintaan POST ke server Hugging Face
    response = requests.post(API_URL, headers=headers, data=img_bytes)
    
    # 5. Dapatkan hasil respons JSON
    if response.status_code == 200:
        return response.json() # Mengembalikan list tingkat keyakinan per kelas
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")

# Uji coba kueri cloud
hasil = query_model_from_cloud("sampah_plastik.jpg")
print(hasil)
```

### Metode B: Memanggil via Local Pipeline (Mengunduh Model ke Komputer Lokal)
Metode ini mengunduh seluruh bobot file model (seperti `.safetensors` atau `.bin`) dari Hugging Face Hub saat dijalankan pertama kali, kemudian mengeksekusinya di CPU/GPU komputer lokal secara offline.

#### Contoh Kode Python (Mengunduh & Eksekusi Lokal):
```python
from transformers import pipeline
from PIL import Image

# 1. Tentukan ID Model Hugging Face yang ingin diunduh
MODEL_ID = "wayfarer130/garbage-classification-vit"

# 2. Buat objek pipeline klasifikasi citra
classifier = pipeline(
    task="image-classification",
    model=MODEL_ID,
    device=-1  # Set -1 untuk CPU, atau 0 untuk kartu grafis Nvidia (CUDA)
)

def query_model_locally(image_path: str):
    # 3. Buka gambar menggunakan Pillow
    img = Image.open(image_path)
    
    # 4. Jalankan inferensi pada CPU lokal
    results = classifier(img)
    return results

# Uji coba inferensi lokal offline
hasil_lokal = query_model_locally("sampah_plastik.jpg")
print(hasil_lokal)
```

---

## 6. Panduan Pemanggilan Google Gemini API Menggunakan Image Input (Developer Tutorial)

Untuk menggunakan Google Gemini sebagai AI pemilah sampah dengan visual prompting yang membatasi hasil menjadi satu kata kunci (seperti Kaca, Plastik, dll.), Anda dapat mengirimkan permintaan HTTP terstruktur ke API Google Generative Language menggunakan format JSON.

#### Contoh Kode Python Menggunakan `requests` (Metode Ringan Tanpa SDK Berat):
```python
import requests
import base64

# 1. Definisikan Kunci API Gemini Anda
GEMINI_API_KEY = "isi_dengan_api_key_studio_anda"  # Dapatkan di aistudio.google.com

# 2. Endpoint kueri model gemini-1.5-flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def encode_image_to_base64(image_path: str) -> str:
    """Mengubah file gambar lokal menjadi string base64 untuk pengiriman API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def klasifikasikan_dengan_gemini(image_path: str):
    # 3. Konversi gambar ke base64
    img_b64 = encode_image_to_base64(image_path)
    
    # 4. Susun visual prompt ketat agar AI hanya memprediksi satu kata terstruktur
    prompt = (
        "Klasifikasikan jenis material sampah dari gambar ini.\n"
        "Pilihan kategori yang valid: Organik, Plastik, Kertas, Kaca, Logam, B3 (Berbahaya).\n"
        "Kembalikan respons wajib berupa format JSON mentah.\n"
        "Skema JSON yang harus Anda kembalikan secara tepat:\n"
        "{\n"
        "  \"label\": \"salah satu kata kategori di atas secara tepat\",\n"
        "  \"confidence\": angka desimal keyakinan antara 0.0 sampai 1.0\n"
        "}"
    )
    
    # 5. Susun payload JSON multimodal
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    # 6. Kirim permintaan POST ke server Google
    response = requests.post(API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        res_json = response.json()
        text_out = res_json["candidates"][0]["content"]["parts"][0]["text"]
        
        # Parse hasil string JSON dari Gemini menjadi objek Python
        import json
        return json.loads(text_out.strip())
    else:
        raise ValueError(f"Gagal memanggil Gemini API: {response.text}")

# Uji coba kueri Gemini
hasil_gemini = klasifikasikan_dengan_gemini("sampah_kaca.jpg")
print(hasil_gemini)
# Output: {'label': 'Kaca', 'confidence': 0.98}
```
---

## 7. Tips Pengambilan Foto untuk Akurasi Maksimal

Model AI mendeteksi sampah berdasarkan karakteristik visual luar. Ikuti pedoman berikut agar hasil klasifikasi akurat:

1. **Jarak yang Pas**: Tempatkan objek sampah sekitar 30 - 50 cm di depan kamera. Objek yang terlalu jauh atau terlalu dekat akan kehilangan bentuk dasarnya.
2. **Pencahayaan Terang**: Ambil foto di ruangan dengan cahaya yang cukup dan merata. Hindari bayangan tebal yang menyelimuti objek.
3. **Objek Tunggal**: Jangan memotret tumpukan sampah campuran. Model AI bekerja optimal dengan mengidentifikasi satu objek sampah dominan dalam satu gambar.
4. **Kebersihan Objek**: Kosongkan wadah botol plastik atau kaca dari sisa cairan berwarna tebal untuk mempermudah AI mengenali karakteristik fisik wadah tersebut.
