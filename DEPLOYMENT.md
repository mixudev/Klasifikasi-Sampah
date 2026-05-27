# 🚀 Deploy ke Streamlit Cloud

## Panduan Lengkap Deployment & Troubleshooting

### ✅ Quick Start

1. **Push ke GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy di Streamlit Cloud**
   - Buka https://share.streamlit.io/
   - Login dengan GitHub
   - Deploy → pilih repo → main.py
   - **Tunggu 15-20 menit untuk first run**

3. **Done!** Akses URL yang diberikan

---

## 🔍 Troubleshooting: "Model Loading Failed"

### Penyebab & Solusi

#### 1️⃣ **First Deployment - Model sedang download**
**Status:** ⏳ Normal, ini expected!
- Model ~1.2GB, butuh waktu
- **Solusi:** Tunggu 10-15 menit, kemudian refresh browser

**Progress:**
```
1-2 min   : Install dependencies
3-5 min   : Connect to HuggingFace
5-15 min  : Download model (~1.2GB)
15+ min   : Ready to use ✅
```

#### 2️⃣ **Network Timeout/Slow Connection**
**Error:** `HTTPSConnectionPool`, `NameResolutionError`, `timeout`
- HuggingFace API sedang slow atau connection unstable
- **Solusi:**
  ```
  ✅ Refresh halaman & tunggu 5 menit
  ✅ Coba Settings → Reset Cache Model
  ✅ Atau gunakan Google Gemini sebagai alternatif
  ```

#### 3️⃣ **Memory Insufficient**
**Error:** Memory allocation error saat download
- Streamlit Cloud resource limitation
- **Solusi:**
  - ✅ Deploy sebagai private app (less resource sharing)
  - ✅ Atau gunakan lebih lightweight model di `config.py`
  - ✅ Atau switch ke Google Gemini

#### 4️⃣ **Model Sudah Cache, tapi Error saat Predict**
**Status:** Model load OK, tapi fail saat prediksi
- **Cek di Settings:**
  - Inference Mode: **Lokal (Offline)** ✅
  - Atau switch ke **Google Gemini** jika ada API key
- **Reset:** Settings → Reset Cache Model

---

## 💡 Best Practices

### ✅ Untuk Streamlit Cloud Success

1. **First Time Setup (Hanya 1x)**
   - Tunggu full 15-20 menit
   - Jangan close browser
   - Jangan reload berkali-kali

2. **Persistent Cache**
   - Model di-cache di Streamlit workspace
   - Subsequent runs: 2-3 detik saja
   - Auto re-download jika workspace reset

3. **Backup Mode: Google Gemini**
   - Settings → Pilih "Google Gemini AI"
   - Input API Key (gratis dari aistudio.google.com)
   - Bisa digunakan sebagai fallback

### ❌ Jangan

- ❌ Jalankan `download_model.py` di cloud (tidak perlu)
- ❌ Ubah model ID saat deployment (need re-download)
- ❌ Upload model files ke repo (terlalu besar, gunakan `.gitignore`)

---

## 📋 Environment Details

### Streamlit Cloud Specifications

| Aspect | Limit |
|--------|-------|
| Memory | 1 GB |
| Storage | 1 GB workspace |
| CPU | Shared |
| Timeout (first run) | 15 min |
| File upload | 200 MB |

### Model Specifications

| Model | Size | Time |
|-------|------|------|
| `wayfarer130/garbage-classification-vit` | ~343 MB | 5-10 min |
| `google/vit-base-patch16-224` | ~346 MB | 5-10 min |
| **Total Cache** | ~700 MB | Fits in 1GB |

---

## 🆘 Still Having Issues?

### Debug Steps

1. **Check Settings**
   - Go to Settings page
   - Note the inference mode
   - Check if it's matching your selection

2. **Reset Everything**
   ```
   Settings → Reset Cache Model → Re-open app
   Tunggu 5 menit, kemudian coba upload gambar
   ```

3. **Check Logs**
   - Streamlit Cloud → View logs
   - Search for "Model loaded" atau error message
   - Copy error & debug

4. **Try Gemini Alternative**
   - Settings → Pilih "Google Gemini AI"
   - Masukkan API Key
   - Test dengan Gemini

### Contact Support
- GitHub Issues: report di repo Anda
- Streamlit Docs: https://docs.streamlit.io/
- HuggingFace Docs: https://huggingface.co/docs/

---

## 📚 Additional Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud/get-started)
- [HuggingFace Model Hub](https://huggingface.co/models)
- [Google Gemini API](https://aistudio.google.com)
- [Our GitHub Repo](https://github.com/mixudev/klasifikasi-sampah)

---

## ✨ Expected Behavior

**First Deployment:**
```
Deploy → Install → Download Model → First Prediction
   ↓        ↓          ↓                    ↓
  1 min   2-3 min    5-10 min          2-3 sec total
```

**Subsequent Access:**
```
Open App → Load cached Model → Predict
   ↓          ↓                  ↓
 30 sec    1-2 sec            2-3 sec total
```

**Result:** Fast, offline, reliable! 🎉
