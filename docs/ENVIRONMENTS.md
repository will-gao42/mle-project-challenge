# Environment Setup Guide

This document describes how to set up the different environments for training and serving models.

## Training Environment (Conda)

The training environment uses Conda for dependency management and includes all ML libraries.

### Setup

1. **Navigate to training directory:**
   ```bash
   cd training/model_A  # or training/model_B
   ```

2. **Create and activate environment:**
   ```bash
   conda env create -f environment.yml
   conda activate housing
   ```

3. **Run training:**
   ```bash
   python src/train.py
   ```

### Environment Contents

The training environment includes:
- Python 3.9
- scikit-learn (for ML algorithms)
- pandas (for data manipulation)
- numpy (for numerical operations)
- pyyaml (for configuration)
- matplotlib/seaborn (for visualization)

## Development Environment (pyenv + virtualenv)

For local development, we recommend using pyenv with virtualenv for Python version management.

### Setup

1. **Install pyenv (if not already installed):**
   ```bash
   # macOS
   brew install pyenv
   
   # Linux
   curl https://pyenv.run | bash
   ```

2. **Install Python 3.9:**
   ```bash
   pyenv install 3.9.18
   pyenv local 3.9.18
   ```

3. **Navigate to service directory:**
   ```bash
   cd services/model_service
   ```

4. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the service:**
   ```bash
   python app/main.py
   ```

## Serving Environment (Docker)

The serving environment uses Docker for production deployment and testing.

### Setup

1. **Navigate to ops directory:**
   ```bash
   cd ops
   ```

2. **Build and run the service:**
   ```bash
   docker-compose up --build
   ```

3. **Test the service:**
   ```bash
   curl http://localhost:8000/health
   ```

### Environment Contents

The serving environment includes:
- FastAPI (web framework)
- uvicorn (ASGI server)
- pydantic (data validation)
- pandas (data processing)
- scikit-learn (model inference)
- gunicorn (production WSGI server)
- pyyaml (configuration)

## Environment Variables

### Training
- No special environment variables required
- Configuration via `configs/params.yaml`

### Serving
- `MODEL_BASE_DIR`: Base directory for model artifacts (default: `/models`)
- `DEFAULT_MODEL_KEY`: Default model to load (default: `model_A`)
- `MODEL_DIR`: Direct model directory path (alternative to MODEL_BASE_DIR)

## Docker Environment

The Docker environment combines both training artifacts and serving runtime:

```bash
# Build and run with docker-compose
cd ops
docker-compose up --build
```

This mounts both model artifacts and runs the service with hot-swap capability.

## Testing Against Docker Service

### Running Tests as Downstream Application

Tests should run in a separate environment as if they were a downstream application consuming the API service.

1. **Start the Docker service:**
   ```bash
   cd ops
   docker-compose up -d
   ```

2. **Run tests from project root:**
   ```bash
   # Set service URL for testing
   export SERVICE_URL=http://localhost:8000
   
   # Run individual tests
   python tests/functional/test_api.py
   python tests/functional/test_reload_switch_model.py
   
   # Run all tests
   python tests/functional/test_all_endpoints.py
   ```

3. **Test hot-swap functionality:**
   ```bash
   # Switch to Model B
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_B"}'
   
   # Switch back to Model A
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_A"}'
   ```

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

## Switching Between Environments

### From Training to Serving
1. Train your model: `cd training/model_A && python src/train.py`
2. Start the service: `cd services/model_service && python app/main.py`
3. The service will automatically load the latest model artifacts

### From Development to Docker Testing
1. Develop locally with pyenv: `cd services/model_service && python app/main.py`
2. Test against Docker: `cd ops && docker-compose up -d && python tests/functional/test_api.py`
3. The tests run as a downstream application consuming the Docker-hosted API

## Troubleshooting

### Training Issues
- Ensure you're in the correct conda environment: `conda activate housing`
- Check that data files exist in the configured paths
- Verify YAML configuration syntax

### Serving Issues
- Check that model artifacts exist in the expected locations
- Verify environment variables are set correctly
- Ensure the service can access the demographics CSV file

### Docker Issues
- Ensure docker-compose is run from the `ops/` directory
- Check that model artifacts are properly mounted
- Verify the service health check endpoint responds
