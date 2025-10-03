# Project Structure Guide

This document provides a detailed guide to navigating the MLE project structure.

> **Note**: This repository has been refactored to follow MLOps best practices with a clean, streamlined structure. All redundant files and directories have been removed.

## Repository Layout

```
mle-project-challenge/
├── README.md                    # Quick start and overview
├── instructions.md              # Original phData requirements
├── docs/                        # Documentation
│   ├── ENVIRONMENTS.md          # Environment setup guide
│   ├── STRUCTURE.md             # This file
│   └── HOT_SWAP.md              # Hot-swap model guide
├── common/                      # Shared utilities
│   └── project_common/
│       ├── demographics.py      # Demographics data loader
│       ├── schemas.py           # API request/response schemas
│       └── __init__.py
├── training/                    # Model training pipelines
│   ├── model_A/                 # Basic KNN model
│   │   ├── src/
│   │   │   └── train.py         # Training script
│   │   ├── configs/
│   │   │   └── params.yaml      # Training configuration
│   │   ├── artifacts/           # Model artifacts (output)
│   │   │   ├── model.pkl
│   │   │   ├── model_features.json
│   │   │   └── model_info.json
│   │   ├── environment.yml      # Conda environment
│   │   └── README.md            # Training instructions
│   └── model_B/                 # Improved model
│       ├── src/
│       │   └── train.py         # Training script
│       ├── configs/
│       │   └── params.yaml      # Training configuration
│       ├── artifacts/           # Model artifacts (output)
│       │   ├── model.pkl
│       │   ├── model_features.json
│       │   └── model_info.json
│       ├── environment.yml      # Conda environment
│       └── README.md            # Training instructions
├── services/                    # Runtime services
│   └── model_service/           # FastAPI prediction service
│       ├── app/
│       │   ├── main.py          # FastAPI application
│       │   ├── model_loader.py  # Model loading utilities
│       │   └── predictor.py     # Prediction logic
│       ├── resources/
│       │   └── zipcode_demographics.csv
│       ├── model/               # Model artifacts (mounted)
│       │   └── .gitkeep
│       ├── requirements.txt     # Serving dependencies
│       ├── Dockerfile           # Service container
│       └── README.md            # Service instructions
├── models/                      # Model registry adapters
│   ├── filesystem_registry.py   # Model key resolution
│   └── __init__.py
├── ops/                         # Deployment configuration
│   ├── docker-compose.yml       # Multi-service orchestration
│   └── nginx.conf               # Load balancer config
├── tests/                       # Test suites
│   └── functional/
│       ├── test_api.py          # API endpoint tests
│       ├── test_batch_api.py    # Batch prediction tests
│       ├── test_reload_api.py   # Model reload tests
│       ├── test_minimal_api.py  # Minimal prediction tests
│       ├── test_all_endpoints.py # Comprehensive API tests
│       └── test_reload_switch_model.py  # Hot-swap tests
└── data/                        # Original data files
    ├── kc_house_data.csv
    ├── zipcode_demographics.csv
    └── future_unseen_examples.csv
```

## Key Directories

### `common/project_common/`
Shared utilities used across training and serving:
- **demographics.py**: Loads and enriches data with zipcode demographics
- **schemas.py**: Pydantic models for API requests/responses

### `training/`
Contains separate training pipelines for different models:
- **model_A/**: Basic KNN model (original implementation)
- **model_B/**: Improved model with multiple algorithms

Each training directory follows the same structure:
- `src/train.py`: Main training script
- `configs/params.yaml`: Configuration file
- `artifacts/`: Output directory for model artifacts
- `environment.yml`: Conda environment specification

### `services/model_service/`
FastAPI service for serving predictions:
- `app/`: Application code
- `resources/`: Static resources (demographics CSV)
- `model/`: Mount point for model artifacts
- `requirements.txt`: Runtime dependencies
- `Dockerfile`: Container specification

### `models/`
Model registry and management:
- **filesystem_registry.py**: Resolves model keys to directories

### `ops/`
Deployment and operations:
- **docker-compose.yml**: Multi-service orchestration
- **nginx.conf**: Load balancer configuration

### `tests/`
Test suites organized by type:
- **functional/**: API and integration tests

## File Naming Conventions

### Training Artifacts
- `model.pkl`: Serialized model object
- `model_features.json`: List of feature names
- `model_info.json`: Model metadata and performance metrics

### Configuration Files
- `params.yaml`: Training parameters and paths
- `environment.yml`: Conda environment specification
- `requirements.txt`: Pip dependencies

### Documentation
- `README.md`: Quick start and usage instructions
- `*.md`: Detailed documentation files

## Data Flow

1. **Training**: `training/model_*/src/train.py` → `training/model_*/artifacts/`
2. **Serving**: `training/model_*/artifacts/` → `services/model_service/model/` (mounted)
3. **API**: `services/model_service/app/` → FastAPI endpoints
4. **Hot-swap**: `/reload` endpoint → `models/filesystem_registry.py` → new model

## Development Workflow

1. **Train Model**: Run training script in `training/model_*/`
2. **Test Locally**: Start service in `services/model_service/`
3. **Deploy**: Use `ops/docker-compose.yml`
4. **Test**: Run tests in `tests/functional/`
5. **Hot-swap**: Use `/reload` endpoint to switch models

## Common Tasks

### Adding a New Model
1. Create `training/model_C/` directory
2. Copy structure from existing model
3. Update `models/filesystem_registry.py` if needed
4. Add to docker-compose volumes

### Modifying API
1. Edit `services/model_service/app/main.py`
2. Update schemas in `common/project_common/schemas.py`
3. Add tests in `tests/functional/`

### Changing Configuration
1. Edit `training/model_*/configs/params.yaml`
2. Update `ops/docker-compose.yml` environment variables
3. Restart services if needed

## Repository Cleanup

The repository has been streamlined by removing:

### Removed Directories
- `app/` - Moved to `services/model_service/app/`
- `scripts/` - Moved to `tests/functional/`
- `model/`, `model_backup/`, `model_improved/` - Moved to `training/*/artifacts/`
- `reports/` - Removed old reports
- `experiments/` - Removed empty placeholder
- `tests/data/` - Removed duplicate test data

### Removed Files
- `conda_environment.yml` - Moved to training directories
- `create_model.py` - Refactored into training scripts
- `requirements.txt` - Moved to service directory
- `test_data.json` - Redundant test data
- Various documentation files - Consolidated into `docs/`

### Result
- **Clean structure**: No duplicate files or directories
- **Clear separation**: Training, serving, and deployment concerns separated
- **Production ready**: Streamlined for deployment and maintenance
- **Easy navigation**: Logical directory structure following MLOps patterns
