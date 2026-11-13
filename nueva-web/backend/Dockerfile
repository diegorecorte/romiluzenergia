FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY nueva-web/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home romiluz && mkdir /data && chown romiluz:romiluz /data
COPY --chown=romiluz:romiluz nueva-web /app/nueva-web
COPY --chown=romiluz:romiluz fotos /app/fotos
USER romiluz
WORKDIR /app/nueva-web/backend
ENV ROMILUZ_PRIVATE_ROOT=/data/romiluz
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "60", "--access-logfile", "/dev/null"]
