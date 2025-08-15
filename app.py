import os, csv, datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

# ---------- Basic setup ----------
app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ik2025")

# allow images + pdf
ALLOWED_EXTS = {"jpg","jpeg","png","gif","heic","heif","webp","pdf"}

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_EXTS

# CSV log
ORDERS_CSV = os.path.join(app.root_path, "orders.csv")
if not os.path.exists(ORDERS_CSV):
    with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "name", "filenames"])

# ---------- Routes ----------
@app.route("/")
def root():
    return redirect(url_for("upload"))

@app.route("/upload", methods=["GET","POST"])
def upload():
    error = None
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        files = request.files.getlist("photos")

        # validations
        if not name:
            error = "Please enter your name."
        elif not files or len(files) == 0:
            error = "Please select at least one file."
        elif len(files) > 9:
            error = "Please select no more than 9 files."
        else:
            clean = []
            for f in files:
                if f and allowed_file(f.filename):
                    clean.append(f)
            if not clean:
                error = "Only JPG, PNG, HEIC/HEIF, WEBP, GIF, or PDF are accepted."
            else:
                # make per-order folder
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = "".join(c for c in name if c.isalnum() or c in (" ","-","_")).strip().replace(" ", "_")
                order_folder = os.path.join(UPLOAD_FOLDER, f"{stamp}_{safe_name}")
                os.makedirs(order_folder, exist_ok=True)

                saved_names = []
                for f in clean:
                    filename = f.filename
                    # prevent collisions
                    base, ext = os.path.splitext(filename)
                    base = base[:80] or "file"
                    final = base + ext
                    i = 1
                    while os.path.exists(os.path.join(order_folder, final)):
                        final = f"{base}_{i}{ext}"
                        i += 1
                    f.save(os.path.join(order_folder, final))
                    saved_names.append(final)

                # log
                with open(ORDERS_CSV, "a", newline="", encoding="utf-8") as fcsv:
                    w = csv.writer(fcsv)
                    w.writerow([stamp, name, ";".join(saved_names)])

                return redirect(url_for("success", count=len(saved_names)))

    return render_template("index.html", error=error)

@app.route("/success")
def success():
    try:
        count = int(request.args.get("count", "0"))
    except:
        count = 0
    return render_template("success.html", count=count)

# ---- Admin: simple listing + download/delete (password via query or sessionless) ----
@app.route("/admin", methods=["GET","POST"])
def admin():
    key = request.args.get("key") or (request.form.get("key") if request.method=="POST" else "")
    needs_key = (key != ADMIN_PASSWORD)
    if needs_key:
        return render_template("admin.html", needs_key=True)

    # handle delete request
    del_target = request.form.get("delete")
    if del_target:
        target_path = os.path.join(UPLOAD_FOLDER, del_target)
        if os.path.exists(target_path) and os.path.isdir(target_path):
            try:
                # remove directory tree
                import shutil
                shutil.rmtree(target_path)
            except Exception as e:
                pass

    # list folders newest first
    try:
        items = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    except FileNotFoundError:
        items = []

    return render_template("admin.html", needs_key=False, files=items)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    # Only for admin downloads with key
    key = request.args.get("key")
    if key != ADMIN_PASSWORD:
        abort(403)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    # Render/Heroku style: respect PORT env
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
