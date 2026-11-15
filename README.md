# Social Media Scraper (Instagram, TikTok, X)

Scraper modular berbasis Python untuk mengekstrak data profil, postingan, dan metrik interaksi (likes, comments, views, shares) dari Instagram, TikTok, dan X (Twitter).

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
