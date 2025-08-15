
import os, csv, datetime as dt
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = Path(__file__).resolve().parent
UPLOADS = BASE_DIR / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ik2025")
# Include pdf in allowed extensions
ALLOWED_EXTS = {"jpg","jpeg","png","gif","webp","heic","heif","pdf"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

def safe_name(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in (" ","-","_")).strip() or "customer"

@app.route("/")
def home():
    return redirect(url_for("upload_form"))

@app.route("/upload", methods=["GET"])
def upload_form():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def handle_upload():
    name = (request.form.get("name") or "").strip()
    files = request.files.getlist("photos")

    if not name:
        return render_template("index.html", error="Please enter your name.")
    if not files:
        return render_template("index.html", error="Please choose at least one file.")

    # Filter allowed, keep up to 9
    files = [f for f in files if f and f.filename and allowed_file(f.filename)]
    if not files:
        return render_template("index.html", error="File type not supported.")
    files = files[:9]

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"{safe_name(name)}_{stamp}"
    dest = UPLOADS / folder
    dest.mkdir(parents=True, exist_ok=True)

    saved = 0
    for f in files:
        fname = os.path.basename(f.filename)
        orig = fname
        i = 1
        while (dest / fname).exists():
            stem, ext = os.path.splitext(orig)
            fname = f"{stem}_{i}{ext}"
            i += 1
        f.save(dest / fname)  # no resizing/compression; originals saved
        saved += 1

    csv_path = BASE_DIR / "orders.csv"
    new = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        if new:
            w.writerow(["timestamp","name","count","folder"])
        w.writerow([stamp, name, saved, folder])

    return render_template("success.html", name=name, count=saved, folder=folder)

@app.route("/admin", methods=["GET","POST"])
def admin():
    key = request.values.get("key","")
    if key != ADMIN_PASSWORD:
        return render_template("admin.html", needs_key=True)

    if request.method == "POST":
        target = request.form.get("delete","")
        if target:
            root = (UPLOADS / target).resolve()
            if str(root).startswith(str(UPLOADS.resolve())) and root.exists():
                for p in root.rglob("*"):
                    if p.is_file():
                        p.unlink()
                for p in sorted(list(root.rglob("*")), reverse=True):
                    if p.is_dir():
                        try: p.rmdir()
                        except OSError: pass
                try: root.rmdir()
                except OSError: pass

    entries = []
    if UPLOADS.exists():
        for folder in sorted(UPLOADS.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if folder.is_dir():
                files = [f.name for f in sorted(folder.iterdir()) if f.is_file()]
                entries.append({"folder": folder.name, "files": files})
    return render_template("admin.html", needs_key=False, files=entries, key=key)

@app.route("/uploads/<path:filename>")
def get_upload(filename):
    key = request.args.get("key","")
    if key != ADMIN_PASSWORD:
        abort(403)
    full = (UPLOADS / filename).resolve()
    if not str(full).startswith(str(UPLOADS.resolve())) or not full.exists():
        abort(404)
    return send_from_directory(full.parent, full.name, as_attachment=True)

@app.route("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
