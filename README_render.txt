# Render deployment quick notes
Build Command:
  pip install -r requirements.txt

Start Command:
  gunicorn app:app

Env Vars:
  ADMIN_PASSWORD = (set your secret, default is ik2025)

Health:
  /health -> {"ok": true}
