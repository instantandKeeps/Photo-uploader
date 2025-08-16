import os, re, datetime
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"jpg","jpeg","png","heic","heif","webp","gif","pdf"}

app = Flask(__name__, static_folder="static", template_folder="templates")

def slugify_name(name: str) -> str:
    # Keep letters, numbers, spaces, dashes and underscores; collapse spaces to '_'.
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "", name).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "guest"

def is_allowed(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXT

@app.route("/")
def home():
    return redirect(url_for("upload"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("index.html", error="")
    # POST
    name = (request.form.get("name") or "").strip()
    files = request.files.getlist("photos")
    error = ""

    if not name:
        error = "Please enter your name."
    elif not files or len(files) == 0:
        error = "Please select at least one file."
    elif len(files) > 9:
        error = "Please select no more than 9 files."
    else:
        bad = [f.filename for f in files if not is_allowed(f.filename)]
        if bad:
            error = "These files are not accepted: " + ", ".join(bad)

    if error:
        return render_template("index.html", error=error)

    # Save: prefix each file with timestamp + customer name
    stamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    who = slugify_name(name)
    saved = 0
    for f in files:
        if not f or f.filename == "": 
            continue
        filename = secure_filename(f.filename)
        final_name = f"{stamp}__{who}__{filename}"
        f.save(os.path.join(UPLOAD_DIR, final_name))
        saved += 1

    return render_template("success.html", name=name, count=saved)

if __name__ == "__main__":
    # Run on localhost for Windows event use
    app.run(host="127.0.0.1", port=5000, debug=False)
