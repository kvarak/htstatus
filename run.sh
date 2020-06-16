#!/bin/bash -ex

## FLASK_ENV=development turns on debug mode when flask starts
export FLASK_ENV=development

# --------------------------------------------------------------------------------

env LOCAL_RUN=true FLASK_RUN_PORT=5000 FLASK_RUN_HOST=0.0.0.0 FLASK_APP=run.py flask run
