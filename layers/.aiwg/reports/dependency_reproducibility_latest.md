# Dependency Reproducibility Audit Report
**Decision**: `FAIL`  
**Status**: `BROKEN`

## Verification Summary
- **Installed Monitored**: ['kuzu', 'networkx', 'fastapi', 'sentence_transformers', 'torch']
- **Declared Dependencies**: []
- **Undeclared Installed**: ['kuzu', 'networkx', 'fastapi', 'sentence_transformers', 'torch']
- **Missing Declared**: []
- **Heavy Dependencies (>10MB)**: ['kuzu (20.5 MB)', 'networkx (11.2 MB)', 'torch (1098.7 MB)']

## Warnings
- pyproject.toml not found
- Critical dependencies (torch/sentence_transformers) are installed but not declared in pyproject.toml!
