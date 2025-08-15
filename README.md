# Instant & Keeps — Photo Uploader

- Mobile‑friendly multi‑upload (up to 9 files)
- Accepted: JPG, PNG, HEIC/HEIF, WEBP, GIF, PDF
- No image resizing (originals saved)
- Admin page to download/delete (password via `ADMIN_PASSWORD`, default `ik2025`)

## Run locally
```
pip install -r requirements.txt
python app.py
```
Open http://localhost:8080/upload

## Render deploy
Create a new Web Service from this repo/zip.
- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Add Environment Variable: `ADMIN_PASSWORD` (set your value)
