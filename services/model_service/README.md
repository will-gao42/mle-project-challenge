# Model Service

FastAPI service for serving house price predictions.

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python app/main.py
```

The service will be available at http://localhost:8000

### Docker

1. Build the image:
```bash
docker build -t model-service .
```

2. Run the container:
```bash
docker run -p 8000:8000 model-service
```

## API Endpoints

- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions
- `POST /predict-min` - Minimal features prediction
- `POST /reload` - Hot reload model

See `/docs` for interactive API documentation.
