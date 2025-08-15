import os, csv, datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

ALLOWED = {"jpg","jpeg","png","gif","heic","heif","webp","pdf"}

def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED

def safe(s: str) -> str:
    s = "".join(c for c in s if c.isalnum() or c in (" ","-","_")).strip()
    return s or "customer"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    name = (request.form.get("name") or "").strip()
    files = request.files.getlist("photos")

    if not name:
        return render_template("index.html", error="Please enter your name.")
    files = [f for f in files if f and f.filename and allowed_file(f.filename)]
    if not files or len(files) > 9:
        return render_template("index.html", error="Please select 1–9 supported files.")

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"{safe(name)}_{stamp}"
    dest = os.path.join(UPLOADS, folder)
    os.makedirs(dest, exist_ok=True)

    saved = 0
    for f in files:
        base = os.path.basename(f.filename)
        stem, ext = os.path.splitext(base)
        stem = (stem[:80] or "file")
        final = stem + ext
        i = 1
        while os.path.exists(os.path.join(dest, final)):
            final = f"{stem}_{i}{ext}"
            i += 1
        f.save(os.path.join(dest, final))
        saved += 1

    log = os.path.join(BASE, "orders.csv")
    new = not os.path.exists(log)
    with open(log, "a", newline="", encoding="utf-8") as fp:
        import csv
        w = csv.writer(fp)
        if new: w.writerow(["timestamp","name","folder","count"])
        w.writerow([stamp, name, folder, saved])

    return redirect(url_for("success", name=name, count=saved, folder=folder))

@app.route("/success")
def success():
    from flask import request
    name = request.args.get("name","")
    count = int(request.args.get("count","0"))
    folder = request.args.get("folder","")
    return render_template("success.html", name=name, count=count, folder=folder)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)