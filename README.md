# Quran JSON (Arabic + English)

Arabic Uthmānī script + English translation:
- **AR**: Arabic Uthmani script  
- **EN**: English translation (Sahih International)

Also includes **Juz** and **Madani Page (1–604)** indexes.

Data is generated from Quran.com API v4 at build time and hosted as static files on Vercel.

**Note**: Simple JSON structure with Arabic in `ar` field and English in `en` field.

## Download (examples)

- `/assets/quran/manifest_multi.json` - Metadata
- `/assets/quran/stats.json` - Statistics
- `/assets/quran/chapters.json` - Chapters info (names, verses count, revelation place)
- `/assets/quran/allah_names.json` - 99 Names of Allah
- `/assets/quran/index_juz.json` - Juz index
- `/assets/quran/index_pages.json` - Pages index
- `/assets/quran/s001.json` … `/assets/quran/s114.json` - Surahs

## Features

- 🔍 **Search Page**: `/search.html` - Search in Quran (Arabic & English)
- 📊 **Statistics**: Total verses, longest/shortest surah, and more
- 📖 **Complete Info**: Chapter names, revelation place, verse counts

Example absolute URL:
https://<your-project>.vercel.app/assets/quran/s002.json

## Deploy on Vercel

1. Push this repo to GitHub.
2. In Vercel: **Add New → Project → Import** this repo → Deploy.
3. After build, browse to `/assets/quran/…`.

## Local build

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python generate_quran_bundle_with_indexes.py
# output: assets/quran/*

Notes

CORS is open (*) so you can fetch from mobile/web.

Files are cached long-term (immutable) — redeploy to refresh.
