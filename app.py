# app.py
import os, re, csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort

# ---------- Basic setup ----------
app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTS = {"jpg", "jpeg", "png", "heic", "heif", "webp", "gif", "pdf"}

def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTS

def safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "user"

# ---------- Routes ----------
@app.route("/")
def root():
    # always show the form at /
    return redirect(url_for("upload_form"))

@app.route("/upload", methods=["GET", "POST"])
def upload_form():
    if request.method == "GET":
        # show the form
        return render_template("index.html", error=None)

    # POST: handle the submission
    name = (request.form.get("name") or "").strip()
    files = request.files.getlist("photos")

    # simple validation (1–9 files, non-empty name, allowed types)
    error = None
    if not name:
        error = "Please enter your name."
    elif not files or len(files) == 0:
        error = "Please select at least one file."
    elif len(files) > 9:
        error = "Please select no more than 9 files."
    elif any(not allowed_file(f.filename) for f in files):
        error = "One or more files are not in an accepted format."

    if error:
        return render_template("index.html", error=error)

    # folder: uploads/YYYY-MM-DD_name
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(UPLOAD_FOLDER, f"{today}_{safe_slug(name)}")
    os.makedirs(folder, exist_ok=True)

    saved = 0
    timestamp = datetime.now().strftime("%H%M%S")
    for i, f in enumerate(files, start=1):
        if not f or not f.filename:
            continue
        ext = f.filename.rsplit(".", 1)[-1].lower()
        filename = f"{timestamp}_{i:02d}.{ext}"
        f.save(os.path.join(folder, filename))
        saved += 1

    # log to CSV (optional)
    with open(os.path.join(UPLOAD_FOLDER, "orders.csv"), "a", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), name, saved, folder])

    return redirect(url_for("success", count=saved))

@app.route("/success")
def success():
    # success.html uses {{ count }}
    try:
        count = int(request.args.get("count", "0"))
    except ValueError:
        count = 0
    return render_template("success.html", count=count)

# ---------- Run locally ----------
if __name__ == "__main__":
    # For local testing only
    app.run(host="0.0.0.0", port=8080, debug=True)