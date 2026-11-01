"""gunicorn settings for the Docker image (see Dockerfile and DEPLOYMENT.md)."""

import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
# /update fetches many CHPP files in one request; the default 30 s kills it.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "180"))
accesslog = "-"
errorlog = "-"
# Path without the query string: OAuth tokens and ids stay out of the logs.
access_log_format = '%(h)s %(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)ss'
