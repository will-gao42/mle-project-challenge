# Hot Model Swapping Guide

This guide explains how to swap models without restarting the service, enabling zero-downtime model updates.

## Overview

The hot-swap functionality allows you to:
- Switch between Model A and Model B without service restart
- Load new model versions from disk
- Maintain service availability during model updates
- Validate model changes before committing

## How It Works

1. **Model Registry**: The `models/filesystem_registry.py` resolves model keys to directories
2. **Reload Endpoint**: The `/reload` endpoint accepts model keys or direct paths
3. **Atomic Swap**: Models are loaded and validated before replacing the in-memory predictor
4. **Version Tracking**: Each model has a unique version hash for tracking changes

## API Usage

### Switch by Model Key

```bash
# Switch to Model B
curl -X POST http://localhost:8000/reload \
  -H "Content-Type: application/json" \
  -d '{"model_key": "model_B"}'

# Switch back to Model A
curl -X POST http://localhost:8000/reload \
  -H "Content-Type: application/json" \
  -d '{"model_key": "model_A"}'

# Use latest model (most recently modified)
curl -X POST http://localhost:8000/reload \
  -H "Content-Type: application/json" \
  -d '{"model_key": "latest"}'
```

### Switch by Direct Path

```bash
# Switch to specific model directory
curl -X POST http://localhost:8000/reload \
  -H "Content-Type: application/json" \
  -d '{"model_dir": "/models/model_B"}'
```

### Reload Current Model

```bash
# Reload current model (useful after file updates)
curl -X POST http://localhost:8000/reload
```

## Response Format

```json
{
  "status": "success",
  "old_version": "a1b2c3d4e5f6g7h8",
  "new_version": "i9j0k1l2m3n4o5p6",
  "message": "Model switched to model_B"
}
```

## Environment Variables

Configure model resolution via environment variables:

```bash
# Base directory for model artifacts
MODEL_BASE_DIR=/models

# Default model to load on startup
DEFAULT_MODEL_KEY=model_A

# Direct model directory (alternative to MODEL_BASE_DIR)
MODEL_DIR=/path/to/model
```

## Docker Configuration

The docker-compose setup mounts both models for hot-swapping:

```yaml
services:
  house-price-api:
    environment:
      - MODEL_BASE_DIR=/models
      - DEFAULT_MODEL_KEY=model_A
    volumes:
      - ../training/model_A/artifacts:/models/model_A:ro
      - ../training/model_B/artifacts:/models/model_B:ro
```

## Model Directory Structure

Each model directory must contain:
- `model.pkl`: Serialized model object
- `model_features.json`: List of feature names
- `model_info.json`: Model metadata (optional)

```
/models/
├── model_A/
│   ├── model.pkl
│   ├── model_features.json
│   └── model_info.json
└── model_B/
    ├── model.pkl
    ├── model_features.json
    └── model_info.json
```

## Workflow Examples

### Deploying a New Model Version

1. **Train new model**:
   ```bash
   cd training/model_B
   python src/train.py
   ```

2. **Verify artifacts**:
   ```bash
   ls -la training/model_B/artifacts/
   ```

3. **Hot-swap to new model**:
   ```bash
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_B"}'
   ```

4. **Test predictions**:
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"bedrooms": 3, "bathrooms": 2.5, ...}'
   ```

5. **Rollback if needed**:
   ```bash
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_A"}'
   ```

### A/B Testing

1. **Start with Model A**:
   ```bash
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_A"}'
   ```

2. **Collect baseline metrics**

3. **Switch to Model B**:
   ```bash
   curl -X POST http://localhost:8000/reload \
     -H "Content-Type: application/json" \
     -d '{"model_key": "model_B"}'
   ```

4. **Compare performance**

5. **Keep the better model**

## Monitoring and Validation

### Health Check

Monitor service health after model swaps:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "model_version": "i9j0k1l2m3n4o5p6"
}
```

### Version Tracking

Track model versions in your monitoring system:

```bash
# Get current version
VERSION=$(curl -s http://localhost:8000/health | jq -r '.model_version')
echo "Current model version: $VERSION"
```

### Automated Testing

Run tests after model swaps:

```bash
python tests/functional/test_reload_switch_model.py
```

## Error Handling

### Common Issues

1. **Model not found**:
   ```json
   {
     "detail": "Model 'model_C' not found in /models. Available models: ['model_A', 'model_B']"
   }
   ```

2. **Invalid model artifacts**:
   ```json
   {
     "detail": "Model reload failed: Model file not found: /models/model_A/model.pkl"
   }
   ```

3. **Feature mismatch**:
   ```json
   {
     "detail": "Model reload failed: Feature mismatch between model and input"
   }
   ```

### Recovery

If a model swap fails:
1. Check the error message
2. Verify model artifacts exist and are valid
3. Try reloading the previous model
4. Check service logs for detailed error information

## Best Practices

1. **Always test models** before deploying to production
2. **Keep previous model versions** for rollback capability
3. **Monitor prediction quality** after model swaps
4. **Use version tracking** in your monitoring system
5. **Document model changes** and performance metrics
6. **Automate testing** after model deployments

## Security Considerations

- Model files are mounted read-only in Docker
- Validate model artifacts before loading
- Use proper file permissions for model directories
- Consider model signing for production deployments
