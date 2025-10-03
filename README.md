# MLE Project - House Price Prediction

A production-ready machine learning service for house price prediction, structured following MLOps best practices.

## Quick Start

### Training Models

**Model A (Basic KNN):**
```bash
cd training/model_A
conda env create -f environment.yml
conda activate housing
python src/train.py
```

**Model B (Improved Model):**
```bash
cd training/model_B
conda env create -f environment.yml
conda activate housing
python src/train.py
```

### Running the Service

**Local Development (pyenv + virtualenv):**
```bash
# Install Python 3.9 with pyenv
pyenv install 3.9.18
pyenv local 3.9.18

# Set up virtual environment
cd services/model_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

**Docker (Production/Testing):**
```bash
cd ops
docker-compose up --build
```

The API will be available at http://localhost:8000

### Testing

**Test against Docker service (recommended):**
```bash
# Start Docker service
cd ops
docker-compose up -d

# Run tests as downstream application
export SERVICE_URL=http://localhost:8000
python tests/functional/test_simple_api.py
python tests/functional/test_reload_switch_model.py

# Stop service
docker-compose down
```

**Test against local development service:**
```bash
# Start local service first
cd services/model_service
python app/main.py

# In another terminal, run tests
python tests/functional/test_api.py
```

## Project Structure

```
├── common/                    # Shared utilities
├── training/                  # Model training pipelines
│   ├── model_A/              # Basic KNN model
│   └── model_B/              # Improved model
├── services/                 # Runtime services
│   └── model_service/        # FastAPI prediction service
├── models/                   # Model registry adapters
├── ops/                      # Deployment configs
├── tests/functional/         # Test suites
├── docs/                     # Documentation
└── data/                     # Original data files
```

## Key Features

- **Hot Model Swapping**: Switch between models without service restart
- **Batch Predictions**: Process multiple predictions efficiently
- **Demographics Enrichment**: Automatic zipcode-based feature enrichment
- **Production Ready**: Docker, health checks, monitoring

## Documentation

- [Project Structure](docs/STRUCTURE.md) - Detailed navigation guide
- [Environments](docs/ENVIRONMENTS.md) - Training vs serving setup
- [Hot Swap Guide](docs/HOT_SWAP.md) - Live model switching
- [Original Instructions](instructions.md) - phData project requirements

## API Endpoints

- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions  
- `POST /predict-min` - Minimal features prediction
- `POST /reload` - Hot reload model

Interactive API docs: http://localhost:8000/docs