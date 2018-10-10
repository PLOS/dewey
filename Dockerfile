# Start from a small image, alpine based images are well maintained, small, and only
# supply what is needed. This keeps our attack surface small and install size down.
FROM python:3.4-alpine

LABEL maintainers="PLOS SREs <it-ops@plos.org>"

# Copy the sources into the container for use.
WORKDIR /code
COPY . /code

# Set some defaults for Deweys expected env vars.
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
    DJANGO_SETTINGS_MODULE="dewey.core.settings.plosdev"

# Here we group together several steps to help keep the image size down. We do this mainly because
# we want to remove the packages we tag with .build-deps, and it needs to be done in the same layer
# as when we install or the net size of the image will not change.
#
# - Get our deps installed and update packages. Flag some of the packages to be removed
#   in a later step as they are only needed during `pip install`.
# - Install our virtualenv and upgrade pip
# - Install plop, it needs to be done separately as it is in a private repo and we'll keep a copy
#   of it in $DEWEY_REPO/tmp/plop on the build machine, and remove it from the container when done
# - Install deweys requirements.txt
# - Install dewey
# - Finally purge the build packages that were required during the install
RUN apk update && apk upgrade &&\
    apk add git postgresql-libs ncurses-libs bash sassc && \
    apk add --virtual .build-deps linux-headers build-base gcc musl-dev postgresql-dev ncurses-dev && \
    python3 -m venv /venvs/dewey && /venvs/dewey/bin/pip install --upgrade pip && \
    /venvs/dewey/bin/pip install git+file:///code/tmp/plop --no-cache-dir && rm -rf /code/tmp && \
    /venvs/dewey/bin/pip install -r requirements/production.txt --no-cache-dir && \
    /venvs/dewey/bin/python setup.py install && \
    apk --purge del .build-deps

# Add dewey user, and chown dirs to dewey, we'll run the service as dewey.
RUN addgroup -g 2029 -S dewey \
    && adduser -u 2029 -G dewey -S dewey && \
    mkdir -p /venvs/dewey && \
    chown -R dewey. /venvs /code

# Tell Docker we want to run this as dewey from here on.
USER dewey:dewey

# Set a pre-defined env var so the startup scripts can locate our virtualenv
ENV VIRTUALENV=/venvs/dewey

# Start dewey via our startup script.
ENTRYPOINT ["/code/bin/dewey-gunicorn-docker.sh"]
