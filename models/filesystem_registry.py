"""Filesystem-based model registry for resolving model keys to directories."""

import os
from pathlib import Path
from typing import Optional


def resolve_model_key(model_key: str, base_dir: str = "/models") -> Path:
    """Resolve a model key to a directory path.
    
    Args:
        model_key: Model identifier (e.g., 'model_A', 'model_B', 'latest')
        base_dir: Base directory containing model artifacts
        
    Returns:
        Path to the model directory
        
    Raises:
        ValueError: If model_key is not recognized
        FileNotFoundError: If the resolved path doesn't exist
    """
    base_path = Path(base_dir)
    
    if model_key == "latest":
        # Find the most recently modified model directory
        model_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("model_")]
        if not model_dirs:
            raise FileNotFoundError(f"No model directories found in {base_path}")
        
        # Sort by modification time, newest first
        latest_dir = max(model_dirs, key=lambda d: d.stat().st_mtime)
        return latest_dir
    
    # Direct model key lookup
    model_path = base_path / model_key
    
    if not model_path.exists():
        available_keys = [d.name for d in base_path.iterdir() if d.is_dir() and d.name.startswith("model_")]
        raise FileNotFoundError(
            f"Model '{model_key}' not found in {base_path}. "
            f"Available models: {available_keys}"
        )
    
    return model_path


def get_available_models(base_dir: str = "/models") -> list[str]:
    """Get list of available model keys.
    
    Args:
        base_dir: Base directory containing model artifacts
        
    Returns:
        List of available model keys
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return []
    
    model_dirs = [d.name for d in base_path.iterdir() if d.is_dir() and d.name.startswith("model_")]
    return sorted(model_dirs)


def validate_model_directory(model_dir: Path) -> bool:
    """Validate that a directory contains required model artifacts.
    
    Args:
        model_dir: Path to model directory
        
    Returns:
        True if directory contains required artifacts
    """
    required_files = ["model.pkl", "model_features.json"]
    
    for file_name in required_files:
        if not (model_dir / file_name).exists():
            return False
    
    return True
