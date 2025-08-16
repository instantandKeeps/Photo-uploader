from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photos' not in request.files:
        return "No file part"
    files = request.files.getlist('photos')
    if not files or files[0].filename == '':
        return "No selected files"
    
    folder_name = datetime.now().strftime("%Y-%m-%d_uploads_%H%M%S")
    save_path = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(save_path, exist_ok=True)
    
    for file in files:
        filename = file.filename
        file.save(os.path.join(save_path, filename))
    
    return render_template("success.html", folder=folder_name)

@app.route('/gallery')
def gallery():
    key = request.args.get("key")
    if key != "ik2025":
        return "Unauthorized"
    folders = os.listdir(UPLOAD_FOLDER)
    folders.sort(reverse=True)
    return render_template("admin.html", folders=folders)

@app.route('/download/<path:folder>/<path:filename>')
def download(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
