# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /wheels

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip wheel -r requirements.txt -w /wheels

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY app /app/app
COPY cron /app/cron
COPY app/cronjob /etc/cron.d/totp_cron

RUN chmod 0644 /etc/cron.d/totp_cron && crontab /etc/cron.d/totp_cron

RUN mkdir -p /data /cron /keys \
  && chown root:root /data /cron /keys \
  && chmod 0755 /data /cron /keys

EXPOSE 8080

ENV DATA_DIR=/data
ENV CRON_DIR=/cron
ENV PORT=8080
ENV STUDENT_PRIVKEY_PATH=/keys/student_private.pem
ENV INSTRUCTOR_PUBKEY_PATH=/keys/instructor_public.pem

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
