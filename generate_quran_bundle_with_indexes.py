#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
v1.4 — Robust paging + safer translator picking + optional ID pinning.

Outputs under: assets/quran/
  - s001.json … s114.json
  - index_juz.json
  - index_pages.json
  - manifest_multi.json

Env (optional):
  QURAN_T_EN / QURAN_T_ID / QURAN_T_ZH / QURAN_T_JA  -> numeric IDs to pin
  DEBUG_LIST_TRANSLATIONS=1 -> also writes public/translations.json (catalog)
"""

import os, re, json, time, hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import requests

API_BASE = "https://api.quran.com/api/v4"
OUT_DIR  = Path("assets/quran")
BUNDLE_VERSION = "v4-uthmani+translit+EN(SI)+ID(KEMENAG)+ZH(MaJian)+JA(Mita)"
HEADERS = {"Accept": "application/json", "User-Agent": "SunnahCoach/1.4 (+quran.com/api)"}

AYAH_COUNTS = {
  1:7,2:286,3:200,4:176,5:120,6:165,7:206,8:75,9:129,10:109,11:123,12:111,
  13:43,14:52,15:99,16:128,17:111,18:110,19:98,20:135,21:112,22:78,23:118,24:64,
  25:77,26:227,27:93,28:88,29:69,30:60,31:34,32:30,33:73,34:54,35:45,36:83,
  37:182,38:88,39:75,40:85,41:54,42:53,43:89,44:59,45:37,46:35,47:38,48:29,
  49:18,50:45,51:60,52:49,53:62,54:55,55:78,56:96,57:29,58:22,59:24,60:13,
  61:14,62:11,63:11,64:18,65:12,66:12,67:30,68:52,69:52,70:44,71:28,72:28,
  73:20,74:56,75:40,76:31,77:50,78:40,79:46,80:42,81:29,82:19,83:36,84:25,
  85:22,86:17,87:19,88:26,89:30,90:20,91:15,92:21,93:11,94:8,95:8,96:19,97:5,
  98:8,99:8,100:11,101:11,102:8,103:3,104:9,105:5,106:4,107:7,108:3,109:6,110:3,
  111:5,112:4,113:5,114:6
}

DESIRED = {
  "en": ["sahih international", "saheeh international"],
  "id": ["kementerian agama", "kemenag", "bahasa indonesia"],
  "zh": ["ma jian"],
  "ja": ["ryoichi mita", "umar mita", "mita"]
}
LANG_SYNONYMS = {
  "en": ["english"],
  "id": ["indonesian", "bahasa indonesia"],
  "zh": ["chinese", "中文", "简体", "繁體"],
  "ja": ["japanese", "日本語"]
}

# ---------- HTTP with retry ----------
def http_get(path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
  url = path if path.startswith("http") else f"{API_BASE}{path}"
  backoff = 1.0
  last_status, last_text = None, ""
  for _ in range(8):
    try:
      r = requests.get(url, params=params, headers=HEADERS, timeout=40)
      if r.status_code == 200:
        return r.json()
      last_status, last_text = r.status_code, r.text
      # gentle backoff on rate limits or server hiccups
      time.sleep(backoff); backoff = min(backoff * 1.6, 6.0)
    except Exception as e:
      last_status, last_text = "EXC", str(e)
      time.sleep(backoff); backoff = min(backoff * 1.6, 6.0)
  raise RuntimeError(f"GET {url} failed: {last_status} {last_text[:200]}")

# ---------- Catalog ----------
def list_translations() -> List[Dict[str, Any]]:
  data = http_get("/resources/translations")
  return data.get("translations", data.get("resources", []))

def pick_ids() -> Tuple[Dict[str,int], Dict[int,Dict[str,Any]]]:
  trs = list_translations()
  by_id = {int(t["id"]): t for t in trs if "id" in t}

  # optional debug dump
  if os.getenv("DEBUG_LIST_TRANSLATIONS"):
    Path("public").mkdir(parents=True, exist_ok=True)
    slim = [{"id": int(t["id"]),
             "language_name": t.get("language_name"),
             "resource_name": t.get("resource_name") or t.get("name"),
             "name": t.get("name")} for t in trs if "id" in t]
    Path("public/translations.json").write_text(json.dumps(slim, ensure_ascii=False, indent=2), "utf-8")

  # env pin
  choice = {}
  for lang, env_key in [("en","QURAN_T_EN"), ("id","QURAN_T_ID"), ("zh","QURAN_T_ZH"), ("ja","QURAN_T_JA")]:
    v = os.getenv(env_key)
    if v and v.isdigit() and int(v) in by_id:
      choice[lang] = int(v)

  def is_lang(t, lang):
    ln = (t.get("language_name") or "").lower()
    return any(s in ln for s in LANG_SYNONYMS[lang])

  for lang in ["en","id","zh","ja"]:
    if lang in choice:  # already pinned
      continue
    cands = [t for t in trs if is_lang(t, lang)]
    if not cands:
      cands = trs[:]  # last resort
    wanted = [w.lower() for w in DESIRED[lang]]
    def score(t):
      name = (t.get("resource_name") or t.get("name") or "").lower()
      name_rank = min((i for i,w in enumerate(wanted) if w in name), default=99)
      lang_penalty = 0 if is_lang(t, lang) else 50
      return (name_rank + lang_penalty, -int(t.get("id",0)))
    cands.sort(key=score)
    if not cands or score(cands[0])[0] >= 149:
      raise SystemExit(f"Couldn't find translation for {lang} (wanted {DESIRED[lang]})")
    choice[lang] = int(cands[0]["id"])

  return choice, {k: by_id[k] for k in choice.values()}

# ---------- Utilities ----------
def sha256_text(lines: List[str]) -> str:
  return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()

def compress_ranges(pairs: List[Tuple[int,int]]) -> List[Dict[str,int]]:
  out, seen, ordered = [], set(), []
  for s,a in pairs:
    if (s,a) not in seen:
      seen.add((s,a)); ordered.append((s,a))
  i, n = 0, len(ordered)
  while i < n:
    s = ordered[i][0]; a1 = a2 = ordered[i][1]; j = i + 1
    while j < n and ordered[j][0] == s and ordered[j][1] == a2 + 1:
      a2 = ordered[j][1]; j += 1
    out.append({"s": s, "a1": a1, "a2": a2}); i = j
  return out

# ---------- Fetch with robust paging ----------
def fetch_surah(surah: int,
                tr_ids: Dict[str,int],
                by_juz: Dict[int, List[Tuple[int,int]]],
                by_page: Dict[int, List[Tuple[int,int]]]) -> List[Dict[str,Any]]:
  fields = "text_uthmani,verse_key,juz_number,hizb_number,rub_number,page_number,ruku_number"
  tr_str = ",".join(str(tr_ids[k]) for k in ["en","id","zh","ja"])
  tr_fields = "resource_name,language_name,id,resource_id"
  per_page = 50
  out: List[Dict[str,Any]] = []

  page_no = 1
  while True:
    data = http_get(
      f"/verses/by_chapter/{surah}",
      params={
        "page": page_no, "per_page": per_page,
        "fields": fields,
        "translations": tr_str,
        "translation_fields": tr_fields,
        "words": "true",
        "word_fields": "transliteration"
      }
    )
    chunk = data.get("verses", []) or []
    if not chunk:
      break

    for v in chunk:
      vk = v.get("verse_key","")
      try:
        s,a = (int(x) for x in vk.split(":"))
      except Exception:
        s,a = surah, len(out)+1

      # transliteration (join word translits)
      parts = []
      for w in (v.get("words") or []):
        tt = (w.get("transliteration") or {}).get("text")
        if tt: parts.append(tt)
      translit = re.sub(r"\s+", " ", " ".join(parts)).strip() if parts else None

      # translations
      tr_map = {"en":None,"id":None,"zh":None,"ja":None}
      for t in (v.get("translations") or []):
        rid = int(t.get("resource_id") or t.get("id", -1))
        txt = (t.get("text") or "").strip()
        if not txt: continue
        for lang, tid in tr_ids.items():
          if rid == tid: tr_map[lang] = txt

      m = {
        "juz": v.get("juz_number"),
        "hizb": v.get("hizb_number"),
        "rub": v.get("rub_number"),
        "page": v.get("page_number"),
        "ruku": v.get("ruku_number")
      }
      out.append({"s":s,"a":a,"ar":v.get("text_uthmani") or "","tl":translit,"tr":tr_map,"m":m})

      if m["juz"] is not None:  by_juz[int(m["juz"])].append((s,a))
      if m["page"] is not None: by_page[int(m["page"])].append((s,a))

    # continue until we receive a short page
    if len(chunk) < per_page:
      break
    page_no += 1
    time.sleep(0.15)  # be nice to the API

  exp = AYAH_COUNTS[surah]
  if len(out) != exp:
    raise SystemExit(f"[ERROR] Surah {surah} count mismatch: got {len(out)} expected {exp}")
  out.sort(key=lambda x:(x["s"],x["a"]))
  return out

# ---------- Main ----------
def main():
  OUT_DIR.mkdir(parents=True, exist_ok=True)

  tr_ids, tr_meta = pick_ids()
  print("Selected translations:")
  for lang, tid in tr_ids.items():
    m = tr_meta[tid]
    print(f"  {lang}: {(m.get('resource_name') or m.get('name'))} (id={tid})")

  by_juz, by_page = defaultdict(list), defaultdict(list)
  manifest_surahs = []

  for sid in range(1,115):
    print(f"Fetching s{sid:03d} …")
    verses = fetch_surah(sid, tr_ids, by_juz, by_page)
    tmp = OUT_DIR / f"s{sid:03d}.json.tmp"
    tmp.write_text(json.dumps(verses, ensure_ascii=False, separators=(",",":")), "utf-8")
    tmp.replace(OUT_DIR / f"s{sid:03d}.json")
    digest = sha256_text([v["ar"] for v in verses])
    manifest_surahs.append({"id":sid,"ayahCount":AYAH_COUNTS[sid],"hash":digest})

  index_juz   = {str(j): compress_ranges(pairs) for j,pairs in sorted(by_juz.items(), key=lambda x:int(x[0]))}
  index_pages = {str(p): compress_ranges(pairs) for p,pairs in sorted(by_page.items(), key=lambda x:int(x[0]))}

  (OUT_DIR / "index_juz.json").write_text(json.dumps(index_juz, ensure_ascii=False, separators=(",",":")), "utf-8")
  (OUT_DIR / "index_pages.json").write_text(json.dumps(index_pages, ensure_ascii=False, separators=(",",":")), "utf-8")

  manifest = {
    "version": BUNDLE_VERSION,
    "source": "Quran Foundation / Quran.com v4",
    "script": "text_uthmani",
    "hasTransliteration": True,
    "translations": {
      lang: {
        "id": tr_ids[lang],
        "name": tr_meta[tr_ids[lang]].get("resource_name") or tr_meta[tr_ids[lang]].get("name"),
        "language": tr_meta[tr_ids[lang]].get("language_name")
      } for lang in ["en","id","zh","ja"]
    },
    "surahCount": 114,
    "ayahTotal": sum(AYAH_COUNTS.values()),
    "generatedAt": int(time.time()),
    "checks": {"verseCounts": True, "sha256": True}
  }
  (OUT_DIR / "manifest_multi.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")
  print("✅ Done → assets/quran/ (114 surahs + manifest + index_juz.json + index_pages.json)")

if __name__ == "__main__":
  main()
