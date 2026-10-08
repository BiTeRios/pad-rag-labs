# Сборка из корня lab2: docker build -f services/inference-service/Dockerfile .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/models
WORKDIR /app
# /models — кэш весов Hugging Face в томе; владелец — app, иначе непривилегированный процесс не запишет
RUN useradd --create-home --uid 10001 app \
    && mkdir /models && chown app /models

# Зависимости — отдельным слоем до кода: при правке кода слой берётся из кэша
COPY services/inference-service/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY libs/common /tmp/rag-common
RUN pip install --no-deps /tmp/rag-common && rm -rf /tmp/rag-common

COPY services/inference-service/inference_service ./inference_service

USER app
EXPOSE 8003
CMD ["uvicorn", "inference_service.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8003"]
