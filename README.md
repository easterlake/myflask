# Minimal Python Flask App

A minimal Python Flask application to deploy on [Seenode](https://seenode.com).

## Key Features

- **Single File**: All code is in `app.py`.
- **Dependencies**: `Flask` and `Gunicorn` are specified in `requirements.txt`.
- **Containerized**: A `Dockerfile` is included for easy deployment.

## How to Run

### Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   flask run
   ```
   The app will be at `http://127.0.0.1:5000`.

### With Gunicorn

To run in a production-like environment:
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

### With Docker

1. **Build the Image**:
   ```bash
   docker build -t python-flask-demo .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 8000:8000 python-flask-demo
   ```
   The app will be at `http://localhost:8000`.


See [Guide to deploy Flask app in seconds](https://seenode.com/docs/)