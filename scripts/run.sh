#!/bin/bash -ex

./scripts/changelog.sh

## FLASK_ENV=development turns on debug mode when flask starts
export FLASK_ENV=development

# --------------------------------------------------------------------------------

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Use uv to run flask with correct environment
env LOCAL_RUN=true FLASK_RUN_PORT=5000 FLASK_RUN_HOST=0.0.0.0 FLASK_APP=run.py uv run flask run
