# Quran JSON (Arabic + English)

Arabic Uthmānī script + English translation:
- **AR**: Arabic Uthmani script  
- **EN**: English translation (Sahih International)

Also includes **Juz** and **Madani Page (1–604)** indexes.

Data is generated from Quran.com API v4 at build time and hosted as static files.

**Note**: Simple JSON structure with Arabic in `ar` field and English in `en` field.

## Download (examples)

- `/assets/quran/manifest_multi.json` - Metadata
- `/assets/quran/stats.json` - Statistics
- `/assets/quran/chapters.json` - Chapters info (names, verses count, revelation place)
- `/assets/quran/reciters.json` - List of Quran reciters
- `/assets/quran/allah_names.json` - 99 Names of Allah
- `/assets/quran/index_juz.json` - Juz index
- `/assets/quran/index_pages.json` - Pages index
- `/assets/quran/s001.json` … `/assets/quran/s114.json` - Surahs

## Features

- 📖 **Quran Reader**: Read and listen to Quran with audio recitations
- 🎧 **Audio Recitations**: Multiple famous reciters available
- 📊 **Statistics**: Total verses, longest/shortest surah, and more
- 📖 **Complete Info**: Chapter names, revelation place, verse counts

Example absolute URL:
https://quran.wpdynamo.com/assets/quran/s002.json

## Deployment

Built with Astro and deployed on Cloudflare Pages.

## Local build

```bash
bash build.sh
# output: dist/*
```

## Notes

- CORS is open (*) so you can fetch from mobile/web.
- Files are cached long-term (immutable) — redeploy to refresh.
