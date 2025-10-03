# Model A Training

This directory contains the training pipeline for Model A (basic KNN model).

## Quick Start

1. Activate the training environment:
```bash
conda env create -f environment.yml
conda activate housing
```

2. Run training:
```bash
python src/train.py
```

3. Artifacts will be saved to `artifacts/` directory.

## Configuration

Edit `configs/params.yaml` to adjust training parameters, data paths, and feature selection.
