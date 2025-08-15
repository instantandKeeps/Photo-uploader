# Render deployment
Build Command:
  pip install -r requirements.txt
Start Command:
  gunicorn app:app
Env:
  ADMIN_PASSWORD = (default 'ik2025')
Health:
  /health
