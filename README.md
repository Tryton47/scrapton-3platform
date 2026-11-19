# Scrapton: Multi-Platform Social Media & Comment Scraper

Scraper modular anti-deteksi berbasis Python (Playwright) untuk mengekstrak komentar, profil, video, feed, dan metrik interaksi dari Instagram, TikTok, dan X (Twitter).

## 🚀 Fitur Utama

- **Apify-Style Actor Console**: Antarmuka web developer-first berkecepatan tinggi dengan tab Input Grid, Live Console Logs, dan Storage Dataset Explorer.
- **Multi-Link Comment Extraction**: Ambil komentar dari 1 hingga puluhan link TikTok, Instagram, atau Tweet sekaligus.
- **Sentiment & Spam Heuristics**: Analisis otomatis polaritas sentimen komentar (positif/netral/negatif) serta deteksi pola spam/promosi bot.
- **Unified Schema**: Model data seragam (Pydantic) untuk ketiga platform.
- **Multi-Format Export**: Ekspor otomatis ke CSV, Excel (.xlsx), JSON, dan JSONL.
- **Stealth Browser Architecture**: Dukungan Playwright dengan bypass deteksi bot dan manajemen sesi akun tersimpan.

## 📁 Struktur Direktori

```text
.
├── config/             # Pengaturan terpusat dan env parser
├── core/               # Unified models, storage exporter, browser manager
├── scrapers/           # Engine scraper spesifik tiap platform dan comment scraper
├── utils/              # Text cleaner, sentiment analyzer, dan URL platform detector
├── data/               # Output hasil scraping (JSON/JSONL/CSV/XLSX)
├── sessions/           # Penyimpanan sesi dan cookies akun
├── tests/              # Unit test suite lengkap
├── app.py              # Apify-style Streamlit Actor Console
├── main.py             # CLI entry-point
└── requirements.txt    # Daftar dependensi Python
```

## 🛠️ Instalasi dan Menjalankan

1. Setup environment dan install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Cek status konfigurasi:
   ```bash
   python main.py --status
   ```

---

## 💬 Scraping Komentar via CLI

Anda dapat mengekstrak komentar langsung dari terminal tanpa membuka browser:

```bash
# 1. Scrape komentar dari satu atau beberapa URL
python main.py --comments "https://www.tiktok.com/@tiktok/video/7708408003065580831" --max-comments 30 --format csv

# 2. Scrape komentar dari file daftar URL (satu link per baris)
python main.py --comments-file urls.txt --max-comments 50 --format excel

# 3. Ekspor format JSONL (Newline Delimited JSON)
python main.py --comments "https://x.com/user/status/123456789" --format jsonl
```

---

## 👤 Scraping Profil dan Konten via CLI

```bash
# TikTok
python main.py --platform tiktok --username target_creator --limit 20 --format json

# Instagram
python main.py --platform instagram --username target_user --limit 15 --format csv

# X (Twitter)
python main.py --platform twitter --username target_handle --limit 20 --format json
```

### Simpan Sesi / Cookies Akun (Interaktif)

Untuk mengakses konten yang dibatasi login wall:
```bash
python main.py --login-instagram
python main.py --login-tiktok
python main.py --login-twitter
```

---

## 🖥️ Apify-Style Web Actor Console

Jalankan antarmuka visual berbasis Streamlit:

```bash
streamlit run app.py
```
Atau klik dua kali `run_ui.bat` di Windows. Akses di `http://localhost:8501`.

### Fitur Actor Console:
1. **Tab 1: Input Configuration**: Tabel grid interaktif untuk input URL, auto-detect platform, dan limit komentar.
2. **Tab 2: Execution Console**: Tampilan log terminal real-time dengan status scraping per link.
3. **Tab 3: Storage Dataset**: Filter pencarian teks/username, dropdown filter platform, preview tabel interaktif, dan tombol download instan (CSV, Excel, JSON).

---

## 🧪 Menjalankan Unit Test

Jalankan seluruh rangkaian pengujian otomatis:
```bash
python -m unittest discover tests
```
