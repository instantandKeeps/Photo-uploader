
import os, csv
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ik2025")
ALLOWED_EXTS = {"jpg","jpeg","png","gif","webp","heic","heif","pdf"}

def allowed_file(fn): 
    return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED_EXTS

def safename(s):
    return "".join(c for c in s if c.isalnum() or c in (" ","-","_")).strip().replace(" ","_") or "customer"

@app.route("/")
def home():
    return redirect(url_for("upload"))

@app.route("/upload", methods=["GET"])
def upload():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def do_upload():
    name = (request.form.get("name") or "").strip()
    files = request.files.getlist("photos")
    if not name:
        return render_template("index.html", error="Please enter your name.")
    files = [f for f in files if f and getattr(f, "filename", "") and allowed_file(f.filename)]
    if not files or len(files) > 9:
        return render_template("index.html", error="Please select 1–9 supported files.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"{safename(name)}_{stamp}"
    dest = UPLOADS / folder
    dest.mkdir(parents=True, exist_ok=True)

    for f in files:
        fn = os.path.basename(f.filename)
        base, ext = os.path.splitext(fn)
        i, out = 1, fn
        while (dest/out).exists():
            out = f"{base}_{i}{ext}"; i += 1
        f.save(dest / out)

    # log
    log = BASE / "orders.csv"
    new = not log.exists()
    with open(log, "a", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        if new: w.writerow(["timestamp","name","folder","count"])
        w.writerow([stamp, name, folder, len(files)])

    return redirect(url_for("success", name=name, count=len(files)))

@app.route("/success")
def success():
    name = request.args.get("name","")
    count = int(request.args.get("count","0"))
    return render_template("success.html", name=name, count=count)

@app.route("/admin")
def admin():
    key = request.args.get("key","")
    if key != ADMIN_PASSWORD:
        return render_template("admin.html", needs_key=True)
    items = [p for p in UPLOADS.iterdir() if p.is_dir()]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return render_template("admin.html", needs_key=False, files=[p.name for p in items], key=key)

@app.route("/uploads/<path:folder>")
def list_folder(folder):
    key = request.args.get("key","")
    if key != ADMIN_PASSWORD: abort(403)
    root = (UPLOADS / folder).resolve()
    if not root.exists() or not str(root).startswith(str(UPLOADS.resolve())):
        abort(404)
    entries = sorted([p.name for p in root.iterdir() if p.is_file()])
    html = ["<h3>Files in {}</h3><ul>".format(folder)]
    for e in entries:
        html.append('<li><a href="{}">Download {}</a></li>'.format(url_for("download_file", folder=folder, filename=e, key=key), e))
    html.append('</ul><p><a href="{}">Back</a></p>'.format(url_for("admin", key=key)))
    return "\n".join(html)

@app.route("/download/<path:folder>/<path:filename>")
def download_file(folder, filename):
    key = request.args.get("key","")
    if key != ADMIN_PASSWORD: abort(403)
    root = (UPLOADS / folder).resolve()
    if not root.exists() or not str(root).startswith(str(UPLOADS.resolve())):
        abort(404)
    return send_from_directory(root, filename, as_attachment=True)

@app.route("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
