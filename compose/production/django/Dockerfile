FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        libpq-dev \
        gettext \
        git \
        gosu \
    && rm -rf /var/lib/apt/lists/*

# Create Django user with stable IDs
RUN addgroup --system --gid 102 django \
    && adduser --system --uid 100 --ingroup django django

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy startup scripts
COPY compose/production/django/entrypoint /entrypoint
COPY compose/production/django/start /start
COPY compose/production/django/celery/worker/start /start-celeryworker
COPY compose/production/django/celery/beat/start /start-celerybeat
COPY compose/production/django/celery/flower/start /start-flower

# Normalize line endings and permissions
RUN sed -i 's/\r$//g' \
        /entrypoint \
        /start \
        /start-celeryworker \
        /start-celerybeat \
        /start-flower \
    && chmod +x \
        /entrypoint \
        /start \
        /start-celeryworker \
        /start-celerybeat \
        /start-flower \
    && chown django:django \
        /entrypoint \
        /start \
        /start-celeryworker \
        /start-celerybeat \
        /start-flower

# Application directories
RUN mkdir -p /app/static /app/staticfiles /app/mediafiles \
    && chown -R django:django /app

WORKDIR /app

# Copy application code
COPY . /app
RUN chown -R django:django /app

# The entrypoint must start as root to fix mounted-volume permissions,
# then drop privileges to django before executing the requested command.
ENTRYPOINT ["/entrypoint"]