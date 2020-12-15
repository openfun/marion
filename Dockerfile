# Marion, the learning certificate factory

# -- Base image --
FROM python:3.8-slim as base

# Upgrade pip to its latest release to speed up dependencies installation
RUN python -m pip install --upgrade pip

# ---- Back-end builder image ----
FROM base as builder

WORKDIR /builder

# Copy required python dependencies
COPY ./src/marion /builder

RUN mkdir /install && \
    pip install --prefix=/install .

# ---- Core application image ----
FROM base as core

WORKDIR /app

# Install system dependencies for Django and Weasyprint
RUN apt-get update && \
    apt-get install -y \
      gettext \
      libcairo2 \
      libffi-dev \
      libgdk-pixbuf2.0-0 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies
COPY --from=builder /install /usr/local

# Copy runtime-required files
COPY ./src/marion /app/
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY ./docker/files/usr/local/etc/gunicorn/marion.py /usr/local/etc/gunicorn/marion.py

# Give the "root" group the same permissions as the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# ---- Development image ----
FROM core as development

ENV PYTHONUNBUFFERED=1

# Copy all sources, not only runtime-required files
COPY ./src/marion /app/

# Uninstall marion and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y marion
RUN pip install -e .[dev]

# Copy extra packages
COPY ./src/howard /usr/local/src/howard
RUN cd /usr/local/src/howard && \
      pip install -e .

# Restore the un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Run django development server
CMD python manage.py runserver 0.0.0.0:8000

# ---- Production image ----
FROM core as production

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Run gunicorn WSGI server
CMD gunicorn -c /usr/local/etc/gunicorn/marion.py marion.wsgi:application
