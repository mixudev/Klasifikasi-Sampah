# 🤗 Panduan HuggingFace Token - WasteAI

## Apa itu HuggingFace Token?

HuggingFace Token adalah kunci autentikasi yang memungkinkan Anda:
- ✅ Mengakses model **private** yang Anda miliki
- ✅ Menggunakan model dengan akses terbatas
- ✅ Bypass rate limiting untuk model publik
- ✅ Download model dengan quota lebih tinggi

---

## 📋 Cara Mendapatkan Token

### 1. Buka HuggingFace Settings
- Kunjungi: https://huggingface.co/settings/tokens
- Login dengan akun HuggingFace Anda (atau buat akun gratis)

### 2. Create New Token
- Klik **"New token"**
- Isi deskripsi: `WasteAI Streamlit` (atau nama lain)
- Pilih akses: **Read** (cukup untuk download model)
- Klik **Create token**

### 3. Copy Token
- Token akan terlihat seperti: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **JANGAN** share token ini ke orang lain!

---

## 🔧 Cara Menggunakan Token di WasteAI

### Opsi 1: Via Interface Streamlit (Recommended)

1. **Buka aplikasi WasteAI**
2. **Pergi ke halaman "Pengaturan Sistem"** (sidebar)
3. **Scroll ke bagian "Konfigurasi Model Hugging Face Hub"**
4. **Di bawah "Model ID", cari section "Token Autentikasi (opsional)"**
5. **Paste token Anda di field "HuggingFace API Token"**
6. **Token disimpan otomatis** ✅

### Opsi 2: Konfigurasi Manual (Environment Variable)

Jika Anda deploy di Streamlit Cloud atau local server:

```bash
# Streamlit Cloud — tambahkan di .streamlit/secrets.toml:
hf_token = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Atau set environment variable sebelum run:
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
streamlit run app/main.py

# Windows PowerShell:
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
streamlit run app/main.py
```

---

## 💡 Kasus Penggunaan

### ✅ Akses Model Private Milik Sendiri
Jika Anda memiliki model private di HuggingFace:
```
Pengaturan → Model ID = "username/private-model-name"
Tambahkan token → Model langsung bisa diakses
```

### ✅ Menggunakan Model dengan Access Request
Beberapa model memerlukan persetujuan akses (BLOOM, LLaMA, dll):
```
1. Kunjungi halaman model di huggingface.co
2. Klik "Access repository" & tunggu approval
3. Generate token dengan akses Read
4. Masukkan token di WasteAI settings
```

### ✅ Bypass Rate Limiting
Model publik juga memiliki rate limit:
- Tanpa token: ~30 requests/hari
- Dengan token: ~1000 requests/hari (lebih tinggi)

---

## 🔒 Keamanan Token

### Best Practices

1. **Gunakan Token Khusus**
   - Buat token terpisah untuk setiap aplikasi
   - Jangan reuse token production di lingkungan development

2. **Scope Token Ke Repository**
   - Jika memungkinkan, pilih "Read" bukan "Write"
   - Batasi akses hanya ke repository tertentu

3. **Simpan Aman**
   - Di Streamlit Cloud: gunakan `secrets.toml`
   - Di local: jangan commit `.env` ke git
   - Jangan paste token di public code

4. **Revoke Token Jika Diperlukan**
   - Pergi ke https://huggingface.co/settings/tokens
   - Klik "Delete" untuk token yang tidak terpakai
   - Token lama akan langsung tidak bisa digunakan

### Di WasteAI

- Token disimpan di database lokal terenkripsi
- **Tidak pernah dikirim ke server eksternal**
- Hanya digunakan untuk autentikasi ke HuggingFace Hub
- Anda bisa kapan saja menghapus token di halaman Settings

---

## 🚀 Deployment di Streamlit Cloud

### Setup Token di Streamlit Cloud

1. **Push kode ke GitHub**
2. **Buka Streamlit Cloud**: https://share.streamlit.io/
3. **Deploy aplikasi**
4. **Klik app → Settings (gear icon)**
5. **Scroll ke "Secrets"** dan paste:
   ```toml
   hf_token = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
6. **Deploy/Rerun** - token akan langsung aktif

**Catatan:** Token di `secrets.toml` bisa langsung diakses via `st.secrets.get("hf_token")`

Jika ingin menggunakan fitur UI Settings:
- Biarkan kosong di `secrets.toml`
- User bisa input token langsung di halaman Settings
- Token disimpan di database aplikasi

---

## ❌ Troubleshooting

### Error: "Invalid token or repo not found"
**Solusi:**
- Copy ulang token dari https://huggingface.co/settings/tokens
- Pastikan token tidak ada spasi di awal/akhir
- Pastikan Anda punya akses ke model tersebut

### Error: "AuthenticationError"
**Solusi:**
- Token sudah expire atau dihapus
- Buat token baru di https://huggingface.co/settings/tokens
- Pastikan token memiliki akses Read

### Model masih tidak bisa dimuat meski ada token
**Solusi:**
- Model mungkin memerlukan approval khusus
- Kunjungi halaman model dan klik "Access repository"
- Tunggu approval dari pemilik model
- Refresh browser dan coba lagi

### "Connection timeout" saat download model
**Solusi:**
- Koneksi internet lambat/tidak stabil
- Coba ulang: Settings → Hapus Cache Model
- Atau gunakan mode Google Gemini sementara

---

## 📚 Referensi

- **HuggingFace Docs**: https://huggingface.co/docs
- **Token Management**: https://huggingface.co/settings/tokens
- **Model Hub**: https://huggingface.co/models
- **Transformers Library**: https://huggingface.co/docs/transformers

---

## 💬 Pertanyaan?

Jika ada masalah:
1. Baca **DEPLOYMENT.md** untuk troubleshooting umum
2. Cek **logs** di Streamlit (Ctrl+I untuk developer console)
3. Pastikan koneksi internet stabil
4. Coba Settings → Reset Semua Pengaturan

**Happy classifying! 🗑️✨**
