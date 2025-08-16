Instant & Keeps — Local Photo Uploader (No coding required)
===========================================================

What it does
------------
• Works offline on your Windows laptop (saves files to the "uploads" folder).
• Lets customers enter their name, select 1–9 files (JPG, PNG, HEIC/HEIF, WEBP, GIF, PDF).
• No resizing. Saves original files using the pattern:
  YYYY-MM-DD__HH-MM-SS__<customer-name>__<original-filename>

How to run (Windows)
--------------------
1) Double‑click **run_windows.bat** (first run installs Python packages automatically).
2) When you see "Running on http://127.0.0.1:5000", open that link (or it will open automatically).
3) Use the page from your phone by scanning the QR shown in the console (optional).

Stop: close the black window.

Replace the logo
----------------
1) Put your logo image as **static/logo.jpg** (replace the placeholder).
2) Refresh the page in your browser.

Where files go
--------------
• Saved inside the **uploads** folder (inside this project).
• Each event/day will have mixed files sorted by time via the filename prefix.
• Use File Explorer search for today's date (e.g., 2025-08-15) to see all of today's drops.

Admin/Gallery (optional)
------------------------
This local version focuses on saving only. If you later want an on‑page gallery,
it can be added — but this keeps things fast and simple for events.

Support tip
-----------
If something doesn't open, double‑click run_windows.bat again. The first run
may take a minute to install Flask.
