# 🚀 Deploy ke Streamlit Cloud

## Solusi untuk Network Issues di Streamlit Cloud

Streamlit Cloud memiliki **network restrictions yang ketat**. Jika model loading gagal di cloud, ada beberapa solusi:

### ✅ Solusi 1: Tunggu & Refresh (Recommended untuk First Run)

Saat pertama kali deploy:
1. Streamlit Cloud akan try download model secara otomatis
2. **First run bisa slow** (5-10 menit tergantung model size)
3. Subsequent runs akan cepat karena model sudah di-cache
4. Jika timeout, refresh halaman → retry otomatis

**Direkomendasikan:**
- Deploy dulu
- Tunggu 10-15 menit untuk first initialization
- Jangan close tab browser

---

### ⚡ Solusi 2: Pre-Cache Model (untuk Development)

Untuk testing local sebelum deploy ke cloud:

```bash
# 1. Download model ke local cache
python download_model.py

# 2. Test di local
streamlit run app/main.py

# 3. Push ke GitHub & deploy
git add .
git commit -m "Pre-cache models"
git push
```

Keuntungan:
- Model sudah cached
- Testing local berjalan smooth
- Deploy ke cloud juga akan smooth

---

### 🔧 Solusi 3: Mengubah Model ke yang Lebih Ringan

Edit `app/config.py`:

```python
# Dari model berat (garbage-classification)
WASTE_MODEL_ID = "wayfarer130/garbage-classification-vit"

# Ke model ringan (bisa download lebih cepat)
WASTE_MODEL_ID = "google/vit-base-patch16-224"
```

Atau gunakan model DistilBERT-based yang lebih kecil.

---

### 🌐 Setup Streamlit Cloud

1. **Push ke GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud support"
   git push origin main
   ```

2. **Ke https://share.streamlit.io/**
   - Login dengan GitHub
   - Click "Deploy an app"
   - Select repository & branch
   - Main file: `app/main.py`
   - Click Deploy

3. **Tunggu Installation**
   - Streamlit akan install dependencies dari `requirements.txt`
   - Model akan auto-download on first run
   - **Biarkan 10-15 menit untuk first initialization**

4. **Done!**
   - Subsequent runs akan cepat
   - Share URL ke teman

---

## 📋 Checklist Sebelum Deploy

- ✅ `.gitignore` sudah di-commit (exclude `.cache/` & model files)
- ✅ `requirements.txt` up-to-date
- ✅ `app/main.py` sudah siap
- ✅ GitHub repo public atau private (sesuai preference)
- ✅ Test local dulu: `streamlit run app/main.py`

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|--------|--------|
| "Model not found" | Tunggu 10 menit, refresh halaman |
| Timeout error | Model terlalu besar, ubah ke model ringan |
| Network error | Retry otomatis, biarkan 2-3 menit |
| Memory full | Streamlit Cloud limit 1GB RAM; optimasi model |

---

## 💡 Tips

- **First deployment biasanya slow** - ini normal, tunggu aja
- **Subsequent access akan super cepat** - model sudah cached
- **Model di-cache per deployment** - jika redeploy, cache ulang
- **Sharing URL:** Streamlit auto-generate URL public untuk share ke orang lain

Enjoy! 🎉
