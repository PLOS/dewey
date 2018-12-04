# Start from a small image, alpine based images are well maintained, small, and only
# supply what is needed. This keeps our attack surface small and install size down.
#
# We also are using a multi stage build to create the venv, and then move it to the
# final image.
FROM python:3.4-alpine as builder
LABEL maintainers="PLOS SREs <it-ops@plos.org>"

# Copy the sources into the container for use.
WORKDIR /code
COPY . /code

# Install system dependencies.
RUN apk update && apk upgrade && \
    apk add git postgresql-libs ncurses-libs bash sassc linux-headers build-base gcc musl-dev postgresql-dev ncurses-dev

# Install virtualenv and python dependencies.
# Here we mount in plop as well to get around it being in a private repo.
RUN python3 -m venv /venvs/dewey && /venvs/dewey/bin/pip install --upgrade pip && \
    /venvs/dewey/bin/pip install git+file:///code/tmp/plop --no-cache-dir && rm -rf /code/tmp && \
    /venvs/dewey/bin/pip install -r requirements/production.txt --no-cache-dir && \
    /venvs/dewey/bin/python setup.py install

# This will be our deployment artifact. Keeping the separate steps lets us keep the image size
# down cleanly and avoid needing to uninstall build dependencies.
FROM python:3.4-alpine as app
LABEL maintainers="PLOS SREs <it-ops@plos.org>"

# Install our runtime dependencies
RUN apk update && apk add --no-cache postgresql-libs ncurses-libs bash sassc

RUN addgroup -g 2029 -S dewey \
    && adduser -u 2029 -G dewey -S dewey

# Tell Docker we want to run this as dewey from here on.
USER dewey:dewey

# Copy over the virtual env and the code from the builder
COPY --from=builder --chown=dewey:dewey /venvs /venvs
COPY --from=builder --chown=dewey:dewey /code /code
WORKDIR /code

# Set some defaults for Deweys expected env vars. These can be overridden during launch or in the
# docker-compose files.
ENV DEWEY_SECRET_KEY=someSpecialSecret121345 \
    DEWEY_POSTGRES_HOST=localhost \
    DEWEY_POSTGRES_PORT=5432 \
    DEWEY_POSTGRES_USER=dewey \
    DEWEY_POSTGRES_PASSWORD=PGPasswd \
    DEWEY_JIRA_USER=dewey \
    DEWEY_JIRA_PASSWORD=JiraPasswd \
    PDNS_API_URL=localhost \
    PDNS_API_KEY=PDNSApiKey \
    DEWEY_VAULT_PASSWORD=DeweyVaultPasswd \
    DEWEY_CELERY_BROKER_URL="redis://redis:6379/0" \
    DJANGO_SETTINGS_MODULE="dewey.core.settings.docker-dev"

# Set a pre-defined env var so the startup scripts can locate our virtualenv
ENV VIRTUALENV=/venvs/dewey
RUN . /venvs/dewey/bin/activate && dewey-manager collectstatic --no-input

# Start dewey via our startup script.
ENTRYPOINT ["/code/bin/dewey-gunicorn-docker.sh"]
