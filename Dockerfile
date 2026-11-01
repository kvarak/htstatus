# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Lint and tests; run with `make docker-check` (needs the compose postgres).
# Tool versions pinned to the local dev environment so formatting matches.
FROM base AS test

COPY requirements.txt pyproject.toml ./
RUN pip install -r requirements.txt \
    && pip install pytest==9.0.3 pytest-cov==7.1.0 pytest-flask==1.3.0 pytest-mock==3.15.1 \
       ruff==0.15.16 black==26.5.1 djlint==1.39.0

COPY . .
RUN cp config.py.example config.py

CMD ["sh", "-c", "ruff check app tests && black --check app tests models.py && djlint app/templates --check && pytest -q"]

FROM base AS runtime

RUN useradd --system --uid 10001 --create-home app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
# The code is read-only for the app user, whatever the modes were in the checkout.
# Of scripts/ only the migration runner and the error viewer are needed here.
RUN cp config.py.example config.py \
    && rm -rf tests RELEASES.md RELEASES-INTERNAL.md pyproject.toml \
    && find scripts -type f ! -name apply_migrations.py ! -name check_errors.py -delete \
    && find scripts -type d -empty -delete \
    && chmod -R a+rX,go-w .

# Data fetched at Update (transfer bids, series, Hattrick terms) lives here;
# mount a volume so it survives new images.
RUN mkdir -p instance && chown app:app instance

# .git is not in the image: CI passes `git describe --tags` (shown in the footer).
ARG APP_VERSION=""
ENV APP_VERSION=${APP_VERSION} \
    FLASK_ENV=production \
    DEBUG_LEVEL=0

USER app
EXPOSE 8000

ENTRYPOINT ["sh", "docker/entrypoint.sh"]
CMD ["gunicorn", "app.factory:create_app()", "--config", "gunicorn.conf.py"]
