FROM python:3.15-alpine AS build
# Unpinned so packages follow the base image and pick up security fixes.
# hadolint ignore=DL3018
RUN apk add --no-cache build-base libpq-dev
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.15-alpine
# hadolint ignore=DL3018
RUN apk upgrade --no-cache && apk add --no-cache libpq
WORKDIR /app
COPY --from=build /wheels /wheels
# pip is only needed to install the wheels; dropping it also drops the copies of
# urllib3, msgpack and setuptools it vendors, which scanners flag on their own.
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels \
    && pip uninstall -y pip
COPY . .
ENV PYTHONPATH=/app/src
ENV TZ=UTC
CMD ["python", "-m", "src.main"]
