# Сборка из корня lab2: docker build -f gateway/Dockerfile .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN useradd --create-home --uid 10001 app

# Зависимости — отдельным слоем до кода: при правке кода слой берётся из кэша
COPY gateway/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY libs/common /tmp/rag-common
RUN pip install --no-deps /tmp/rag-common && rm -rf /tmp/rag-common

COPY gateway/gateway_service ./gateway_service
COPY gateway/routes.yaml ./routes.yaml

USER app
EXPOSE 8000
CMD ["uvicorn", "gateway_service.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
