# Сборка из корня lab2: docker build -f services/analytics-service/Dockerfile .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN useradd --create-home --uid 10001 app

# Зависимости — отдельным слоем до кода: при правке кода слой берётся из кэша
COPY services/analytics-service/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY libs/common /tmp/rag-common
RUN pip install --no-deps /tmp/rag-common && rm -rf /tmp/rag-common

COPY services/analytics-service/analytics_service ./analytics_service

USER app
EXPOSE 8007
CMD ["uvicorn", "analytics_service.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8007"]
