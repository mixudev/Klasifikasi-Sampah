"""
download_model.py — Script untuk download model HuggingFace secara offline
Jalankan ini SEBELUM streamlit app untuk cache model locally.
"""

import os
from huggingface_hub import snapshot_download
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from app.config import WASTE_MODEL_ID, HF_MODEL_ID

def download_models():
    """Download dan cache kedua model ke local storage."""
    
    models = [WASTE_MODEL_ID, HF_MODEL_ID]
    
    for model_id in models:
        print(f"\n{'='*60}")
        print(f"📥 Downloading: {model_id}")
        print(f"{'='*60}")
        
        try:
            # Download model repo
            snapshot_download(repo_id=model_id)
            
            # Pre-load model & feature extractor untuk warm cache
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_id)
            model = AutoModelForImageClassification.from_pretrained(model_id)
            
            print(f"✅ Berhasil download & cache: {model_id}")
            
        except Exception as e:
            print(f"❌ Gagal download {model_id}: {e}")
            print(f"   Pastikan ada koneksi internet & model ID valid")

if __name__ == "__main__":
    print("🤖 WasteAI Model Downloader")
    print("Ini akan download & cache model ke folder local HuggingFace")
    download_models()
    print("\n✨ Selesai! Sekarang jalankan: streamlit run app/main.py")
