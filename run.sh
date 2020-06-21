#!/bin/bash -ex

./changelog.sh

## FLASK_ENV=development turns on debug mode when flask starts
if [ "$1" = "5050" ]
then
  export FLASK_ENV=development
fi

# --------------------------------------------------------------------------------

if [ "$1" = "5000" ] || [ "$1" = "5050" ]
then
  env LOCAL_RUN=true FLASK_RUN_PORT=$1 FLASK_RUN_HOST=0.0.0.0 FLASK_APP=run.py flask run
else
  exit
fi
