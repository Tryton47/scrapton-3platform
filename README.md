# Social Media Scraper (Instagram, TikTok, X)

Scraper modular anti-deteksi berbasis Python (Playwright) untuk mengekstrak profil, video, feed, dan metrik interaksi dari Instagram, TikTok, dan X (Twitter).

## 🚀 Fitur Utama

- **Unified Schema**: Model data seragam (Pydantic) untuk ketiga platform.
- **Stealth Browser Architecture**: Dukungan Playwright dengan bypass deteksi bot & manajemen session/cookies.
- **Multi-Format Export**: Ekspor otomatis ke JSON, CSV, dan database SQLite lokal.
- **Human Emulation**: Algoritma random delay dan scrolling alami untuk meminimalisir risiko rate-limit atau shadowban.

## 📁 Struktur Direktori

```text
.
├── config/             # Pengaturan terpusat & env parser
├── core/               # Unified models, storage exporter, browser manager
├── scrapers/           # Engine scraper spesifik tiap platform
├── data/               # Output hasil scraping (JSON/CSV/DB)
├── sessions/           # Penyimpanan sesi & cookies akun
├── main.py             # CLI entry-point
└── requirements.txt    # Daftar dependensi Python
```

## 🛠️ Instalasi & Menjalankan

1. Buat virtual environment dan install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Cek status konfigurasi:
   ```bash
   python main.py --status
   ```

3. Jalankan scraping (contoh):
   ```bash
   python main.py --platform instagram --username target_user --format json
   ```

### 🎵 Cara Pakai TikTok Scraper

1. Simpan sesi / cookie TikTok sekali (opsional namun disarankan):
   ```bash
   python main.py --login-tiktok
   ```

2. Jalankan scraper video TikTok:
   ```bash
   # Ekspor video profil TikTok ke JSON
   python main.py --platform tiktok --username target_creator --limit 20 --format json

   # Ekspor ke CSV
   python main.py --platform tiktok --username target_creator --limit 50 --format csv
   ```

### 🐦 Cara Pakai X (Twitter) Scraper

1. Simpan sesi / cookie X (Twitter) sekali:
   ```bash
   python main.py --login-twitter
   ```
   *(Jendela browser akan terbuka, silakan login ke akun X Anda untuk menyimpan `auth_token` dan `ct0`)*.

2. Jalankan scraper tweet X:
   ```bash
   # Ekspor tweet profil X ke JSON
   python main.py --platform twitter --username target_handle --limit 20 --format json

   # Ekspor ke CSV
   python main.py --platform twitter --username target_handle --limit 50 --format csv
   ```

## 🖥️ Antarmuka Web Dashboard (Streamlit)

Selain via terminal CLI, Anda dapat menggunakan antarmuka visual berbasis web interaktif:

1. **Jalankan via batch launcher (Windows)**:
   Cukup klik dua kali file `run_ui.bat`.

2. **Atau jalankan via terminal**:
   ```bash
   streamlit run app.py
   ```
   Buka browser di `http://localhost:8501`.

### Fitur Dashboard:
- 🎯 Pemilihan platform interaktif (TikTok, Instagram, X).
- 📊 Filter slider limit konten (3 - 50 konten).
- 📋 Tabel data lengkap dengan fitur search, sort, dan download instan (.csv / .xlsx).
- 📈 Visualisasi grafik bar perbandingan Views vs Likes.
