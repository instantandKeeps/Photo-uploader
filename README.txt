INSTANT & KEEPS — LOCAL UPLOADER (Windows)

What it does
- Lets customers select up to 9 files (JPG, PNG, HEIC/HEIF, WEBP, GIF, PDF)
- Saves them to: uploads/<Name_YYYYMMDD_HHMMSS>/... on your computer
- Shows a success page with the folder name

How to run
1) Double‑click: run_windows.bat
   - This creates a Python sandbox (.venv), installs Flask, then starts the app.

2) Open this link in your browser (or phone on same Wi‑Fi):
   http://localhost:8080

3) After someone uploads, files appear in: uploads\Name_YYYYMMDD_HHMMSS

Notes
- Close the window to stop the server.
- Replace static\logo.jpg with your real logo if you want.
- To change the text or button, edit templates\index.html.
