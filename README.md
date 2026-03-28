# Jeejal Backend Starter

This is a FastAPI starter backend for the ultrasound app. It covers:

- user registration and login
- provider and doctor roles
- report creation, doctor assignment, review, and signing
- local file upload for ultrasound images and signatures
- signed PDF export

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Notes

- This starter uses SQLite by default so you can move fast locally.
- For deployment, switch `DATABASE_URL` to Postgres.
- The fetal ultrasound assets are already copied under `vendor/Fetal_Ultrasound-main`.
- `app/services/ai_service.py` now uses the provided `.h5` model automatically when TensorFlow is available.
- For AI inference, use a TensorFlow-supported Python version. TensorFlow's install guide currently lists Windows wheels for Python 3.10-3.13, not 3.14. Source: [TensorFlow pip install guide](https://www.tensorflow.org/install/pip)
- AI-only dependencies are listed in `requirements-ai.txt`.
